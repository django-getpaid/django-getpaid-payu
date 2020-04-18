""""
Settings:
    pos_id
    second_key
    client_id
    client_secret
"""
import hashlib
import json
import logging
from collections import OrderedDict
from urllib.parse import urljoin

import pendulum
import requests
from django import http
from django.db.transaction import atomic
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.http import urlencode
from django.utils.timezone import now
from django_fsm import can_proceed
from getpaid.exceptions import LockFailure
from getpaid.post_forms import PaymentHiddenInputsPostForm
from getpaid.processor import BaseProcessor

logger = logging.getLogger(__name__)


class PaymentProcessor(BaseProcessor):
    slug = "payu"
    display_name = "PayU"
    accepted_currencies = [
        "BGN",
        "CHF",
        "CZK",
        "DKK",
        "EUR",
        "GBP",
        "HRK",
        "HUF",
        "NOK",
        "PLN",
        "RON",
        "RUB",
        "SEK",
        "UAH",
        "USD",
    ]
    ok_statuses = [200, 201, 302]
    method = "REST"  #: Supported modes: REST, POST (not recommended!)
    sandbox_url = "https://secure.snd.payu.com/api/v2_1/"
    production_url = "https://secure.payu.com/api/v2_1/"
    confirmation_method = "PUSH"  #: PUSH - paywall will send POST request to your server; PULL - you need to check the payment status
    post_form_class = PaymentHiddenInputsPostForm
    post_template_name = "getpaid_payu/payment_post_form.html"
    _token = None
    _token_expires = None

    # Specifics

    def prepare_form_data(self, post_data):
        pos_id = self.get_setting("pos_id")
        second_key = self.get_setting("second_key")
        algorithm = self.get_setting("algorithm", "SHA-256").upper()
        hasher = getattr(hashlib, algorithm.replace("-", "").lower())
        encoded = urlencode(OrderedDict(sorted(post_data.items())))
        prepared = f"{encoded}&{second_key}".encode("ascii")
        signature = hasher(prepared).hexdigest()
        post_data[
            "OpenPayu-Signature"
        ] = f"signature={signature};algorithm={algorithm};sender={pos_id}"
        return post_data

    # Helper methods

    def get_oauth_token(self):
        dt = pendulum.instance(now())
        if self._token is None or self._token_expires <= dt.add(seconds=-20):
            base_url = self.get_paywall_baseurl()
            url = urljoin(base_url, "/pl/standard/user/oauth/authorize")
            data = {
                "grant_type": "client_credentials",
                "client_id": self.get_setting("client_id"),
                "client_secret": self.get_setting("client_secret"),
            }
            response = requests.post(url, data=urlencode(data))
            resp_data = response.json()
            token_type = resp_data.get("token_type", "bearer").capitalize()
            token = resp_data.get("access_token")
            self._token = f"{token_type} {token}"
            self._token_expires = dt.add(seconds=resp_data.get("expires_in"))
        return self._token

    def prepare_paywall_headers(self):
        return {"Authorization": self.get_oauth_token()}

    def get_paywall_context(self, request=None, **kwargs):
        # TODO: configurable buyer info inclusion
        """
        "buyer" is optional
        :param request: request creating the payment
        :return: dict with params accepted by paywall
        """
        loc = "127.0.0.1"
        our_baseurl = self.get_our_baseurl(request)
        key_trans = {
            "unit_price": "unitPrice",
            "first_name": "firstName",
            "last_name": "lastName",
        }
        raw_products = self.payment.get_items()
        for product in raw_products.values():
            if "unit_price" in product:
                product["unit_price"] *= 100

        products = {key_trans.get(k, k): v for k, v in raw_products.items()}
        context = {
            "extOrderId": self.payment.get_unique_id(),
            "customerIp": loc if not request else request.META.get("REMOTE_ADDR", loc),
            "merchantPosId": self.get_setting("pos_id"),
            "description": self.payment.description,
            "currencyCode": self.payment.currency,
            "totalAmount": self.payment.amount_required * 100,
            "products": products,
        }
        if self.get_setting("confirmation_method", self.confirmation_method) == "PUSH":
            context["notifyUrl"] = urljoin(
                our_baseurl, reverse("getpaid:callback", kwargs={"pk": self.payment.pk})
            )
        return context

    def get_paywall_method(self):
        return self.get_setting("paywall_method", self.method)

    # Communication with paywall

    @atomic()
    def prepare_transaction(self, request=None, view=None, **kwargs):
        method = self.get_paywall_method().upper()
        if method == "REST":
            try:
                results = self.prepare_lock(request=request, **kwargs)
                response = http.HttpResponseRedirect(results["url"])
            except LockFailure as exc:
                logger.error(exc, extra=getattr(exc, "context", None))
                self.payment.fail()
                response = http.HttpResponseRedirect(
                    reverse("getpaid:payment-failure", kwargs={"pk": self.payment.pk})
                )
            self.payment.save()
            return response
        elif method == "POST":
            data = self.get_paywall_context(request=request, **kwargs)
            url = self.get_main_url()
            form = self.get_form(data)
            return TemplateResponse(
                request=request,
                template=self.get_template_names(view=view),
                context={"form": form, "paywall_url": url},
            )

    def handle_paywall_callback(self, request, **kwargs):
        payu_header_raw = request.headers.get(
            "OpenPayU-Signature"
        ) or request.headers.get("X-OpenPayU-Signature", "")
        payu_header = {
            k: v for k, v in [i.split("=") for i in payu_header_raw.split(";")]
        }
        algo_name = payu_header.get("algorithm", "MD5")
        signature = payu_header.get("signature")
        second_key = self.get_setting("second_key")
        algorithm = getattr(hashlib, algo_name.replace("-", "").lower())

        expected_signature = algorithm(
            f"{request.body}{second_key}".encode("utf-8")
        ).hexdigest()

        if expected_signature == signature:
            data = json.loads(request.body)

            if "order" in data:
                order_data = data.get("order")
                status = order_data.get("status")
                if status == "COMPLETED":
                    if can_proceed(self.payment.confirm_payment):
                        self.payment.confirm_payment()
                    else:
                        logger.debug(
                            "Cannot confirm payment",
                            extra={
                                "payment_id": self.payment.id,
                                "payment_status": self.payment.status,
                            },
                        )
                elif status == "CANCELED":
                    self.payment.fail()
                elif status == "WAITING_FOR_CONFIRMATION":
                    if can_proceed(self.payment.confirm_lock):
                        self.payment.confirm_lock()
                    else:
                        logger.debug(
                            "Already locked",
                            extra={
                                "payment_id": self.payment.id,
                                "payment_status": self.payment.status,
                            },
                        )
            elif "refund" in data:
                refund_data = data.get("refund")
                status = refund_data.get("status")
                if status == "FINALIZED":
                    amount = refund_data.get("amount") / 100
                    self.payment.confirm_refund(amount)
                    if can_proceed(self.payment.mark_as_refunded):
                        self.payment.mark_as_refunded()
                elif status == "CANCELED":
                    self.payment.cancel_refund()
                    if can_proceed(self.payment.mark_as_paid):
                        self.payment.mark_as_paid()
            self.payment.save()
        else:
            logger.error(
                f"Received bad signature for payment {self.payment.id}! "
                f"Got '{signature}', expected '{expected_signature}'"
            )

    def fetch_payment_status(self):
        base_url = self.get_paywall_baseurl()
        url = urljoin(base_url, f"orders/{self.payment.external_id}")
        headers = self.prepare_paywall_headers()
        response = requests.get(url, headers=headers)
        results = {"raw_response": response}
        if response.status_code == 200:
            data = response.json()
            status = data.get("status", {}).get("statusCode")
            if status == "SUCCESS":
                results["callback"] = "confirm_payment"
            elif status == "WAITING_FOR_CONFIRMATION":
                results["callback"] = "confirm_lock"
            elif status == "PENDING":
                results["callback"] = "confirm_prepared"
        return results

    def get_main_url(self, data=None):
        baseurl = self.get_paywall_baseurl()
        return urljoin(baseurl, "orders")

    def prepare_lock(self, request=None, **kwargs):
        results = {}
        api_url = self.get_main_url()
        headers = self.prepare_paywall_headers()
        context = self.get_paywall_context(request=request, **kwargs)
        response = results["raw_response"] = requests.post(
            api_url, data=context, headers=headers
        )
        if response.status_code in self.ok_statuses:
            resp_data = response.json()
            results["url"] = resp_data.get("redirectUri")
            self.payment.confirm_prepared()
            self.payment.external_id = results["ext_order_id"] = resp_data.get(
                "orderId", ""
            )
        else:
            raise LockFailure(
                "Unable to prepare payment pre-auth.",
                context={
                    "api_url": api_url,
                    "headers": headers,
                    "context": context,
                    "response": response,
                },
            )
        return results

    def charge(self, **kwargs):
        url = urljoin(self.get_main_url(), f"{self.payment.external_id}/status")
        headers = self.prepare_paywall_headers()
        data = {"orderId": self.payment.external_id, "orderStatus": "COMPLETED"}
        response = requests.put(url, headers=headers, json=data)
        result = {"raw_response": response}
        if response.status_code == 200:
            data = response.json()
            result["status_desc"] = data.get("status", {}).get("statusDesc")
            if data.get("status", {}).get("statusCode") == "SUCCESS":
                result["success"] = True
        return result

    def release_lock(self):
        base_url = self.get_paywall_baseurl()
        payu_id = self.payment.external_id
        url = urljoin(base_url, f"orders/{payu_id}")
        headers = self.prepare_paywall_headers()
        response = requests.delete(url, headers=headers)
        status = response.json().get("status", {}).get("statusCode")
        if status == "SUCCESS":
            return self.payment.amount_locked

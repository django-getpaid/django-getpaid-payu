import uuid
from decimal import Decimal

import pytest
import swapper
from django.urls import reverse_lazy

from getpaid_payu.types import Currency

pytestmark = pytest.mark.django_db

Order = swapper.load_model("getpaid", "Order")
Payment = swapper.load_model("getpaid", "Payment")

url_post_payment = "https://secure.snd.payu.com/api/v2_1/orders"
url_api_register = "https://secure.snd.payu.com/api/v2_1/orders"
url_api_operate = reverse_lazy("paywall:api_operate")


@pytest.mark.parametrize(
    "before,after",
    [
        ({"amount": 100}, {"amount": Decimal("1")}),
        ([{"amount": 100},], [{"amount": Decimal("1")},]),
        ({"internal": {"amount": 100}}, {"internal": {"amount": Decimal("1")}}),
        ({"internal": [{"amount": 100}]}, {"internal": [{"amount": Decimal("1")}]}),
        (
            [{"internal": [{"amount": 100}]},],
            [{"internal": [{"amount": Decimal("1")}]},],
        ),
    ],
)
def test_normalize(before, after, getpaid_client):
    result = getpaid_client._normalize(before)
    assert result == after


@pytest.mark.parametrize("response_status", [200, 201, 302])
def test_new_order(response_status, getpaid_client, requests_mock):
    my_order_id = f"{uuid.uuid4()}"
    requests_mock.post(
        "/api/v2_1/orders",
        json={
            "status": {"statusCode": "SUCCESS",},
            "redirectUri": "https://paywall.example.com/url",
            "orderId": "WZHF5FFDRJ140731GUEST000P01",
            "extOrderId": my_order_id,
        },
        status_code=response_status,
    )

    result = getpaid_client.new_order(
        amount=20, currency=Currency.PLN, order_id=my_order_id
    )
    assert "status" in result
    assert "redirectUri" in result
    assert "orderId" in result
    assert "extOrderId" in result

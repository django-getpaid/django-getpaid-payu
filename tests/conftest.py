import pytest
from pytest_factoryboy import register

from getpaid_payu.client import Client

from .factories import OrderFactory, PaymentFactory, PaywallEntryFactory

register(PaymentFactory)
register(OrderFactory)
register(PaywallEntryFactory)


@pytest.fixture
def getpaid_client(requests_mock):
    requests_mock.post(
        "/pl/standard/user/oauth/authorize",
        json={
            "access_token": "7524f96e-2d22-45da-bc64-778a61cbfc26",
            "token_type": "bearer",
            "expires_in": 43199,
            "grant_type": "client_credentials",
        },
    )
    yield Client(
        api_url="https://example.com/",
        pos_id=12345,
        second_key="abcdef",
        oauth_id=12345,
        oauth_secret="abcdef",
    )

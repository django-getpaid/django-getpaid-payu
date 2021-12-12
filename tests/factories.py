import factory
import swapper
from paywall.models import PaymentEntry


class OrderFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("color_name")
    total = factory.Faker(
        "pydecimal", positive=True, right_digits=2, min_value=10, max_value=500
    )
    currency = "EUR"

    class Meta:
        model = swapper.load_model("getpaid", "Order")


class PaymentFactory(factory.django.DjangoModelFactory):
    order = factory.SubFactory(OrderFactory)
    amount_required = factory.SelfAttribute("order.total")
    currency = factory.SelfAttribute("order.currency")
    description = factory.SelfAttribute("order.name")
    backend = "getpaid_payu"

    class Meta:
        model = swapper.load_model("getpaid", "Payment")


class PaywallEntryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PaymentEntry

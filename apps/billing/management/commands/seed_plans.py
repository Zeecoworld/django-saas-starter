from django.core.management.base import BaseCommand

from apps.billing.models import Plan


class Command(BaseCommand):
    help = "Creates example Starter/Pro plans. Edit the price IDs to match your Stripe dashboard."

    def handle(self, *args, **options):
        plans = [
            {
                "name": "Starter",
                "stripe_price_id": "price_starter_replace_me",
                "interval": "month",
                "amount_cents": 1900,
                "features": ["1 organization", "Up to 3 team members", "Email support"],
            },
            {
                "name": "Pro",
                "stripe_price_id": "price_pro_replace_me",
                "interval": "month",
                "amount_cents": 4900,
                "features": [
                    "Unlimited organizations",
                    "Unlimited team members",
                    "Priority support",
                ],
            },
        ]
        for data in plans:
            plan, created = Plan.objects.update_or_create(
                stripe_price_id=data["stripe_price_id"], defaults=data
            )
            action = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"{action} plan: {plan.name}"))

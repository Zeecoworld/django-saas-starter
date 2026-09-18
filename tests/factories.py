import factory

from apps.organizations.models import Membership, Organization
from apps.users.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    full_name = factory.Faker("name")

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        self.set_password(extracted or "testpass123")
        if create:
            self.save()


class OrganizationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Organization
        skip_postgeneration_save = True

    name = factory.Sequence(lambda n: f"Test Org {n}")
    owner = factory.SubFactory(UserFactory)

    @factory.post_generation
    def add_owner_membership(self, create, extracted, **kwargs):
        if create:
            Membership.objects.get_or_create(
                organization=self, user=self.owner, defaults={"role": Membership.Role.OWNER}
            )

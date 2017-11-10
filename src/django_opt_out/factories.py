# coding=utf-8
import factory
import faker
from django.contrib.auth import get_user_model
from django.utils import timezone

from . import models

fake = faker.Faker()


class UserFactory(factory.DjangoModelFactory):
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')
    username = factory.Sequence(lambda n: fake.user_name() + str(n))
    is_staff = False
    is_active = True

    class Meta:
        model = get_user_model()


class OptOutTagFactory(factory.DjangoModelFactory):
    name = factory.Faker('domain_word')

    class Meta:
        model = models.OptOutTag


class OptOutFactory(factory.DjangoModelFactory):
    email = factory.Faker('email')
    ts = factory.LazyFunction(timezone.now)

    class Meta:
        model = models.OptOut


class OptOutTagValueFactory(factory.DjangoModelFactory):
    opt_out = factory.SubFactory(OptOutTagFactory)
    tag = factory.SubFactory(OptOutTagFactory)

    class Meta:
        model = models.OptOutTagValue


class OptOutFeedbackFactory(factory.DjangoModelFactory):
    text = factory.Faker('sentence')

    class Meta:
        model = models.OptOutFeedback

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            self.tags.add(*extracted)

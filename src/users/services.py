import json
import uuid

import redis
from django.conf import settings

from .models import User
from .tasks import send_activation_mail


def create_activation_key(email: str) -> uuid.UUID:
    return uuid.uuid3(namespace=uuid.uuid4(), name=email)


def create_activation_link(activation_key: uuid.UUID) -> str:
    return f"https://frontend.com/users/activate/{activation_key}"


class Activator:
    def __init__(self, email: str):
        self.email = email

    def create_activation_key(self) -> uuid.UUID:
        return uuid.uuid3(namespace=uuid.uuid4(), name=self.email)

    def create_activation_link(self, activation_key: uuid.UUID) -> str:
        return f"https://frontend.com/users/activate/{activation_key}"

    def send_user_activation_email(self, activation_key: uuid.UUID) -> None:
        """Send activation email using SMTP."""

        activation_link = self.create_activation_link(activation_key)

        send_activation_mail.delay(
            recipient=self.email,
            activation_link=activation_link,
        )

    def save_activation_information(
        self, internal_user_id: int, activation_key: uuid.UUID
    ) -> None:
        """Save activation information to the cache.

        1. Connect to the cache

        2. Save the next structure to the cache:
        {
            "activation:ea57acaf-5ead-430d-914f-5f4fe95cafe7": {
                "user_id": 3
            }
        }

        3. Return None
        """

        # create Redis Connection instance
        # save record to the Redis with TTL of 1 day

        print(internal_user_id, activation_key)
        connection = redis.Redis.from_url(settings.CACHE_URL)

        payload = {"user_id": internal_user_id}
        connection.set(f"activation: {activation_key}", json.dumps(payload), ex=90000)

    def validate_activation(self, activation_key: uuid.UUID) -> None:

        # create Redis Connection instance
        # Generate the key base on the activation namespaces
        # update user table. is_active => True

        user_data = list(User.objects.values("id"))

        connection = redis.Redis.from_url(settings.CACHE_URL)

        res = connection.keys()

        for i in res:
            if (
                str(activation_key) == i.decode("utf-8")[-36:]
                and connection.ttl(f"activation: {activation_key}") < 86400
            ):
                result = connection.get(f"activation: {activation_key}")
                mydict = json.loads(result.decode("utf-8"))
                for k in user_data:
                    if mydict["user_id"] == k["id"]:
                        User.objects.get(id=k["id"])
                        User.objects.filter(id=k["id"]).update(is_active=True)

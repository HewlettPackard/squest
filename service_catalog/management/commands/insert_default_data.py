import logging

import yaml
from django.contrib.auth.models import User
from django.core.management import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def __init__(self):
        super().__init__()
        self.default_data = None
        print("[insert_default_data] Start")

    def handle(self, *args, **options):
        with open("default_data.yml", 'r') as stream_default_data:
            self.default_data = yaml.load(stream_default_data, Loader=yaml.BaseLoader)
            self.create_users()
            print("[insert_default_data] End")

    def create_users(self):
        if "users" in self.default_data:
            for user in self.default_data["users"]:
                try:
                    User.objects.get(username=user["username"])
                except User.DoesNotExist:
                    logger.info(f"Create User '{user['username']}'")
                    if "is_admin" in user and user["is_admin"] == "true":
                        User.objects.create_superuser(username=user["username"],
                                                      email=user["email"],
                                                      password=user["password"])
                    else:
                        User.objects.create_user(username=user["username"],
                                                 email=user["email"],
                                                 password=user["password"])

import os
import json
import random

from dotenv import load_dotenv
from locust import HttpUser, task, between

with open("test_users.jsonl") as f:
    USERS = [json.loads(line) for line in f if line.strip()]


load_dotenv()

class NotificationSender(HttpUser):

    host = os.getenv("SERVER_BASE_URL")

    # Random wait between 1 and 3 seconds between each simulated
    # user's requests - mimics a human, not a script firing as fast
    # as possible. Lower this later to find your ceiling.
    wait_time = between(1, 3)

    def on_start(self):
        # Each simulated Locust user is "assigned" one real test user
        # to authenticate as for its entire session - more realistic
        # than re-picking auth on every single request.

        ## IN FUTURE, GET A DIFFERENT USER FOR DIFFERENT CALL/TEST
        self.user = random.choice(USERS)

    @task
    def send_notification(self):
        target = random.choice(USERS)

        # Avoid sending a notification to yourself - edge case we
        # don't care about testing right now.
        while target["id"] == self.user["id"]:
            target = random.choice(USERS)

        self.client.post(
            "/api/v1/notifications/send/",
            json={
                "source_user": self.user["id"],
                "target_user": target["id"],
            },
            auth=(self.user["username"], self.user["password"]),
        )

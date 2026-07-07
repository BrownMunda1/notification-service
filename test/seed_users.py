import os
import time
import json
import secrets
import argparse
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

def seed_new_users(count: int):

    server_base_url = os.getenv("SERVER_BASE_URL")

    register_api_url = f"{server_base_url.rstrip("/")}/api/v1/users/register/"

    created_users: list[dict] = []

    for _ in range(count):

        username = f"test_user_{int(time.time())}"
        password = secrets.token_urlsafe(nbytes=12)
        try:
            response = requests.post(
                url=register_api_url,
                data={"username": username, "password": password}
            )
        except Exception as e:
            print(f"Unexpected Error while registering new user: {e}")
            raise

        if response.status_code in (200, 201):
            reveal_password = os.getenv("SEED_USERS_REVEAL_PASSWORD")
            if reveal_password and reveal_password.lower() == "true":
                response_json = response.json()
                id = response_json["id"]
                created_users.append({
                    "id": id,
                    "username": username,
                    "password": password
                })
        else:
            print(f"Unexpected error while creating new user:: Status Code {response.status_code}: {response.text}")

    save_users = Path(f"test_users.jsonl")
    with save_users.open("a", encoding="utf-8") as f:
        for user in created_users:
            f.write(json.dumps(user) + "\n")

    return created_users

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=1)

    args = parser.parse_args()
    start_time = time.time()
    users = seed_new_users(count=args.count)
    elapsed_time = time.time() - start_time
    print(f"Saved {len(users)} new users into database successfully. Time taken: {int(elapsed_time)} seconds")

if __name__ == "__main__":
    main()

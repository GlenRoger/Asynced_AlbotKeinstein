# auth.py

import config

def get_oauth_token():
    with open(config.OAUTH_TOKEN_FILE, "r") as file:
        return file.read().strip()
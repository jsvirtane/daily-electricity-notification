import json
import sys
import os
from typing import TypedDict
from dotenv import load_dotenv


sys.path.append("../pycaruna")
from pycaruna import Authenticator

load_dotenv()


class AuthData(TypedDict):
    token: str
    customer_id: str | None

def authenticate(debug: bool = False) -> AuthData:
    username = os.getenv("CARUNA_USERNAME")
    password = os.getenv("CARUNA_PASSWORD")

    if username is None or password is None:
        raise Exception("CARUNA_USERNAME and CARUNA_PASSWORD must be defined")

    # Authenticate using your e-mail and password. This will ultimately return an object containing a token (used for
    # Caruna Plus API interaction) and a user object which among other things contain your customer IDs (needed when
    # interacting with the Caruna Plus API).
    #
    # The token is valid for 60 minutes (as of this writing).
    authenticator = Authenticator(username, password)
    login_result = authenticator.login()

    auth_result: AuthData = {
        "token": login_result["token"],
        "customer_id": next(
            iter(login_result["user"]["ownCustomerNumbers"]),
            next(iter(login_result["user"]["representedCustomerNumbers"]), None),
        ),
    }



    if debug:
        print("Login result:")
        print(json.dumps(login_result, indent=2))
        print("Auth result:")
        print(json.dumps(auth_result, indent=2))

    return auth_result


if __name__ == "__main__":
    authenticate(debug=True)

import datetime

import jwt
from fastapi import HTTPException
from starlette import status
from starlette.status import HTTP_400_BAD_REQUEST

from .config import AUTH0_CONFIG, SECRET_RSA_KEY


class VerifyToken(object):
    """Does all the token verification using PyJWT"""

    def __init__(self, token):
        self.token = token
        self.config = AUTH0_CONFIG

        jwks_url = f'https://{self.config["DOMAIN"]}/.well-known/jwks.json'
        self.jwks_client = jwt.PyJWKClient(jwks_url)

    @staticmethod
    def create_custom(user_id: int, data: dict):
        data.update({
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=600),
            "kid": user_id
        })
        # when setting back to "algorithm=ALG" "NotImplementedError: Algorithm not supported" raises
        return jwt.encode(data, str(SECRET_RSA_KEY), algorithm="HS256")

    @staticmethod
    def verify_custom(token: str):
        try:
            decoded = jwt.decode(token, str(SECRET_RSA_KEY), algorithms=["HS256"])
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        return decoded

    def verify(self) ->dict:
        # This gets the 'kid' from the passed tokenSS
        try:
            self.signing_key = self.jwks_client.get_signing_key_from_jwt(
                self.token
            ).key
        except jwt.exceptions.PyJWKClientError as error:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=error.__str__())
        except jwt.exceptions.DecodeError as error:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=error.__str__())

        try:
            payload = jwt.decode(
                self.token,
                self.signing_key,
                algorithms=self.config["ALGORITHM"],
                audience=self.config["API_AUDIENCE"],
                issuer=self.config["ISSUER"],
            )
        except Exception as e:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))
        return payload

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt, JWTError, ExpiredSignatureError

from exceptions.security import InvalidTokenError, TokenExpiredError
from security.interfaces import JWTAuthManagerInterface


class JWTAuthManager(JWTAuthManagerInterface):
    _ACCESS_KEY_TIMEDELTA_MINUTES = 60
    _REFRESH_KEY_TIMEDELTA_MINUTES = 60 * 24 * 7

    def __init__(self, secret_key_access: str, secret_key_refresh: str, algorithm: str):
        self._secret_key_access = secret_key_access
        self._secret_key_refresh = secret_key_refresh
        self._algorithm = algorithm

    def _create_token(
        self, data: dict, secret_key: str, expires_delta: timedelta
    ) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, secret_key, algorithm=self._algorithm)

    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        return self._create_token(
            data,
            self._secret_key_access,
            expires_delta or timedelta(minutes=self._ACCESS_KEY_TIMEDELTA_MINUTES),
        )

    def create_refresh_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        return self._create_token(
            data,
            self._secret_key_refresh,
            expires_delta or timedelta(minutes=self._REFRESH_KEY_TIMEDELTA_MINUTES),
        )

    def decode_access_token(self, token: str) -> dict:
        try:
            return jwt.decode(
                token, self._secret_key_access, algorithms=[self._algorithm]
            )
        except ExpiredSignatureError:
            raise TokenExpiredError
        except JWTError:
            raise InvalidTokenError

    def decode_refresh_token(self, token: str) -> dict:
        try:
            return jwt.decode(
                token, self._secret_key_refresh, algorithms=[self._algorithm]
            )
        except ExpiredSignatureError:
            raise TokenExpiredError
        except JWTError:
            raise InvalidTokenError

    def verify_refresh_token_or_raise(self, token: str) -> None:
        self.decode_refresh_token(token)

    def verify_access_token_or_raise(self, token: str) -> None:
        self.decode_access_token(token)

from abc import ABC, abstractmethod
from typing import TypeVar, Generic
from pydantic import BaseModel

T = TypeVar("T")


class AuthResponse(BaseModel):
    success: bool
    user_id: str


class Authenticator(ABC, Generic[T]):
    @abstractmethod
    def authenticate(self, request: T) -> AuthResponse:
        pass

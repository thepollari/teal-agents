from auth.authenticator import Authenticator, AuthResponse
from pydantic import BaseModel


class UserIdOnlyAuthRequest(BaseModel):
    user_id: str


class UserIdOnlyAuthenticator(Authenticator[UserIdOnlyAuthRequest]):
    def authenticate(self, request: UserIdOnlyAuthRequest) -> AuthResponse:
        return AuthResponse(success=True, user_id=request.user_id)

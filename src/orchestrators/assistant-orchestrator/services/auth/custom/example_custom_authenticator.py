from auth.authenticator import Authenticator, AuthResponse
from pydantic import BaseModel


class ExampleUserIdOnlyAuthRequest(BaseModel):
    user_id: str


class ExampleUserIdOnlyAuthenticator(Authenticator[ExampleUserIdOnlyAuthRequest]):
    def authenticate(self, request: ExampleUserIdOnlyAuthRequest) -> AuthResponse:
        if request.user_id == "good_id":
            return AuthResponse(success=True, user_id=request.user_id)
        else:
            return AuthResponse(success=False, user_id=request.user_id)

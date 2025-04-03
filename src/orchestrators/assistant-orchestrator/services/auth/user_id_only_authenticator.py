from auth.authenticator import Authenticator, AuthResponse
from pydantic import BaseModel


class UserIdOnlyAuthRequest(BaseModel):
    user_id: str


class UserIdOnlyAuthenticator(Authenticator[UserIdOnlyAuthRequest]):
    def authenticate(self, orchestrator_name: str, request: UserIdOnlyAuthRequest) -> AuthResponse:
        return AuthResponse(success=True, orch_name=orchestrator_name, user_id=request.user_id)

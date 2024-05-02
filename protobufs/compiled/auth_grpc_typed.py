from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict

from config.grpc import GRPCConnection
from utils.decorators import handle_grpc_response_error


@dataclass
class Empty:
    detail: str | None


@dataclass
class AuthRequest:
    token: str


@dataclass
class User:
    id: int


@dataclass
class AuthResponse:
    user: User


@dataclass
class LoginRequest:
    login: str
    password: str


@dataclass
class JWTTokens:
    access: str
    refresh: str
    detail: str | None


@dataclass
class CodeSentResponse:
    email: str
    message: str
    detail: str | None


@dataclass
class RefreshTokensRequest:
    refresh: str


@dataclass
class ChangePasswordRequest:
    user_id: int
    current_password: int
    new_password: int
    re_new_password: int


@dataclass
class ResetPasswordRequest:
    email: str


@dataclass
class ResetPasswordConfirmRequest:
    email: str
    code: str
    new_password: str
    re_new_password: str


@dataclass
class RegisterRequest:
    email: str
    username: str
    password: str
    re_password: str


@dataclass
class RepeatRegisterRequest:
    email: str


@dataclass
class ConfirmRegisterRequest:
    email: str
    code: str


@dataclass
class CheckEmailConfirmedRequest:
    user_id: int


@dataclass
class CheckEmailConfirmedResponse:
    confirmed: bool | None


class IAuthStub(ABC):
    @abstractmethod
    async def auth(self, request: AuthRequest) -> AuthResponse: ...

    @abstractmethod
    async def jwt_refresh(self, request: RefreshTokensRequest) -> JWTTokens: ...

    @abstractmethod
    async def login(self, request: LoginRequest) -> JWTTokens: ...

    @abstractmethod
    async def password_change(self, request: ChangePasswordRequest) -> Empty: ...

    @abstractmethod
    async def password_reset(
        self, request: ResetPasswordRequest
    ) -> CodeSentResponse: ...

    @abstractmethod
    async def password_reset_confirm(
        self, request: ResetPasswordConfirmRequest
    ) -> Empty: ...

    @abstractmethod
    async def register(self, request: RegisterRequest) -> CodeSentResponse: ...

    @abstractmethod
    async def register_repeat(
        self, request: RepeatRegisterRequest
    ) -> CodeSentResponse: ...

    @abstractmethod
    async def register_confirm(self, request: ConfirmRegisterRequest) -> JWTTokens: ...

    @abstractmethod
    async def check_email_confirmed(
        self, request: CheckEmailConfirmedRequest
    ) -> CheckEmailConfirmedResponse: ...


class AuthStub(IAuthStub):
    def __init__(self, connection: GRPCConnection) -> None:
        self.connection = connection

    @handle_grpc_response_error
    async def auth(self, request: AuthRequest) -> AuthResponse:
        from auth_pb2 import AuthRequest as _AuthRequest  # noqa: E501

        response = await self.connection.stub.auth(_AuthRequest(**asdict(request)))
        return AuthResponse(user=User(id=response.user.id))

    @handle_grpc_response_error
    async def jwt_refresh(self, request: RefreshTokensRequest) -> JWTTokens:
        from auth_pb2 import RefreshTokensRequest as _RefreshTokensRequest  # noqa: E501

        response = await self.connection.stub.jwt_refresh(
            _RefreshTokensRequest(**asdict(request))
        )
        return JWTTokens(
            access=response.access,
            refresh=response.refresh,
            detail=response.detail,
        )

    @handle_grpc_response_error
    async def login(self, request: LoginRequest) -> JWTTokens:
        from auth_pb2 import LoginRequest as _LoginRequest  # noqa: E501

        response = await self.connection.stub.login(_LoginRequest(**asdict(request)))
        return JWTTokens(
            access=response.access,
            refresh=response.refresh,
            detail=response.detail,
        )

    @handle_grpc_response_error
    async def password_change(self, request: ChangePasswordRequest) -> Empty:
        from auth_pb2 import (
            ChangePasswordRequest as _ChangePasswordRequest,
        )  # noqa: E501

        response = await self.connection.stub.password_change(
            _ChangePasswordRequest(**asdict(request))
        )
        return Empty(detail=response.detail)

    @handle_grpc_response_error
    async def password_reset(self, request: ResetPasswordRequest) -> CodeSentResponse:
        from auth_pb2 import ResetPasswordRequest as _ResetPasswordRequest  # noqa: E501

        response = await self.connection.stub.password_reset(
            _ResetPasswordRequest(**asdict(request))
        )
        return CodeSentResponse(
            email=response.email,
            message=response.message,
            detail=response.detail,
        )

    @handle_grpc_response_error
    async def password_reset_confirm(
        self, request: ResetPasswordConfirmRequest
    ) -> Empty:
        from auth_pb2 import (
            ResetPasswordConfirmRequest as _ResetPasswordConfirmRequest,
        )  # noqa: E501

        response = await self.connection.stub.password_reset_confirm(
            _ResetPasswordConfirmRequest(**asdict(request))
        )
        return Empty(detail=response.detail)

    @handle_grpc_response_error
    async def register(self, request: RegisterRequest) -> CodeSentResponse:
        from auth_pb2 import RegisterRequest as _RegisterRequest  # noqa: E501

        response = await self.connection.stub.register(
            _RegisterRequest(**asdict(request))
        )
        return CodeSentResponse(
            email=response.email,
            message=response.message,
            detail=response.detail,
        )

    @handle_grpc_response_error
    async def register_repeat(self, request: RepeatRegisterRequest) -> CodeSentResponse:
        from auth_pb2 import (
            RepeatRegisterRequest as _RepeatRegisterRequest,
        )  # noqa: E501

        response = await self.connection.stub.register_repeat(
            _RepeatRegisterRequest(**asdict(request))
        )
        return CodeSentResponse(
            email=response.email,
            message=response.message,
            detail=response.detail,
        )

    @handle_grpc_response_error
    async def register_confirm(self, request: ConfirmRegisterRequest) -> JWTTokens:
        from auth_pb2 import (
            ConfirmRegisterRequest as _ConfirmRegisterRequest,
        )  # noqa: E501

        response = await self.connection.stub.register_confirm(
            _ConfirmRegisterRequest(**asdict(request))
        )
        return JWTTokens(
            access=response.access,
            refresh=response.refresh,
            detail=response.detail,
        )

    @handle_grpc_response_error
    async def check_email_confirmed(
        self, request: CheckEmailConfirmedRequest
    ) -> CheckEmailConfirmedResponse:
        from auth_pb2 import (
            CheckEmailConfirmedRequest as _CheckEmailConfirmedRequest,
        )  # noqa: E501

        response = await self.connection.stub.check_email_confirmed(
            _CheckEmailConfirmedRequest(**asdict(request))
        )
        return CheckEmailConfirmedResponse(confirmed=response.confirmed)

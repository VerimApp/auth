from dependency_injector.wiring import Closing, Provide, inject

from protobufs.compiled import auth_pb2_grpc
from protobufs.compiled.auth_pb2 import (
    AuthResponse,
    User,
    Empty,
    JWTTokens,
    CodeSentResponse,
    CheckEmailConfirmedResponse,
)
from schemas import (
    RefreshTokensSchema,
    LoginSchema,
    ChangePasswordSchema,
    ResetPasswordSchema,
    ResetPasswordConfirmSchema,
    RegistrationSchema,
    RepeatRegistrationCodeSchema,
    ConfirmRegistrationSchema,
)
from config.di import Container
from services.jwt import IRefreshJWTTokens
from services.login import ILoginUser
from services.authenticate import IAuthenticate
from services.password import IChangePassword, IResetPassword, IConfirmResetPassword
from services.registration import (
    IRegisterUser,
    IRepeatRegistrationCode,
    IConfirmRegistration,
    ICheckRegistration,
)
from utils.decorators import handle_grpc_request_error
from utils.exceptions import CustomException


class GRPCAuth(auth_pb2_grpc.AuthServicer):
    @inject
    async def auth(
        self, request, context, service: IAuthenticate = Provide[Container.authenticate]
    ):
        user = await service(token=request.token)
        try:
            return AuthResponse(user=User(id=user.id))
        except CustomException as e:
            return AuthResponse(user=User(id=-1), error_message=str(e))

    @handle_grpc_request_error(JWTTokens)
    @inject
    async def jwt_refresh(
        self,
        request,
        context,
        service: IRefreshJWTTokens = Provide[Container.refresh_jwt_tokens],
    ):
        tokens = await service(entry=RefreshTokensSchema(refresh=request.refresh))
        return JWTTokens(access=tokens.access, refresh=tokens.refresh)

    @handle_grpc_request_error(JWTTokens)
    @inject
    async def login(
        self,
        request,
        context,
        service: ILoginUser = Provide[Container.login_user],
    ):
        tokens = await service(
            entry=LoginSchema(login=request.login, password=request.password)
        )
        return JWTTokens(access=tokens.access, refresh=tokens.refresh)

    @handle_grpc_request_error(Empty)
    @inject
    async def password_change(
        self,
        request,
        context,
        service: IChangePassword = Provide[Container.change_password],
    ):
        await service(
            user_id=request.user_id,
            entry=ChangePasswordSchema(
                current_password=request.current_password,
                new_password=request.new_password,
                re_new_password=request.re_new_password,
            ),
        )
        return Empty()

    @handle_grpc_request_error(CodeSentResponse)
    @inject
    async def password_reset(
        self,
        request,
        context,
        service: IResetPassword = Provide[Container.reset_password],
    ):
        response = await service(entry=ResetPasswordSchema(email=request.email))
        return CodeSentResponse(email=response.email, message=response.message)

    @handle_grpc_request_error(Empty)
    @inject
    async def password_reset_confirm(
        self,
        request,
        context,
        service: IConfirmResetPassword = Provide[Container.confirm_reset_password],
    ):
        await service(
            entry=ResetPasswordConfirmSchema(
                email=request.email,
                code=request.code,
                new_password=request.new_password,
                re_new_password=request.re_new_password,
            )
        )
        return Empty()

    @handle_grpc_request_error(CodeSentResponse)
    @inject
    async def register(
        self,
        request,
        context,
        service: IRegisterUser = Provide[Container.register_user],
    ):
        response = await service(
            entry=RegistrationSchema(
                email=request.email,
                username=request.username,
                password=request.password,
                re_password=request.re_password,
            )
        )
        return CodeSentResponse(email=response.email, message=response.message)

    @handle_grpc_request_error(CodeSentResponse)
    @inject
    async def register_repeat(
        self,
        request,
        context,
        service: IRepeatRegistrationCode = Provide[Container.repeat_registration_code],
    ):
        response = await service(
            entry=RepeatRegistrationCodeSchema(email=request.email)
        )
        return CodeSentResponse(email=response.email, message=response.message)

    @handle_grpc_request_error(JWTTokens)
    @inject
    async def register_confirm(
        self,
        request,
        context,
        service: IConfirmRegistration = Provide[Container.confirm_registration],
    ):
        tokens = await service(
            entry=ConfirmRegistrationSchema(email=request.email, code=request.code)
        )
        return JWTTokens(access=tokens.access, refresh=tokens.refresh)

    @handle_grpc_request_error(CheckEmailConfirmedResponse)
    @inject
    async def check_email_confirmed(
        self,
        request,
        context,
        service: ICheckRegistration = Provide[Container.check_registration],
    ):
        return CheckEmailConfirmedResponse(
            confirmed=await service(user_id=request.user_id)
        )

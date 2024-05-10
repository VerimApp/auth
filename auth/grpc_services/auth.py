from dependency_injector.wiring import Provide, inject
from sqlalchemy.ext.asyncio import AsyncSession

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
from config.db import Database
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
from utils.decorators import handle_grpc_request_error, inject_session
from utils.exceptions import CustomException


class GRPCAuth(auth_pb2_grpc.AuthServicer):
    @inject_session
    @inject
    async def auth(
        self,
        request,
        context,
        session: AsyncSession,
        service: IAuthenticate = Provide[Container.authenticate],
    ):
        user = await service(session=session, token=request.token)
        try:
            return AuthResponse(user=User(id=user.id))
        except CustomException as e:
            return AuthResponse(user=User(id=-1), error_message=str(e))

    @handle_grpc_request_error(JWTTokens)
    @inject_session
    @inject
    async def jwt_refresh(
        self,
        request,
        context,
        session: AsyncSession,
        service: IRefreshJWTTokens = Provide[Container.refresh_jwt_tokens],
    ):
        tokens = await service(
            session=session, entry=RefreshTokensSchema(refresh=request.refresh)
        )
        return JWTTokens(access=tokens.access, refresh=tokens.refresh)

    @handle_grpc_request_error(JWTTokens)
    @inject_session
    @inject
    async def login(
        self,
        request,
        context,
        session: AsyncSession,
        service: ILoginUser = Provide[Container.login_user],
    ):
        tokens = await service(
            session=session,
            entry=LoginSchema(login=request.login, password=request.password),
        )
        return JWTTokens(access=tokens.access, refresh=tokens.refresh)

    @handle_grpc_request_error(Empty)
    @inject_session
    @inject
    async def password_change(
        self,
        request,
        context,
        session: AsyncSession,
        service: IChangePassword = Provide[Container.change_password],
    ):
        await service(
            session=session,
            user_id=request.user_id,
            entry=ChangePasswordSchema(
                current_password=request.current_password,
                new_password=request.new_password,
                re_new_password=request.re_new_password,
            ),
        )
        return Empty()

    @handle_grpc_request_error(CodeSentResponse)
    @inject_session
    @inject
    async def password_reset(
        self,
        request,
        context,
        session: AsyncSession,
        service: IResetPassword = Provide[Container.reset_password],
    ):
        response = await service(
            session=session, entry=ResetPasswordSchema(email=request.email)
        )
        return CodeSentResponse(email=response.email, message=response.message)

    @handle_grpc_request_error(Empty)
    @inject_session
    @inject
    async def password_reset_confirm(
        self,
        request,
        context,
        session: AsyncSession,
        service: IConfirmResetPassword = Provide[Container.confirm_reset_password],
    ):
        await service(
            session=session,
            entry=ResetPasswordConfirmSchema(
                email=request.email,
                code=request.code,
                new_password=request.new_password,
                re_new_password=request.re_new_password,
            ),
        )
        return Empty()

    @handle_grpc_request_error(CodeSentResponse)
    @inject_session
    @inject
    async def register(
        self,
        request,
        context,
        session: AsyncSession,
        service: IRegisterUser = Provide[Container.register_user],
    ):
        response = await service(
            session=session,
            entry=RegistrationSchema(
                email=request.email,
                username=request.username,
                password=request.password,
                re_password=request.re_password,
            ),
        )
        return CodeSentResponse(email=response.email, message=response.message)

    @handle_grpc_request_error(CodeSentResponse)
    @inject_session
    @inject
    async def register_repeat(
        self,
        request,
        context,
        session: AsyncSession,
        service: IRepeatRegistrationCode = Provide[Container.repeat_registration_code],
    ):
        response = await service(
            session=session, entry=RepeatRegistrationCodeSchema(email=request.email)
        )
        return CodeSentResponse(email=response.email, message=response.message)

    @handle_grpc_request_error(JWTTokens)
    @inject_session
    @inject
    async def register_confirm(
        self,
        request,
        context,
        session: AsyncSession,
        service: IConfirmRegistration = Provide[Container.confirm_registration],
    ):
        tokens = await service(
            session=session,
            entry=ConfirmRegistrationSchema(email=request.email, code=request.code),
        )
        return JWTTokens(access=tokens.access, refresh=tokens.refresh)

    @handle_grpc_request_error(CheckEmailConfirmedResponse)
    @inject_session
    @inject
    async def check_email_confirmed(
        self,
        request,
        context,
        session: AsyncSession,
        service: ICheckRegistration = Provide[Container.check_registration],
    ):
        return CheckEmailConfirmedResponse(
            confirmed=await service(session=session, user_id=request.user_id)
        )

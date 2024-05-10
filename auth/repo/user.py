from typing import Dict

from sqlalchemy import func, or_, select, update, delete, exists, Select, Result
from sqlalchemy.ext.asyncio import AsyncSession

from schemas import RegistrationSchema
from services.repo import IUserRepo
from models.users import User
from utils.decorators import handle_orm_error, row_to_model


class UserRepo(IUserRepo):
    model = User

    @handle_orm_error
    async def all(
        self,
        session: AsyncSession,
        *,
        include_not_confirmed_email: bool = False,
        as_select: bool = False,
    ) -> Result[User] | Select[User]:
        qs = select(self.model)
        if not include_not_confirmed_email:
            qs = qs.filter(self.model.email_confirmed == True)  # noqa: E712
        if as_select:
            return qs
        return await session.execute(qs)

    @handle_orm_error
    async def create(self, session: AsyncSession, entry: RegistrationSchema) -> User:
        user = self.model(
            email=entry.email.lower(), username=entry.username, password=entry.password
        )
        session.add(user)
        await session.flush([user])
        await session.refresh(user)
        return user

    @handle_orm_error
    async def update(self, session: AsyncSession, user: User, values: Dict) -> None:
        await session.execute(
            update(self.model).filter(self.model.id == user.id).values(**values)
        )

    @handle_orm_error
    async def delete(self, session: AsyncSession, user: User) -> None:
        await session.execute(delete(self.model).filter(self.model.id == user.id))

    @handle_orm_error
    async def email_exists(self, session: AsyncSession, email: str) -> bool:
        qs = await self.all(session, include_not_confirmed_email=True, as_select=True)
        result = await session.execute(
            exists(qs).where(func.lower(self.model.email) == func.lower(email)).select()
        )
        return bool(result.scalar())

    @handle_orm_error
    async def username_exists(self, session: AsyncSession, username: str) -> bool:
        qs = await self.all(session, include_not_confirmed_email=True, as_select=True)
        result = await session.execute(
            exists(qs)
            .where(func.lower(self.model.username) == func.lower(username))
            .select()
        )
        return bool(result.scalar())

    @handle_orm_error
    @row_to_model()
    async def get_by_login(self, session: AsyncSession, login: str) -> User | None:
        qs = await self.all(session, as_select=True)
        result = await session.execute(
            qs.filter(
                or_(
                    func.lower(self.model.username) == func.lower(login),
                    func.lower(self.model.email) == func.lower(login),
                )
            )
        )
        return result.first()

    @handle_orm_error
    @row_to_model()
    async def get_by_id(self, session: AsyncSession, id: int) -> User | None:
        qs = await self.all(session, include_not_confirmed_email=True, as_select=True)
        result = await session.execute(qs.filter(self.model.id == id))
        return result.first()

    @handle_orm_error
    @row_to_model()
    async def get_by_email(
        self,
        session: AsyncSession,
        email: str,
        *,
        include_not_confirmed_email: bool = False,
    ) -> User | None:
        qs = await self.all(
            session,
            include_not_confirmed_email=include_not_confirmed_email,
            as_select=True,
        )
        result = await session.execute(
            qs.filter(
                func.lower(self.model.email) == func.lower(email),
            )
        )
        return result.first()

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
        session: AsyncSession | None = None,
        *,
        include_not_confirmed_email: bool = False,
        as_select: bool = False,
    ) -> Result[User] | Select[User]:
        async with session or self.session_factory() as session:
            qs = select(self.model)
            if not include_not_confirmed_email:
                qs = qs.filter(self.model.email_confirmed == True)  # noqa: E712
            if as_select:
                return qs
            return await session.execute(qs)

    @handle_orm_error
    async def create(self, entry: RegistrationSchema) -> User:
        user = self.model(
            email=entry.email.lower(), username=entry.username, password=entry.password
        )
        async with self.session_factory() as session:
            session.add(user)
            await session.commit()
            await session.refresh(user)
        return user

    @handle_orm_error
    async def update(self, user: User, values: Dict) -> None:
        async with self.session_factory() as session:
            await session.execute(
                update(self.model).filter(self.model.id == user.id).values(**values)
            )
            await session.commit()

    @handle_orm_error
    async def delete(self, user: User) -> None:
        async with self.session_factory() as session:
            await session.execute(delete(self.model).filter(self.model.id == user.id))
            await session.commit()

    @handle_orm_error
    async def email_exists(self, email: str) -> bool:
        async with self.session_factory() as session:
            qs = await self.all(
                session, include_not_confirmed_email=True, as_select=True
            )
            result = await session.execute(
                exists(qs)
                .where(func.lower(self.model.email) == func.lower(email))
                .select()
            )
            return bool(result.scalar())

    @handle_orm_error
    async def username_exists(self, username: str) -> bool:
        async with self.session_factory() as session:
            qs = await self.all(
                session, include_not_confirmed_email=True, as_select=True
            )
            result = await session.execute(
                exists(qs)
                .where(func.lower(self.model.username) == func.lower(username))
                .select()
            )
            return bool(result.scalar())

    @handle_orm_error
    @row_to_model()
    async def get_by_login(self, login: str) -> User | None:
        async with self.session_factory() as session:
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
    async def get_by_id(self, id: int) -> User | None:
        async with self.session_factory() as session:
            qs = await self.all(
                session, include_not_confirmed_email=True, as_select=True
            )
            result = await session.execute(qs.filter(self.model.id == id))
            user = result.first()
        return user

    @handle_orm_error
    @row_to_model()
    async def get_by_email(
        self, email: str, *, include_not_confirmed_email: bool = False
    ) -> User | None:
        async with self.session_factory() as session:
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

from typing import Dict

from sqlalchemy import func, or_
from sqlalchemy.orm import Session, Query

from schemas import RegistrationSchema
from services.repo import IUserRepo
from models.users import User
from utils.types import UserType
from utils.decorators import handle_orm_error


class UserRepo(IUserRepo):
    model = User

    @handle_orm_error
    def all(self, session: Session | None = None, *, include_not_confirmed_email: bool = False) -> Query:
        with session or self.session_factory() as session:
            qs = session.query(self.model)
            if not include_not_confirmed_email:
                qs = qs.filter(self.model.email_confirmed == True)  # noqa: E712
            return qs

    @handle_orm_error
    def create(self, entry: RegistrationSchema) -> UserType:
        with self.session_factory() as session:
            user = self.model(
                email=entry.email.lower(), username=entry.username, password=entry.password
            )
            session.add(user)
            session.commit()
            session.refresh(user)
        return user

    @handle_orm_error
    def update(self, user: UserType, values: Dict) -> None:
        with self.session_factory() as session:
            session.query(self.model).filter(self.model.id == user.id).update(values)
            session.commit()

    @handle_orm_error
    def delete(self, user: UserType) -> None:
        with self.session_factory() as session:
            session.query(self.model).filter(self.model.id == user.id).delete()
            session.commit()

    @handle_orm_error
    def email_exists(self, email: str) -> bool:
        with self.session_factory() as session:
            return session.query(
                self.all(include_not_confirmed_email=True)
                .exists()
                .where(func.lower(self.model.email) == func.lower(email))
            ).scalar()

    @handle_orm_error
    def username_exists(self, username: str) -> bool:
        with self.session_factory() as session:
            return session.query(
                self.all(include_not_confirmed_email=True)
                .exists()
                .where(func.lower(self.model.username) == func.lower(username))
            ).scalar()

    @handle_orm_error
    def get_by_login(self, login: str) -> UserType | None:
        with self.session_factory() as session:
            return (
                self.all(session)
                .filter(
                    or_(
                        func.lower(self.model.username) == func.lower(login),
                        func.lower(self.model.email) == func.lower(login),
                    )
                )
                .first()
            )

    @handle_orm_error
    def get_by_id(self, id: int) -> UserType | None:
        with self.session_factory() as session:
            user = (
                self.all(session, include_not_confirmed_email=True)
                .filter(self.model.id == id)
                .first()
            )
            if user:
                session.expunge(user)
            return user

    @handle_orm_error
    def get_by_email(
        self, email: str, *, include_not_confirmed_email: bool = False
    ) -> UserType | None:
        with self.session_factory() as session:
            return (
                self.all(session, include_not_confirmed_email=include_not_confirmed_email)
                .filter(
                    func.lower(self.model.email) == func.lower(email),
                )
                .first()
            )

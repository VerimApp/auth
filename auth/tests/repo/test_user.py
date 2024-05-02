from datetime import datetime, timezone

from config.di import get_di_test_container
from models.users import User
from services.repo import IUserRepo
from schemas import RegistrationSchema
from utils.test import RepoTestMixin


container = get_di_test_container()


class TestUserRepo(RepoTestMixin):
    repo: IUserRepo = container.user_repo()

    def setup_method(self):
        self.now = datetime(10, 10, 10, tzinfo=timezone.utc)
        self.entry = RegistrationSchema(
            email="testuser1@email.com",
            username="testuser1",
            password="testpassword",
            re_password="testpassword",
        )

    def teardown_method(self):
        with self.repo.session_factory() as session:
            session.query(User).delete()
            session.commit()

    def _create(self, *, unique_fields_suffix: str = "", confirm_email: bool = False):
        if unique_fields_suffix:
            self.entry.email = f"{unique_fields_suffix}@".join(
                self.entry.email.split("@")
            )
            self.entry.username += unique_fields_suffix
        user = self.repo.create(self.entry)
        if confirm_email:
            self.repo.update(user, {"email_confirmed": True})
        return user

    def test_all(self):
        assert self.repo.all().count() == 0
        user = self._create()
        assert self.repo.all().count() == 0
        self.repo.update(user, {"email_confirmed": True})
        assert self.repo.all().count() == 1
        user = self._create(unique_fields_suffix="2")
        assert self.repo.all().count() == 1
        self.repo.update(user, {"email_confirmed": True})
        assert self.repo.all().count() == 2

    def test_all_include_not_confirmed_email(self):
        assert self.repo.all(include_not_confirmed_email=True).count() == 0
        user = self._create()
        assert self.repo.all(include_not_confirmed_email=True).count() == 1
        self.repo.update(user, {"email_confirmed": True})
        assert self.repo.all(include_not_confirmed_email=True).count() == 1
        user = self._create(unique_fields_suffix="2")
        assert self.repo.all(include_not_confirmed_email=True).count() == 2
        self.repo.update(user, {"email_confirmed": True})
        assert self.repo.all(include_not_confirmed_email=True).count() == 2

    def test_create(self):
        user = self._create()

        assert isinstance(user, User)
        assert user.email == self.entry.email
        assert user.username == self.entry.username
        assert user.password == self.entry.password
        assert user.first_name is None
        assert user.last_name is None
        assert user.is_active
        assert user.created_at is not None
        assert user.updated_at is not None
        assert user.tokens_revoked_at is None
        assert user.email_confirmed == False

    def test_create_email_normalization(self):
        self.entry.email = "tEsTuSeR@eMaIl.CoM"
        user = self._create()

        assert isinstance(user, User)
        assert user.email == self.entry.email.lower()
        assert user.username == self.entry.username
        assert user.password == self.entry.password
        assert user.first_name is None
        assert user.last_name is None
        assert user.is_active
        assert user.created_at is not None
        assert user.updated_at is not None
        assert user.tokens_revoked_at is None
        assert user.email_confirmed == False

    def test_update(self):
        user = self._create()

        assert user.email_confirmed == False
        assert user.tokens_revoked_at is None
        self.repo.update(user, {"email_confirmed": True})
        user = self.repo.get_by_id(user.id)
        assert user.email_confirmed
        assert user.tokens_revoked_at is None
        self.repo.update(user, {"tokens_revoked_at": self.now})
        user = self.repo.get_by_id(user.id)
        assert user.email_confirmed
        assert user.tokens_revoked_at == self.now

    def test_delete(self):
        user = self._create()
        assert self.repo.get_by_id(user.id) is not None
        self.repo.delete(user)
        assert self.repo.get_by_id(user.id) is None

    def test_email_exists(self):
        assert self.repo.email_exists(self.entry.email) == False
        assert self.repo.email_exists(self.entry.email.upper()) == False
        assert (
            self.repo.email_exists(
                "".join(
                    self.entry.email[i] if i % 2 == 0 else self.entry.email[i].upper()
                    for i in range(len(self.entry.email))
                )
            )
            == False
        )
        self._create()
        assert self.repo.email_exists(self.entry.email)
        assert self.repo.email_exists(self.entry.email.upper())
        assert self.repo.email_exists(
            "".join(
                self.entry.email[i] if i % 2 == 0 else self.entry.email[i].upper()
                for i in range(len(self.entry.email))
            )
        )

    def test_username_exists(self):
        assert self.repo.username_exists(self.entry.username) == False
        assert self.repo.username_exists(self.entry.username.upper()) == False
        assert (
            self.repo.username_exists(
                "".join(
                    (
                        self.entry.username[i]
                        if i % 2 == 0
                        else self.entry.username[i].upper()
                    )
                    for i in range(len(self.entry.username))
                )
            )
            == False
        )
        self._create()
        assert self.repo.username_exists(self.entry.username)
        assert self.repo.username_exists(self.entry.username.upper())
        assert self.repo.username_exists(
            "".join(
                self.entry.username[i] if i % 2 == 0 else self.entry.username[i].upper()
                for i in range(len(self.entry.username))
            )
        )

    def test_get_by_login_as_email(self):
        assert self.repo.get_by_login(self.entry.email) is None
        assert self.repo.get_by_login(self.entry.email.upper()) is None
        assert (
            self.repo.get_by_login(
                "".join(
                    self.entry.email[i] if i % 2 == 0 else self.entry.email[i].upper()
                    for i in range(len(self.entry.email))
                )
            )
            is None
        )
        user = self._create(confirm_email=True)
        assert self.repo.get_by_login(self.entry.email).id == user.id
        assert self.repo.get_by_login(self.entry.email.upper()).id == user.id
        assert (
            self.repo.get_by_login(
                "".join(
                    self.entry.email[i] if i % 2 == 0 else self.entry.email[i].upper()
                    for i in range(len(self.entry.email))
                )
            ).id
            == user.id
        )

    def test_get_by_login_as_username(self):
        assert self.repo.get_by_login(self.entry.username) is None
        assert self.repo.get_by_login(self.entry.username.upper()) is None
        assert (
            self.repo.get_by_login(
                "".join(
                    (
                        self.entry.username[i]
                        if i % 2 == 0
                        else self.entry.username[i].upper()
                    )
                    for i in range(len(self.entry.username))
                )
            )
            is None
        )
        user = self._create(confirm_email=True)
        assert self.repo.get_by_login(self.entry.username).id == user.id
        assert self.repo.get_by_login(self.entry.username.upper()).id == user.id
        assert (
            self.repo.get_by_login(
                "".join(
                    (
                        self.entry.username[i]
                        if i % 2 == 0
                        else self.entry.username[i].upper()
                    )
                    for i in range(len(self.entry.username))
                )
            ).id
            == user.id
        )

    def test_by_id(self):
        assert self.repo.get_by_id(1) is None
        user = self._create()
        assert self.repo.get_by_id(user.id).id == user.id
        self.repo.update(user, {"email_confirmed": True})
        assert self.repo.get_by_id(user.id).id == user.id

    def test_by_email(self):
        assert self.repo.get_by_email(self.entry.email) is None
        assert self.repo.get_by_email(self.entry.email.upper()) is None
        assert (
            self.repo.get_by_email(
                "".join(
                    self.entry.email[i] if i % 2 == 0 else self.entry.email[i].upper()
                    for i in range(len(self.entry.email))
                )
            )
            is None
        )
        user = self._create(confirm_email=True)
        assert self.repo.get_by_email(self.entry.email).id == user.id
        assert self.repo.get_by_email(self.entry.email.upper()).id == user.id
        assert (
            self.repo.get_by_email(
                "".join(
                    self.entry.email[i] if i % 2 == 0 else self.entry.email[i].upper()
                    for i in range(len(self.entry.email))
                )
            ).id
            == user.id
        )

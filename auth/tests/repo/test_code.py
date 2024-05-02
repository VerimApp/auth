from config.di import get_di_test_container
from models.codes import Code
from models.users import User
from services.codes.repo import ICodeRepo
from services.codes.types import CodeTypeEnum
from services.entries import CreateCodeEntry
from schemas import RegistrationSchema
from utils.test import RepoTestMixin


container = get_di_test_container()


class TestCodeRepo(RepoTestMixin):
    repo: ICodeRepo = container._code_repo()

    def setup_method(self):
        self.user = self._create_user()
        self.entry = CreateCodeEntry(
            user_id=self.user.id, code="1111", type=CodeTypeEnum.EMAIL_CONFIRM
        )

    def teardown_method(self):
        with self.repo.session_factory() as session:
            session.query(Code).delete()
            session.query(User).delete()
            session.commit()

    def _create_user(self, *, unique_fields_suffix: str = "1"):
        return container.user_repo().create(
            entry=RegistrationSchema(
                email=f"testuser{unique_fields_suffix}@email.com",
                username=f"testuser{unique_fields_suffix}",
                password="testpassword",
                re_password="testpassword",
            )
        )

    def test_create(self):
        code = self.repo.create(self.entry)

        assert isinstance(code, Code)
        assert code.type == self.entry.type
        assert code.user_id == self.entry.user_id
        assert code.code == self.entry.code

    def test_get_last_not_exist(self):
        assert (
            self.repo.get_last(self.user.id, type=CodeTypeEnum.RESET_PASSWORD) is None
        )
        assert self.repo.get_last(self.user.id, type=CodeTypeEnum.EMAIL_CONFIRM) is None

        self.repo.create(self.entry)

        assert (
            self.repo.get_last(self.user.id, type=CodeTypeEnum.RESET_PASSWORD) is None
        )
        assert (
            self.repo.get_last(self.user.id, type=CodeTypeEnum.EMAIL_CONFIRM)
            is not None
        )

    def test_get_last_one_exist(self):
        code_email = self.repo.create(self.entry)

        assert (
            self.repo.get_last(self.user.id, type=CodeTypeEnum.RESET_PASSWORD) is None
        )
        assert (
            self.repo.get_last(self.user.id, type=CodeTypeEnum.EMAIL_CONFIRM).id
            == code_email.id
        )

        self.entry.type = CodeTypeEnum.RESET_PASSWORD
        code_password = self.repo.create(self.entry)

        assert (
            self.repo.get_last(self.user.id, type=CodeTypeEnum.EMAIL_CONFIRM).id
            == code_email.id
        )
        assert (
            self.repo.get_last(self.user.id, type=CodeTypeEnum.RESET_PASSWORD).id
            == code_password.id
        )

    def test_get_last_multiple_exist(self):
        code1 = self.repo.create(self.entry)
        assert (
            self.repo.get_last(self.user.id, type=CodeTypeEnum.EMAIL_CONFIRM).id
            == code1.id
        )

        code2 = self.repo.create(self.entry)
        assert (
            self.repo.get_last(self.user.id, type=CodeTypeEnum.EMAIL_CONFIRM).id
            == code2.id
        )

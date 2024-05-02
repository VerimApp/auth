from unittest import mock

from config.di import get_di_test_container
from services.registration import CheckRegistration
from utils.test import ServiceTestMixin


container = get_di_test_container()


class TestCheckRegistration(ServiceTestMixin):
    def setup_method(self):
        self.repo = mock.Mock()
        self.repo.get_by_id.return_value = self.user

        self.context = container.check_registration.override(
            CheckRegistration(repo=self.repo)
        )

    def test_user_not_found(self):
        self.repo.get_by_id.return_value = None
        with self.context:
            result = container.check_registration()(self.user.id)

            assert result is None
            self.repo.delete.assert_not_called()

    def test_email_not_confirmed(self):
        self.user.email_confirmed = False
        with self.context:
            result = container.check_registration()(self.user.id)

            assert result == False
            self.repo.delete.assert_called_once_with(self.user)

    def test_email_confirmed(self):
        self.user.email_confirmed = True
        with self.context:
            result = container.check_registration()(self.user.id)

            assert result
            self.repo.delete.assert_not_called()

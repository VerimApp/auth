from unittest import mock

from config.di import get_di_test_container
from config.mail import SendEmailEntry
from services.codes import SendCode
from services.codes.types import CodeTypeEnum
from services.entries import SendCodeEntry
from schemas import CodeSentSchema
from utils.test import ServiceTestMixin
from utils.email import safe_email_str


container = get_di_test_container()


class TestSendCode(ServiceTestMixin):
    def setup_method(self):
        self.entry = SendCodeEntry(
            email=self.user.email, code="1111", type=CodeTypeEnum.EMAIL_CONFIRM.value
        )

        self.send_email = mock.Mock()

        self.context = container.send_code.override(
            SendCode(send_email=self.send_email)
        )

    def test_send_for_email_confirm(self):
        with self.context:
            code_sent = container.send_code()(entry=self.entry)

            assert isinstance(code_sent, CodeSentSchema)
            assert code_sent.email == self.entry.email
            assert code_sent.message == SendCode.result_map[
                CodeTypeEnum.EMAIL_CONFIRM.value
            ] % {"email": safe_email_str(self.entry.email)}
            self.send_email.assert_called_once_with(
                entry=SendEmailEntry(
                    emails=[self.entry.email],
                    subject=SendCode.subject_map[CodeTypeEnum.EMAIL_CONFIRM.value],
                    message=SendCode.message_map[CodeTypeEnum.EMAIL_CONFIRM.value]
                    % {"code": self.entry.code},
                )
            )

    def test_send_for_password_reset(self):
        self.entry.type = CodeTypeEnum.RESET_PASSWORD.value
        with self.context:
            code_sent = container.send_code()(entry=self.entry)

            assert isinstance(code_sent, CodeSentSchema)
            assert code_sent.email == self.entry.email
            assert code_sent.message == SendCode.result_map[
                CodeTypeEnum.RESET_PASSWORD.value
            ] % {"email": safe_email_str(self.entry.email)}
            self.send_email.assert_called_once_with(
                entry=SendEmailEntry(
                    emails=[self.entry.email],
                    subject=SendCode.subject_map[CodeTypeEnum.RESET_PASSWORD.value],
                    message=SendCode.message_map[CodeTypeEnum.RESET_PASSWORD.value]
                    % {"code": self.entry.code},
                )
            )

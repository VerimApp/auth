import logging
from smtplib import SMTPException
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
from typing import List, Dict

from celery import Celery
from fastapi_mail.config import ConnectionConfig
from fastapi_mail.schemas import MessageSchema, MessageType
from fastapi_mail import FastMail

from config import settings


logger = logging.getLogger("mail")


config = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    USE_CREDENTIALS=True,
    MAIL_SSL_TLS=False,
    MAIL_STARTTLS=True,
)


@dataclass
class SendEmailEntry:
    emails: List[str]
    subject: str
    message: str = ""


class ISendEmail(ABC):
    @abstractmethod
    def __call__(self, entry: SendEmailEntry) -> None: ...


class _ISendEmail(ABC):
    @abstractmethod
    async def __call__(self, entry_dict: Dict) -> None: ...


class SendEmail(ISendEmail):
    def __init__(self, celery_app: Celery):
        self.celery_app = celery_app

    def __call__(self, entry: SendEmailEntry) -> None:
        self._add_task(entry)

    def _add_task(self, entry: SendEmailEntry) -> None:
        self.celery_app.send_task(
            "config.celery.send_email", kwargs={"entry_dict": asdict(entry)}
        )


class _SendEmail(_ISendEmail):
    async def __call__(self, entry_dict: Dict) -> None:
        await self._send_email(entry=self._to_entry(entry_dict))

    def _to_entry(self, entry_dict: Dict) -> SendEmailEntry:
        return SendEmailEntry(**entry_dict)

    async def _send_email(self, entry: SendEmailEntry) -> None:
        try:
            await FastMail(config).send_message(
                message=MessageSchema(
                    recipients=entry.emails,
                    subject=entry.subject,
                    body=entry.message,
                    subtype=MessageType.plain,
                )
            )
        except SMTPException as e:
            logger.critical(
                f"Failed to send email - {str(e)}",
                extra={"entry": asdict(entry)},
                exc_info=e,
            )
            raise

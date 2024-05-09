import logging
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
from typing import List

from celery import Celery


logger = logging.getLogger("mail")


@dataclass
class SendEmailEntry:
    emails: List[str]
    subject: str
    message: str = ""


class ISendEmail(ABC):
    @abstractmethod
    def __call__(self, entry: SendEmailEntry) -> None: ...


class SendEmail(ISendEmail):
    def __init__(self, celery_app: Celery):
        self.celery_app = celery_app

    def __call__(self, entry: SendEmailEntry) -> None:
        self._add_task(entry)

    def _add_task(self, entry: SendEmailEntry) -> None:
        self.celery_app.send_task(
            "config.celery.send_email", kwargs={"entry_dict": asdict(entry)}
        )

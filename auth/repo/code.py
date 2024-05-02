from dataclasses import asdict

from services.codes.types import CodeTypeEnum, CodeType
from services.entries import CreateCodeEntry
from services.codes.repo import ICodeRepo
from models.codes import Code
from utils.decorators import handle_orm_error


class CodeRepo(ICodeRepo):
    model = Code

    @handle_orm_error
    def create(self, entry: CreateCodeEntry) -> CodeType:
        if not isinstance(entry.type, str):
            entry.type = entry.type.value
        code = self.model(**asdict(entry))
        self.session.add(code)
        return code

    @handle_orm_error
    def get_last(self, user_id: int, type: CodeTypeEnum) -> CodeType | None:
        return (
            self.session.query(self.model)
            .filter(Code.user_id == user_id, Code.type == type.value)
            .order_by(Code.created_at.desc())
            .first()
        )

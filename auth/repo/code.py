from dataclasses import asdict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.codes.types import CodeTypeEnum
from services.entries import CreateCodeEntry
from services.codes.repo import ICodeRepo
from models.codes import Code
from utils.decorators import handle_orm_error, row_to_model


class CodeRepo(ICodeRepo):
    model = Code

    @handle_orm_error
    async def create(self, session: AsyncSession, entry: CreateCodeEntry) -> Code:
        if not isinstance(entry.type, str):
            entry.type = entry.type.value
        code = self.model(**asdict(entry))
        session.add(code)
        return code

    @handle_orm_error
    @row_to_model()
    async def get_last(
        self, session: AsyncSession, user_id: int, type: CodeTypeEnum
    ) -> Code | None:
        result = await session.execute(
            select(self.model)
            .filter(self.model.user_id == user_id, self.model.type == type.value)
            .order_by(self.model.created_at.desc())
        )
        return result.first()

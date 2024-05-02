from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from typing import List

from config.grpc import GRPCConnection
from utils.decorators import handle_grpc_response_error

from auth_grpc_typed import Empty


@dataclass
class CreatePublicationRequest:
    user_id: int
    url: str


@dataclass
class PublicationResponse:
    id: int
    url: str
    type: str
    believed_count: int
    disbelieved_count: int
    created_at: str
    believed: bool
    detail: str | None


@dataclass
class VoteRequest:
    user_id: int
    publication_id: int
    believed: bool


@dataclass
class PaginationRequest:
    user_id: int
    page: int
    size: int


@dataclass
class PublicationsSelectionResponse:
    items: List[PublicationResponse]
    total: int
    page: int
    size: int
    pages: int
    detail: str | None


class IPublisherStub(ABC):
    @abstractmethod
    async def publications_create(
        self, request: CreatePublicationRequest
    ) -> PublicationResponse: ...

    @abstractmethod
    async def publications_selection(
        self, request: PaginationRequest
    ) -> PublicationsSelectionResponse: ...

    @abstractmethod
    async def publications_vote(self, request: VoteRequest) -> Empty: ...


class PublisherStub(IPublisherStub):
    def __init__(self, connection: GRPCConnection) -> None:
        self.connection = connection

    @handle_grpc_response_error
    async def publications_create(
        self, request: CreatePublicationRequest
    ) -> PublicationResponse:
        from publisher_pb2 import CreatePublicationRequest as _CreatePublicationRequest

        response = await self.connection.stub.publications_create(
            _CreatePublicationRequest(**asdict(request))
        )
        return PublicationResponse(
            id=response.id,
            url=response.url,
            type=response.type,
            believed_count=response.believed_count,
            disbelieved_count=response.disbelieved_count,
            created_at=response.created_at,
            believed=response.believed,
            detail=response.detail,
        )

    @handle_grpc_response_error
    async def publications_selection(
        self, request: PaginationRequest
    ) -> PublicationsSelectionResponse:
        from publisher_pb2 import PaginationRequest as _PaginationRequest

        response = await self.connection.stub.publications_selection(
            _PaginationRequest(**asdict(request))
        )
        return PublicationsSelectionResponse(
            items=[
                PublicationResponse(
                    id=publication.id,
                    url=publication.url,
                    type=publication.type,
                    believed_count=publication.believed_count,
                    disbelieved_count=publication.disbelieved_count,
                    created_at=publication.created_at,
                    believed=publication.believed,
                    detail=publication.detail,
                )
                for publication in response.items
            ],
            total=response.total,
            page=response.page,
            size=response.size,
            pages=response.pages,
            detail=response.detail,
        )

    @handle_grpc_response_error
    async def publications_vote(self, request: VoteRequest) -> Empty:
        from publisher_pb2 import VoteRequest as _VoteRequest

        response = await self.connection.stub.publications_vote(
            _VoteRequest(**asdict(request))
        )
        return Empty(detail=response.detail)

# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: publisher.proto
# Protobuf Python Version: 4.25.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import protobufs.compiled.auth_pb2 as auth__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x0fpublisher.proto\x12\tpublisher\x1a\nauth.proto"8\n\x18\x43reatePublicationRequest\x12\x0f\n\x07user_id\x18\x01'
    b" \x01(\x05\x12\x0b\n\x03url\x18\x02"
    b' \x01(\t"\xb5\x01\n\x13PublicationResponse\x12\n\n\x02id\x18\x01'
    b" \x01(\x05\x12\x0b\n\x03url\x18\x02 \x01(\t\x12\x0c\n\x04type\x18\x03"
    b" \x01(\t\x12\x16\n\x0e\x62\x65lieved_count\x18\x04"
    b" \x01(\x05\x12\x19\n\x11\x64isbelieved_count\x18\x05"
    b" \x01(\x05\x12\x12\n\ncreated_at\x18\x06"
    b" \x01(\t\x12\x10\n\x08\x62\x65lieved\x18\x07"
    b" \x01(\x08\x12\x13\n\x06\x64\x65tail\x18\x08"
    b' \x01(\tH\x00\x88\x01\x01\x42\t\n\x07_detail"H\n\x0bVoteRequest\x12\x0f\n\x07user_id\x18\x01'
    b" \x01(\x05\x12\x16\n\x0epublication_id\x18\x02"
    b" \x01(\x05\x12\x10\n\x08\x62\x65lieved\x18\x03"
    b' \x01(\x08"@\n\x11PaginationRequest\x12\x0f\n\x07user_id\x18\x01'
    b" \x01(\x05\x12\x0c\n\x04page\x18\x02 \x01(\x05\x12\x0c\n\x04size\x18\x03"
    b' \x01(\x05"\xa8\x01\n\x1dPublicationsSelectionResponse\x12-\n\x05items\x18\x01'
    b" \x03(\x0b\x32\x1e.publisher.PublicationResponse\x12\r\n\x05total\x18\x02"
    b" \x01(\x05\x12\x0c\n\x04page\x18\x03 \x01(\x05\x12\x0c\n\x04size\x18\x04"
    b" \x01(\x05\x12\r\n\x05pages\x18\x05 \x01(\x05\x12\x13\n\x06\x64\x65tail\x18\x06"
    b" \x01(\tH\x00\x88\x01\x01\x42\t\n\x07_detail2\x83\x02\n\tPublisher\x12Z\n\x13publications_create\x12#.publisher.CreatePublicationRequest\x1a\x1e.publisher.PublicationResponse\x12`\n\x16publications_selection\x12\x1c.publisher.PaginationRequest\x1a(.publisher.PublicationsSelectionResponse\x12\x38\n\x11publications_vote\x12\x16.publisher.VoteRequest\x1a\x0b.auth.Emptyb\x06proto3"
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "publisher_pb2", _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    _globals["_CREATEPUBLICATIONREQUEST"]._serialized_start = 42
    _globals["_CREATEPUBLICATIONREQUEST"]._serialized_end = 98
    _globals["_PUBLICATIONRESPONSE"]._serialized_start = 101
    _globals["_PUBLICATIONRESPONSE"]._serialized_end = 282
    _globals["_VOTEREQUEST"]._serialized_start = 284
    _globals["_VOTEREQUEST"]._serialized_end = 356
    _globals["_PAGINATIONREQUEST"]._serialized_start = 358
    _globals["_PAGINATIONREQUEST"]._serialized_end = 422
    _globals["_PUBLICATIONSSELECTIONRESPONSE"]._serialized_start = 425
    _globals["_PUBLICATIONSSELECTIONRESPONSE"]._serialized_end = 593
    _globals["_PUBLISHER"]._serialized_start = 596
    _globals["_PUBLISHER"]._serialized_end = 855
# @@protoc_insertion_point(module_scope)

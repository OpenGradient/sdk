# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: infer.proto
# Protobuf Python Version: 5.27.2
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    27,
    2,
    '',
    'infer.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0binfer.proto\x12\tinference\"[\n\x10InferenceRequest\x12\n\n\x02tx\x18\x01 \x01(\t\x12;\n\x10image_generation\x18\x06 \x01(\x0b\x32!.inference.ImageGenerationRequest\"u\n\x16ImageGenerationRequest\x12\r\n\x05model\x18\x01 \x01(\t\x12\x0e\n\x06prompt\x18\x02 \x01(\t\x12\x13\n\x06height\x18\x03 \x01(\x05H\x00\x88\x01\x01\x12\x12\n\x05width\x18\x04 \x01(\x05H\x01\x88\x01\x01\x42\t\n\x07_heightB\x08\n\x06_width\"\x1b\n\rInferenceTxId\x12\n\n\x02id\x18\x01 \x01(\t\"\xd4\x01\n\x0fInferenceStatus\x12\x31\n\x06status\x18\x01 \x01(\x0e\x32!.inference.InferenceStatus.Status\x12\x1a\n\rerror_message\x18\x02 \x01(\tH\x00\x88\x01\x01\"`\n\x06Status\x12\x16\n\x12STATUS_UNSPECIFIED\x10\x00\x12\x16\n\x12STATUS_IN_PROGRESS\x10\x01\x12\x14\n\x10STATUS_COMPLETED\x10\x02\x12\x10\n\x0cSTATUS_ERROR\x10\x03\x42\x10\n\x0e_error_message\"\xa4\x01\n\x0fInferenceResult\x12\x43\n\x17image_generation_result\x18\x05 \x01(\x0b\x32\".inference.ImageGenerationResponse\x12\x17\n\npublic_key\x18\x07 \x01(\tH\x00\x88\x01\x01\x12\x16\n\tsignature\x18\x08 \x01(\tH\x01\x88\x01\x01\x42\r\n\x0b_public_keyB\x0c\n\n_signature\"-\n\x17ImageGenerationResponse\x12\x12\n\nimage_data\x18\x01 \x01(\x0c\x32\xf6\x01\n\x10InferenceService\x12J\n\x11RunInferenceAsync\x12\x1b.inference.InferenceRequest\x1a\x18.inference.InferenceTxId\x12J\n\x12GetInferenceStatus\x12\x18.inference.InferenceTxId\x1a\x1a.inference.InferenceStatus\x12J\n\x12GetInferenceResult\x12\x18.inference.InferenceTxId\x1a\x1a.inference.InferenceResultb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'infer_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_INFERENCEREQUEST']._serialized_start=26
  _globals['_INFERENCEREQUEST']._serialized_end=117
  _globals['_IMAGEGENERATIONREQUEST']._serialized_start=119
  _globals['_IMAGEGENERATIONREQUEST']._serialized_end=236
  _globals['_INFERENCETXID']._serialized_start=238
  _globals['_INFERENCETXID']._serialized_end=265
  _globals['_INFERENCESTATUS']._serialized_start=268
  _globals['_INFERENCESTATUS']._serialized_end=480
  _globals['_INFERENCESTATUS_STATUS']._serialized_start=366
  _globals['_INFERENCESTATUS_STATUS']._serialized_end=462
  _globals['_INFERENCERESULT']._serialized_start=483
  _globals['_INFERENCERESULT']._serialized_end=647
  _globals['_IMAGEGENERATIONRESPONSE']._serialized_start=649
  _globals['_IMAGEGENERATIONRESPONSE']._serialized_end=694
  _globals['_INFERENCESERVICE']._serialized_start=697
  _globals['_INFERENCESERVICE']._serialized_end=943
# @@protoc_insertion_point(module_scope)

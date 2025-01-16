# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""


import grpc

from . import infer_pb2 as infer__pb2

GRPC_GENERATED_VERSION = "1.66.2"
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower

    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f"The grpc package installed is at version {GRPC_VERSION},"
        + " but the generated code in infer_pb2_grpc.py depends on"
        + f" grpcio>={GRPC_GENERATED_VERSION}."
        + f" Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}"
        + f" or downgrade your generated code using grpcio-tools<={GRPC_VERSION}."
    )


class InferenceServiceStub(object):
    """The inference service definition"""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.RunInferenceAsync = channel.unary_unary(
            "/inference.InferenceService/RunInferenceAsync",
            request_serializer=infer__pb2.InferenceRequest.SerializeToString,
            response_deserializer=infer__pb2.InferenceTxId.FromString,
            _registered_method=True,
        )
        self.GetInferenceStatus = channel.unary_unary(
            "/inference.InferenceService/GetInferenceStatus",
            request_serializer=infer__pb2.InferenceTxId.SerializeToString,
            response_deserializer=infer__pb2.InferenceStatus.FromString,
            _registered_method=True,
        )
        self.GetInferenceResult = channel.unary_unary(
            "/inference.InferenceService/GetInferenceResult",
            request_serializer=infer__pb2.InferenceTxId.SerializeToString,
            response_deserializer=infer__pb2.InferenceResult.FromString,
            _registered_method=True,
        )


class InferenceServiceServicer(object):
    """The inference service definition"""

    def RunInferenceAsync(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def GetInferenceStatus(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def GetInferenceResult(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")


def add_InferenceServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
        "RunInferenceAsync": grpc.unary_unary_rpc_method_handler(
            servicer.RunInferenceAsync,
            request_deserializer=infer__pb2.InferenceRequest.FromString,
            response_serializer=infer__pb2.InferenceTxId.SerializeToString,
        ),
        "GetInferenceStatus": grpc.unary_unary_rpc_method_handler(
            servicer.GetInferenceStatus,
            request_deserializer=infer__pb2.InferenceTxId.FromString,
            response_serializer=infer__pb2.InferenceStatus.SerializeToString,
        ),
        "GetInferenceResult": grpc.unary_unary_rpc_method_handler(
            servicer.GetInferenceResult,
            request_deserializer=infer__pb2.InferenceTxId.FromString,
            response_serializer=infer__pb2.InferenceResult.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler("inference.InferenceService", rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers("inference.InferenceService", rpc_method_handlers)


# This class is part of an EXPERIMENTAL API.
class InferenceService(object):
    """The inference service definition"""

    @staticmethod
    def RunInferenceAsync(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/inference.InferenceService/RunInferenceAsync",
            infer__pb2.InferenceRequest.SerializeToString,
            infer__pb2.InferenceTxId.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True,
        )

    @staticmethod
    def GetInferenceStatus(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/inference.InferenceService/GetInferenceStatus",
            infer__pb2.InferenceTxId.SerializeToString,
            infer__pb2.InferenceStatus.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True,
        )

    @staticmethod
    def GetInferenceResult(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/inference.InferenceService/GetInferenceResult",
            infer__pb2.InferenceTxId.SerializeToString,
            infer__pb2.InferenceResult.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True,
        )

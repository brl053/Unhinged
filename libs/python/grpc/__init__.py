"""
Unhinged gRPC Client Library

Cross-project gRPC client utilities that work with generated protobuf clients.
"""

from .client_factory import (
    GrpcClientFactory,
    create_audio_client,
    create_llm_client,
    create_vision_client,
)

__all__ = [
    'GrpcClientFactory',
    'create_audio_client',
    'create_llm_client',
    'create_vision_client'
]

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from thenewboston.constants.errors import ERROR
from thenewboston.constants.network import CONFIRMATION_VALIDATOR, HEAD_HASH_LENGTH

from thenewboston_validator.cache_tools.queued_confirmation_blocks import get_queued_confirmation_block
from thenewboston_validator.cache_tools.valid_confirmation_blocks import get_valid_confirmation_block
from thenewboston_validator.decorators.nodes import is_signed_by_primary_validator
from thenewboston_validator.self_configurations.helpers.self_configuration import get_self_configuration
from thenewboston_validator.tasks.confirmation_block_queue import process_confirmation_block_queue
from ..serializers.confirmation_block import ConfirmationBlockSerializerCreate


class ConfirmationBlockViewSet(ViewSet):
    """
    Confirmation block

    ---
    create:
      description: Add a confirmation block to the queue
    queued:
      description: View individual queued confirmation block
    valid:
      description: View individual valid confirmation block
    """

    @staticmethod
    @is_signed_by_primary_validator
    def create(request):
        self_configuration = get_self_configuration(exception_class=RuntimeError)

        if self_configuration.node_type != CONFIRMATION_VALIDATOR:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

        serializer = ConfirmationBlockSerializerCreate(data=request.data['message'])

        serializer.is_valid(raise_exception=True)
        serializer.save()
        process_confirmation_block_queue.delay()

        return Response({}, status=status.HTTP_201_CREATED)

    @staticmethod
    def get_block(block_identifier, block_getter):
        if len(block_identifier) != HEAD_HASH_LENGTH:
            return Response(
                {ERROR: f'block_identifier must be {HEAD_HASH_LENGTH} characters long'},
                status=status.HTTP_403_FORBIDDEN
            )

        confirmation_block = block_getter(block_identifier=block_identifier)

        if not confirmation_block:
            return Response({}, status=status.HTTP_404_NOT_FOUND)

        return Response(confirmation_block)

    @staticmethod
    @action(methods=['get'], detail=True)
    def queued(request, pk):
        self_configuration = get_self_configuration(exception_class=RuntimeError)

        if self_configuration.node_type != CONFIRMATION_VALIDATOR:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

        return ConfirmationBlockViewSet.get_block(pk, get_queued_confirmation_block)

    @staticmethod
    @action(methods=['get'], detail=True)
    def valid(request, pk):
        return ConfirmationBlockViewSet.get_block(pk, get_valid_confirmation_block)

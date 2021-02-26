from django.http import Http404
from django.utils.decorators import classonlymethod
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.viewsets import ViewSet
from thenewboston.constants.network import CONFIRMATION_VALIDATOR

from thenewboston_validator.decorators.nodes import is_self_signed_message
from thenewboston_validator.self_configurations.helpers.self_configuration import get_self_configuration
from ..helpers import get_clean_info
from ..serializers.clean import CleanSerializer


class CleanViewSet(ViewSet):
    serializer_class = CleanSerializer

    def initial(self, request, *args, **kwargs):
        if get_self_configuration(exception_class=RuntimeError).node_type != CONFIRMATION_VALIDATOR:
            raise Http404
        return super().initial(request, *args, **kwargs)

    @classonlymethod
    def as_view(cls, actions=None, **kwargs):
        return super().as_view(
            actions={
                'get': 'clean_status',
                'post': 'create'
            },
            **kwargs
        )

    @staticmethod
    def clean_status(request):
        return Response(
            get_clean_info(),
            status=HTTP_200_OK
        )

    @is_self_signed_message
    def create(self, request):
        serializer = self.serializer_class(
            data={
                **request.data['message']
            },
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            get_clean_info(),
            status=HTTP_200_OK
        )

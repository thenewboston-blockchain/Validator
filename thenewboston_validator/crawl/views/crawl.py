from django.http import Http404
from django.utils.decorators import classonlymethod
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.viewsets import ViewSet
from thenewboston.constants.network import CONFIRMATION_VALIDATOR

from thenewboston_validator.decorators.nodes import is_self_signed_message
from thenewboston_validator.self_configurations.helpers.self_configuration import get_self_configuration
from ..helpers import get_crawl_info
from ..serializers.crawl import CrawlSerializer


class CrawlViewSet(ViewSet):
    serializer_class = CrawlSerializer

    def initial(self, request, *args, **kwargs):
        if get_self_configuration(exception_class=RuntimeError).node_type != CONFIRMATION_VALIDATOR:
            raise Http404
        return super().initial(request, *args, **kwargs)

    @classonlymethod
    def as_view(cls, actions=None, **kwargs):
        return super().as_view(
            actions={
                'get': 'crawl_status',
                'post': 'create'
            },
            **kwargs
        )

    @staticmethod
    def crawl_status(request):
        return Response(
            get_crawl_info(),
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
            get_crawl_info(),
            status=HTTP_200_OK
        )

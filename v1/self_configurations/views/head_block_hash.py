from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.views import APIView

from v1.cache_tools.cache_keys import HEAD_BLOCK_HASH


# head_block_hash
class HeadBlockHashDetail(APIView):

    @staticmethod
    def get(request):
        """
        description: Get head block hash
        """

        return Response(cache.get(HEAD_BLOCK_HASH))

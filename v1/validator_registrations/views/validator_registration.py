from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from v1.decorators.nodes import is_signed_message
from ..models.validator_registration import ValidatorRegistration
from ..serializers.validator_registration import ValidatorRegistrationSerializer, ValidatorRegistrationSerializerCreate


# validator_registrations
class ValidatorRegistrationView(APIView):

    @staticmethod
    def get(request):
        """
        description: List validator registrations
        """

        validator_registrations = ValidatorRegistration.objects.all()
        return Response(ValidatorRegistrationSerializer(validator_registrations, many=True).data)

    @staticmethod
    @is_signed_message
    def post(request):
        """
        description: Register a validator
        """

        serializer = ValidatorRegistrationSerializerCreate(
            data={
                **request.data['message'],
                'signing_nid': request.data['node_identifier']
            },
            context={'request': request}
        )

        if serializer.is_valid():
            validator_registration = serializer.save()
            return Response(
                ValidatorRegistrationSerializer(validator_registration).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

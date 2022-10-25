import json

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from pyDataverse.api import NativeApi
from pyDataverse.models import Dataset
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from main.utils import format_form_response_to_dataset


class TypeformSubmissions(APIView):
    permission_classes = [AllowAny]

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        body = request.data
        received_signature = request.headers.get("typeform-signature")

        if not received_signature:
            return Response(status=status.HTTP_403_FORBIDDEN)

        if received_signature != settings.TYPEFORM_CLIENT_SECRET:
            return Response("Invalid signature", status=status.HTTP_403_FORBIDDEN)

        api = NativeApi(settings.DATAVERSE_BASE_URL, settings.DATAVERSE_API_TOKEN)
        ds = Dataset()
        ds.from_json(json.dumps(format_form_response_to_dataset(body)))

        resp = api.create_dataset(settings.DATAVERSE_PARENT_ALIAS, ds.json())
        return Response(
            data=resp.json(), status=status.HTTP_200_OK if resp.status_code in (200, 201)
            else status.HTTP_400_BAD_REQUEST
        )

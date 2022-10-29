import json

from fastapi import FastAPI, Body, Request, status, HTTPException
from pyDataverse.api import NativeApi
from pyDataverse.models import Dataset

from local_secrets import *
from utils import format_form_response_to_dataset

app = FastAPI()


@app.post("/submit_dataset_form")
def submit_dataset_form(request: Request, input_data: dict = Body()):
    received_signature = request.headers.get("typeform-signature")

    if not received_signature or received_signature != SECRETS_TYPEFORM_CLIENT_SECRET:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid signature token.")

    required_fields = ["Назва джерела", "Автор джерела", "Опис українською"]
    for field_ in required_fields:
        if field_ not in input_data.keys():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Field '{field_}' is required.")

    api = NativeApi(SECRETS_DATAVERSE_BASE_URL, SECRETS_DATAVERSE_API_TOKEN)
    ds = Dataset()
    ds.from_json(json.dumps(format_form_response_to_dataset(input_data)))

    resp = api.create_dataset(SECRETS_DATAVERSE_PARENT_ALIAS, ds.json())
    return resp.json()

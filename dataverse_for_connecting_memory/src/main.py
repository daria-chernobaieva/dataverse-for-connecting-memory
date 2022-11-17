import json

from fastapi import FastAPI, Body, Request, status, HTTPException, Response
from pyDataverse.api import NativeApi
from pyDataverse.models import Dataset, Datafile

from const import *
from local_secrets import *
from utils import format_form_response_to_dataset, MyHTMLParser

app = FastAPI()


@app.post("/submit_dataset_form")
def submit_dataset_form(request: Request, response: Response, input_data: dict = Body()):
    received_signature = request.headers.get("typeform-signature")

    if not received_signature or received_signature != SECRETS_TYPEFORM_CLIENT_SECRET:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid signature token.")

    required_fields = [TITLE, AUTHOR_NAME, DS_DESCRIPTION_VALUE_UA]
    for field_ in required_fields:
        if field_ not in input_data.keys():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Field '{field_}' is required.")

    api = NativeApi(SECRETS_DATAVERSE_BASE_URL, SECRETS_DATAVERSE_API_TOKEN)
    ds = Dataset()
    ds.from_json(json.dumps(format_form_response_to_dataset(input_data)))

    resp = api.create_dataset(SECRETS_DATAVERSE_PARENT_ALIAS, ds.json())

    if resp.status_code != status.HTTP_201_CREATED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=resp.json().get("message"))

    # parser = MyHTMLParser()
    # parser.feed(input_data.get(FILES))
    #
    # for link in parser.links:
    #     df = Datafile()
    #     ds_pid = resp.json().get("data").get("persistentId")
        # df_filename =
        # df.set({"pid": ds_pid, "filename": df_filename})
        # resp = api.upload_datafile(ds_pid, df_filename, df.json())

    return resp.json().get("data")

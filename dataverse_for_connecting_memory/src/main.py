import json
from tempfile import NamedTemporaryFile

from fastapi import FastAPI, Body, Request, status, HTTPException, Response
from pyDataverse.api import NativeApi
from pyDataverse.models import Dataset, Datafile
from apiclient.discovery import build
import sentry_sdk
from sentry_sdk.integrations.starlette import StarletteIntegration
from sentry_sdk.integrations.fastapi import FastApiIntegration

from const import *
from local_secrets import *
from utils import format_form_response_to_dataset, MyHTMLParser


sentry_sdk.init(
    dsn=SECRETS_SENTRY_DSN,
    traces_sample_rate=1.0,
    integrations=[
        StarletteIntegration(transaction_style="endpoint"),
        FastApiIntegration(transaction_style="endpoint"),
    ],
)

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

    # Files upload
    parser = MyHTMLParser()
    parser.feed(input_data.get(FILES, ""))
    ds_pid = resp.json().get("data").get("persistentId")

    if len(parser.links) > 0:
        try:
            service = build("drive", "v3", developerKey=SECRETS_GOOGLE_API_KEY)
            for link in parser.links:
                file_id = link.split("https://drive.google.com/open?id=")[-1]
                metadata = service.files().get(fileId=file_id).execute()
                df_filename = metadata.get("name")
                df = Datafile(data={"pid": ds_pid, "filename": df_filename})

                file_content = service.files().get_media(fileId=file_id).execute()
                with NamedTemporaryFile(
                    suffix=f".{metadata.get('mimeType').split('/')[-1]}",
                    prefix=f"{df_filename.split('.')[0]}"
                ) as pdf:
                    pdf.write(file_content)
                    api.upload_datafile(ds_pid, pdf.name, df.json())
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.get("/sentry-debug")
def trigger_error():
    division_by_zero = 1 / 0

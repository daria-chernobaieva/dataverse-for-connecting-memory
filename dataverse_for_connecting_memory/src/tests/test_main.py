import json
from unittest import mock
from fastapi import status
from fastapi.testclient import TestClient

from src.const import TITLE, AUTHOR_NAME, DS_DESCRIPTION_VALUE_UA, FILES
from src.main import app
from src.local_secrets import SECRETS_TYPEFORM_CLIENT_SECRET, SECRETS_DATAVERSE_PARENT_ALIAS, SECRETS_GOOGLE_API_KEY
from src.utils import format_form_response_to_dataset

client = TestClient(app)


@mock.patch("pyDataverse.api.NativeApi.create_dataset")
@mock.patch("pyDataverse.models.Dataset.from_json")
@mock.patch("pyDataverse.models.Dataset.json")
def test_submit_dataset_form(dataset_to_json_mock, dataset_from_json_mock, create_dataset_mock):
    # no input data => failure, no processable entity
    response = client.post("/submit_dataset_form")

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    create_dataset_mock.assert_not_called()

    # add input data, no signature => failure, not permitted
    input_data = {"test_key": "test_value"}
    response = client.post("/submit_dataset_form", json=input_data)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "Invalid signature token."}
    dataset_from_json_mock.assert_not_called()
    create_dataset_mock.assert_not_called()

    # Wrong signature => failure, not permitted
    headers = {"typeform-signature": "test"}
    response = client.post("/submit_dataset_form", json=input_data, headers=headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "Invalid signature token."}
    dataset_from_json_mock.assert_not_called()
    create_dataset_mock.assert_not_called()

    # Right signature, required fields aren't there => failure, validation error
    headers["typeform-signature"] = SECRETS_TYPEFORM_CLIENT_SECRET
    response = client.post("/submit_dataset_form", json=input_data, headers=headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": f"Field '{TITLE}' is required."}
    dataset_from_json_mock.assert_not_called()
    create_dataset_mock.assert_not_called()

    # Required fields are there => failure on Dataverse side
    required_fields = [TITLE, AUTHOR_NAME, DS_DESCRIPTION_VALUE_UA]
    input_data = {
        field_: "test" for field_ in required_fields
    }
    create_dataset_mock.return_value.status_code = status.HTTP_403_FORBIDDEN
    expected_success_result = create_dataset_mock.return_value.json.return_value = {
        "message": "Dataverse Error"
    }
    response = client.post("/submit_dataset_form", json=input_data, headers=headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": expected_success_result["message"]}

    dataset_from_json_mock.assert_called_once_with(
        json.dumps(format_form_response_to_dataset(input_data))
    )
    create_dataset_mock.assert_called_once_with(SECRETS_DATAVERSE_PARENT_ALIAS, dataset_to_json_mock.return_value)

    # failure on Dataverse side
    dataset_from_json_mock.reset_mock()
    create_dataset_mock.reset_mock()
    create_dataset_mock.return_value.status_code = status.HTTP_201_CREATED
    create_dataset_mock.return_value.json.return_value = {
        "data": {"id": 1, "persistentId": "doi/smth"}
    }

    response = client.post("/submit_dataset_form", json=input_data, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() is None
    dataset_from_json_mock.assert_called_once_with(
        json.dumps(format_form_response_to_dataset(input_data))
    )
    create_dataset_mock.assert_called_once_with(SECRETS_DATAVERSE_PARENT_ALIAS, dataset_to_json_mock.return_value)


@mock.patch("pyDataverse.api.NativeApi.create_dataset")
@mock.patch("src.utils.MyHTMLParser.__init__")
@mock.patch("src.main.build")
@mock.patch("pyDataverse.models.Datafile.__init__", return_value=None)
@mock.patch("pyDataverse.models.Datafile.json")
@mock.patch("pyDataverse.api.NativeApi.upload_datafile")
def test_submit_dataset_form_with_file_uploads(upload_datafile_mock, datafile_to_json_mock, datafile_mock, service_mock,
                                               html_parser_mock, create_dataset_mock):
    headers = {"typeform-signature": SECRETS_TYPEFORM_CLIENT_SECRET}
    required_fields = [TITLE, AUTHOR_NAME, DS_DESCRIPTION_VALUE_UA]
    input_data = {
        field_: "test" for field_ in required_fields
    }

    file_ids = ["test1", "test2"]
    links = [f"https://drive.google.com/open?id={file_id}" for file_id in file_ids]
    input_data.update({
        FILES: "".join([f"<a href='{link}'></a>" for link in links]),
    })

    create_dataset_mock.return_value.status_code = status.HTTP_201_CREATED
    persistentId = "doi/smth"
    create_dataset_mock.return_value.json.return_value = {
        "data": {"id": 1, "persistentId": persistentId}
    }

    html_parser_mock.return_value.links = links

    # success
    service_mock.reset_mock()
    service_files = service_mock.return_value.files.return_value
    expected_metadata = service_files.get.return_value.execute.return_value = {
        "name": "test.pdf", "mimeType": "application/pdf"
    }
    service_files.get_media.return_value.execute.return_value = b"test pdf"
    upload_datafile_mock.return_value = {}

    response = client.post("/submit_dataset_form", json=input_data, headers=headers)
    service_mock.assert_called_once_with("drive", "v3", developerKey=SECRETS_GOOGLE_API_KEY)

    service_files.get.assert_called()
    service_files.get_media.assert_called()

    datafile_mock.assert_called_with(data={"pid": persistentId, "filename": expected_metadata["name"]})
    upload_datafile_mock.assert_called_with(persistentId, mock.ANY, datafile_to_json_mock.return_value)

    assert response.status_code == status.HTTP_200_OK

    # failure
    message = "Google Client Error"
    service_mock.side_effect = Exception(message)
    response = client.post("/submit_dataset_form", json=input_data, headers=headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": message}

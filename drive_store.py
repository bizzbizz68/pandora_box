import io, json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

SCOPES = ["https://www.googleapis.com/auth/drive"]

creds = Credentials.from_service_account_file(
    "credentials.json",
    scopes=SCOPES
)

drive = build("drive", "v3", credentials=creds)

FILE_NAME = "chat_room.json"


def _find_file():
    res = drive.files().list(
        q=f"name='{FILE_NAME}' and trashed=false",
        fields="files(id)"
    ).execute()
    files = res.get("files", [])
    return files[0]["id"] if files else None


def _create_file():
    media = MediaIoBaseUpload(
        io.BytesIO(b"{}"),
        mimetype="application/json"
    )
    file = drive.files().create(
        body={"name": FILE_NAME},
        media_body=media,
        fields="id"
    ).execute()
    return file["id"]


def get_file_id():
    return _find_file() or _create_file()


def load_data():
    file_id = get_file_id()
    request = drive.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    MediaIoBaseDownload(fh, request).next_chunk()
    fh.seek(0)
    return json.load(fh)


def save_data(data):
    file_id = get_file_id()
    media = MediaIoBaseUpload(
        io.BytesIO(json.dumps(data).encode()),
        mimetype="application/json",
        resumable=True
    )
    drive.files().update(
        fileId=file_id,
        media_body=media
    ).execute()

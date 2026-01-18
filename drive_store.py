import io, json, os, sys
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDS_PATH = os.path.join(BASE_DIR, "credentials.json")

SCOPES = ["https://www.googleapis.com/auth/drive"]
FILE_NAME = "chat_room.json"

# 🔴 BẮT BUỘC: folder ID của bố (lấy trên URL Drive)
FOLDER_ID = "DÁN_FOLDER_ID_VÀO_ĐÂY"


def log(msg):
    print(f"[DRIVE] {msg}", flush=True)


# ===== AUTH =====
log(f"Loading creds from: {CREDS_PATH}")
creds = Credentials.from_service_account_file(
    CREDS_PATH,
    scopes=SCOPES
)
drive = build("drive", "v3", credentials=creds)


# ===== DRIVE OPS =====
def find_file():
    log("Finding file...")
    res = drive.files().list(
        q=f"name='{FILE_NAME}' and trashed=false",
        fields="files(id, parents)"
    ).execute()
    files = res.get("files", [])
    log(f"Found files: {files}")
    return files[0]["id"] if files else None


def create_file():
    log("Creating file on Drive...")
    media = MediaIoBaseUpload(
        io.BytesIO(b"{}"),
        mimetype="application/json"
    )
    file = drive.files().create(
        body={
            "name": FILE_NAME,
            "parents": [FOLDER_ID]
        },
        media_body=media,
        fields="id"
    ).execute()
    log(f"Created file id={file['id']}")
    return file["id"]


def get_file_id():
    fid = find_file()
    if fid:
        return fid
    return create_file()


def load_data():
    fid = get_file_id()
    log("Loading data...")
    request = drive.files().get_media(fileId=fid)
    fh = io.BytesIO()
    MediaIoBaseDownload(fh, request).next_chunk()
    fh.seek(0)
    return json.load(fh)


def save_data(data):
    fid = get_file_id()
    log("Saving data...")
    media = MediaIoBaseUpload(
        io.BytesIO(json.dumps(data).encode()),
        mimetype="application/json",
        resumable=True
    )
    drive.files().update(
        fileId=fid,
        media_body=media
    ).execute()

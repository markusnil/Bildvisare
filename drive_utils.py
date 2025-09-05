import os
import io

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive"]


def get_service(credentials_file="credentials.json", token_file="token.json"):
    """Authenticate and return a Google Drive service instance."""
    creds = None

    # Load stored token if it exists
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    # Refresh or request new token if needed
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")

        # Save new token
        with open(token_file, "w") as token:
            token.write(creds.to_json())

    return build("drive", "v3", credentials=creds)


def upload_file(service, folder_id, file_path, mime_type="application/octet-stream"):
    """Upload a file to Google Drive inside a specific folder."""
    file_metadata = {
        "name": os.path.basename(file_path),
        "parents": [folder_id]
    }
    media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id, name"
    ).execute()
    print(f"✅ Uploaded {file.get('name')} (ID: {file.get('id')})")
    return file.get("id")


def download_file(service, file_id, filename, dest_dir="."):
    """Download a binary file from Google Drive by ID."""
    file_metadata = service.files().get(fileId=file_id, fields="mimeType, name").execute()
    mime_type = file_metadata.get("mimeType")

    if mime_type.startswith("application/vnd.google-apps"):
        print(f"⏭️ Skipping {filename} (Google Docs type)")
        return

    file_path = os.path.join(dest_dir, filename)
    if os.path.exists(file_path):
        print(f"⚠️ File {file_path} already exists! Skipping!")
        return

    request = service.files().get_media(fileId=file_id)
    print(file_path)
    fh = io.FileIO(file_path, "wb")
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()
        if status:
            print(f"⬇️ Downloading {filename}: {int(status.progress() * 100)}%")

    print(f"✅ Downloaded {filename} to {file_path}")


def list_files(service, folder_id=None, page_size=20):
    """List files in Google Drive, optionally filtered by folder_id."""
    query = f"'{folder_id}' in parents" if folder_id else None
    results = (
        service.files()
        .list(q=query, pageSize=page_size, fields="nextPageToken, files(id, name, mimeType)")
        .execute()
    )
    return results.get("files", [])


def main():
    """Example usage of the Drive API helpers."""
    try:
        service = get_service()

        # List files in a specific folder
        folder_id = "18l_kSviqElZrFXgI_y9WsKaFeBtFpyp-"
        items = list_files(service, folder_id)

        if not items:
            print("No files found.")
        else:
            print("Files in Drive folder:")
            for item in items:
                print(f"{item['name']} ({item['id']})")

        # Upload example
        file_to_upload = "Kebabseg2.png"
        if os.path.exists(file_to_upload):
            upload_file(service, folder_id, file_to_upload)
        else:
            print("⚠️ Upload file not found locally.")

        # Download all files from folder
        for item in items:
            download_file(service, item["id"], item["name"], ".")

    except HttpError as error:
        print(f"❌ An error occurred: {error}")


if __name__ == "__main__":
    main()

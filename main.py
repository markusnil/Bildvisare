import os.path
import io

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload


# If modifying these scopes, delete the file token.json.
#SCOPES = ["https://www.googleapis.com/auth/drive.metadata.readonly"]
#SCOPES = ["https://www.googleapis.com/auth/drive.file"]
SCOPES = ["https://www.googleapis.com/auth/drive"]


# Function: "upload_file"
#   Uploads a file specified with path: "file_path" onto google drive folder: "folder_id"

def upload_file(service, folder_id, file_path, mime_type="application/octet-stream"):
    file_metadata = {
        "name": os.path.basename(file_path),
        "parents": [folder_id]   # upload into specific folder
    }
    media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id, name"
    ).execute()
    print(f"Uploaded {file.get('name')} (ID: {file.get('id')})")
    return file.get("id")

# Function: "download_file"
#   Downloads a file: "file_id" to destination path: "destination"

def download_file(service, file_id, filename, dest_dir="."):
    """Download a Drive file by ID if it's a binary file. Skip Google Docs types."""

    # Check file type first
    file_metadata = service.files().get(fileId=file_id, fields="mimeType, name").execute()
    mime_type = file_metadata.get("mimeType")

    if mime_type.startswith("application/vnd.google-apps"):
        print(f"⏭️ Skipping {filename} (Google Docs type, not a binary file)")
        return  # Skip non-binary files
    
    FileToDownload = file_metadata['name']
    if os.path.exists(FileToDownload):
      print("File already exists! Skipping!")
      return
    

    # Proceed with download
    request = service.files().get_media(fileId=file_id)
    file_path = os.path.join(dest_dir, filename)

    fh = io.FileIO(file_path, "wb")
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        if status:
            print(f"Downloading {filename}: {int(status.progress() * 100)}%")
    print(f"✅ Downloaded {filename} to {file_path}")


def main():
  """Shows basic usage of the Drive v3 API.
  Prints the names and ids of the first 10 files the user has access to.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("drive", "v3", credentials=creds)

    # Call the Drive v3 API
    results = (
        service.files()
        .list(q=f"'18l_kSviqElZrFXgI_y9WsKaFeBtFpyp-' in parents", pageSize=20, fields="nextPageToken, files(id, name)")
        #.list(pageSize=20, fields="nextPageToken, files(id, name)")
        .execute()
    )
    items = results.get("files", [])

    if not items:
      print("No files found.")
      #return
    print("Files:")
    for item in items:
      print(f"{item['name']} ({item['id']})")

    # Upload file:
    FileToDownload = "Kebabseg2.png"
    if os.path.exists(FileToDownload):
      print("Found file!")
      upload_file(service, "18l_kSviqElZrFXgI_y9WsKaFeBtFpyp-", FileToDownload)
      print("File uploaded!")
    else:
      print("Found nothing!!")

    os.makedirs(".", exist_ok=True)

    # Download all files:
    for item in items:
      download_file(service, item["id"], item['name'], ".")

  except HttpError as error:
    # TODO(developer) - Handle errors from drive API.
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()
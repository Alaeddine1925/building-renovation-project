import os.path
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload
import io
from datetime import datetime


def get_latest_file():
    SCOPES = ["https://www.googleapis.com/auth/drive"]
    creds = None

    # check for authentication token
    if os.path.exists("..\\Configurator_Frontend\\public\\token.pickle"):
        with open("..\\Configurator_Frontend\\public\\token.pickle", "rb") as token:
            creds = pickle.load(token)

    # check fpr valid credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "..\\Configurator_Backend\\API_Storage\\credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("..\\Configurator_Frontend\\public\\token.pickle", "wb") as token:
            pickle.dump(creds, token)

    drive_service = build("drive", "v3", credentials=creds)
    folder_id = "10dP2ZlCioYTG9dWeYKCVntlimZDLG_or"  # ID du dossier
    query = f"'{folder_id}' in parents"
    fields = "files(id, name, modifiedTime)"

    try:
        response = drive_service.files().list(q=query, fields=fields).execute()
        files = response.get("files", [])
        if not files:
            print("No file found in the Drive directory.")
            return "error"

        # Convert modifiedTime to datetime and sort files by it
        files = sorted(
            files,
            key=lambda x: datetime.strptime(x["modifiedTime"], "%Y-%m-%dT%H:%M:%S.%fZ"),
            reverse=True,
        )
        latest_file = files[0]
        file_name = "Fichier_USDZ.usdz"
        file_id = latest_file["id"]
        download_directory = "../Configurator_Frontend/public/"  # Remontez d'un niveau au répertoire parent
        if not os.path.exists(download_directory):
            os.makedirs(download_directory)
        file_name = download_directory + file_name

        request = drive_service.files().get_media(fileId=file_id)
        fh = io.FileIO(file_name, "wb")
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            done = downloader.next_chunk()
        print("Download file with success.")
        return "success"
    except HttpError as error:
        print("An error happened while downloading file :", error)
        return "error"

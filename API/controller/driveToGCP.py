
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.cloud import storage

# Only account in credentials.json (hadri.carad@gmail.com) can access google drive

def driveToGCP(fileName, fileID):
    
    def download_file(file_id, destination_file_path, credentials):
        """Downloads a file from Google Drive."""
        service = build('drive', 'v3', credentials=credentials)

        request = service.files().get_media(fileId=file_id)
        fh = io.FileIO(destination_file_path, 'wb')
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}%")

        print(f"File downloaded to {destination_file_path}")



    def upload_file(bucket_name, source_file_path, destination_blob_name):
        """Uploads a file to a Google Cloud Storage bucket."""
        # Initialize the storage client
        client = storage.Client()

        # Get the bucket
        bucket = client.get_bucket(bucket_name)

        # Create a blob with the desired destination name
        blob = bucket.blob(destination_blob_name)

        # Upload the file
        blob.upload_from_filename(source_file_path)

        print(f"File {source_file_path} uploaded to gs://{bucket_name}/{destination_blob_name}.")


    # Replace with your file's ID and the destination file path
    
    
    SCOPES = ['https://www.googleapis.com/auth/drive']
    
    FILE_ID = fileID
    DESTINATION_FILE_PATH = fileName
    flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
    credentials = flow.run_local_server(port=0)
    download_file(FILE_ID, DESTINATION_FILE_PATH, credentials)

    # Replace these values with your own
    BUCKET_NAME = "staging.api-wall-measures-391914.appspot.com"
    SOURCE_FILE_PATH = fileName
    DESTINATION_BLOB_NAME = "template/"+ fileName  # The name to be used in the bucket

    upload_file(BUCKET_NAME, SOURCE_FILE_PATH, DESTINATION_BLOB_NAME)
    
    return str("File " + fileID + " has been downloaded from google drive and uploaded to GCP "+ fileName +" with success")
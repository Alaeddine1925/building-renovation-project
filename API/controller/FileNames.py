from google.cloud import storage
from model.constantesGlobales import (
    GCP_PROGECT, GCP_BUCKETNAME, GCP_FOLDER_USDZ
)
import json

def FileNames():
    # Create a client using your Google Cloud project ID
    client = storage.Client(project=GCP_PROGECT)

    # Name of the bucket containing the files
    bucket_name = GCP_BUCKETNAME

    # Prefix for the folder (e.g., '/tmp/')
    folder_prefix = GCP_FOLDER_USDZ

    # List all blobs in the specified bucket with the prefix
    blobs = client.list_blobs(bucket_name, prefix=folder_prefix)

    # Iterate over the blobs and filter for file names ending with ".usdz"
    file_names = [blob.name for blob in blobs if blob.name.lower().endswith('.usdz')]

    # Print the file names
    for file_name in file_names:
        print(file_name)
    
    
    result = json.dumps(file_names, ensure_ascii = False, indent = 5)
    return json.loads(result) 


def LastUpdatedFile():
    # Create a client using your Google Cloud project ID
    client = storage.Client(project=GCP_PROGECT)

    # Name of the bucket containing the files
    bucket_name = GCP_BUCKETNAME

    # Prefix for the folder (e.g., '/tmp/')
    folder_prefix = GCP_FOLDER_USDZ

    # List all blobs in the specified bucket with the prefix
    blobs = client.list_blobs(bucket_name, prefix=folder_prefix)

    # Sort the blobs by their updated time in descending order
    sorted_blobs = sorted(blobs, key=lambda blob: blob.updated, reverse=True)

    # Get the name of the last uploaded file

    last_uploaded_file_name = sorted_blobs[0].name

    return last_uploaded_file_name

    
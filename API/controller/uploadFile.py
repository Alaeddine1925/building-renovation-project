from google.cloud import storage
from model.constantesGlobales import ( GCP_BUCKETNAME)

import json

def uploadFile(localFilePath, GCPFilePath):
    # Initialize a client
    client = storage.Client()

    # Define your bucket name
    bucket_name = GCP_BUCKETNAME

    # Get a reference to the bucket
    bucket = client.bucket(bucket_name)

    # Upload the file
    blob = bucket.blob(GCPFilePath)
    blob.upload_from_filename(localFilePath)

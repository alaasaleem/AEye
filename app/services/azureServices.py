from datetime import datetime, timedelta,timezone
import os
from dotenv import load_dotenv
from azure.cognitiveservices.speech import SpeechConfig
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.core.credentials import AzureKeyCredential
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from azure.ai.language.conversations import ConversationAnalysisClient
from azure.core.credentials import AzureKeyCredential
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.storage.blob import BlobServiceClient,ContainerSasPermissions,generate_container_sas

load_dotenv()

# Set up the subscription info for the Speech Service:
speechKey = os.getenv('AZURE_SPEECH_KEY')
serviceRegion = os.getenv('AZURE_SERVICE_REGION')
# Set up the subscription info for the Computer Vision Service:
aiEndpoint = os.getenv('AZURE_COMPUTER_VISION_ENDPOINT')
aiKey = os.getenv('AZURE_COMPUTER_VISION_KEY')
# Set up the subscription info for the Face Service:
faceEndpoint = os.getenv('AZURE_FACE_ENDPOINT')
faceKey = os.getenv('AZURE_FACE_KEY')
# Azure credentials
nlpKey =  os.getenv('AZURE_NLP_KEY')
nlpEndpoint =  os.getenv('AZURE_NLP_ENDPOINT')

projectName = os.getenv('AZURE_CONVERSATIONS_PROJECT_NAME')
deploymentName = os.getenv('AZURE_CONVERSATIONS_DEPLOYMENT_NAME')

# analyze quey
nlpClient = ConversationAnalysisClient(nlpEndpoint, AzureKeyCredential(nlpKey))

#cv client
cvClient = ComputerVisionClient(aiEndpoint, CognitiveServicesCredentials(aiKey))

#Azuer for BLOB storage 
storageEndpoint = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
#client of storage BLOB
storageClient = BlobServiceClient.from_connection_string(storageEndpoint)
connection_dict = dict(item.split("=", 1) for item in storageEndpoint.split(";") if item)

    # Extract the account name and account key
accountName = connection_dict.get("AccountName")
accountKey = connection_dict.get("AccountKey")

speechConfig = SpeechConfig(subscription=speechKey, region=serviceRegion)

imageAnalysisClient = ImageAnalysisClient(
    endpoint=aiEndpoint,
    credential=AzureKeyCredential(aiKey)
)

# Initialize the Face client
faceClient = FaceClient(faceEndpoint, CognitiveServicesCredentials(faceKey))



#function to create folder to the user and return the URL of the folder
def createUserContainer(containerName):
    try:
        containerClient = storageClient.get_container_client(containerName)      
        if containerClient.exists():
            return containerClient.url
        containerClient.create_container()
        
        # Get the URL of the folder
        containerURL = containerClient.url
        
        print(f"Folder '{containerName}' created successfully.")
        return containerURL
        
    except Exception as e:
        print(f"Error creating container: {e}")
        return None

def downloadContainer(containerName,dest):

    container_client = storageClient.get_container_client(containerName)

    for blob in container_client.list_blobs():
        blob_client = container_client.get_blob_client(blob)
        download_file_path = f"{dest}/{blob.name}"
        
        with open(download_file_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())

    print("Download complete.")

#function to upload img to the usere's container
def uploadImageToContainer(containerName, imageStream, blobName):
    number = 1
    try:
        blobClient = storageClient.get_blob_client(container=containerName, blob=blobName)
        containerClient = storageClient.get_container_client(containerName)
        if not containerClient.exists():
              containerClient.create_container()
        name, extension = blobName.rsplit('.') 
        #if the image already exists
        while blobClient.exists():
            blobName = f"{name}-{number}.{extension}" 
            number += 1
            blobClient = storageClient.get_blob_client(container=containerName, blob=blobName)
            print(f"Image '{blobName}' already exists in '{containerName}'. Attempting with new name.")
        
        #upload the image
        blobClient.upload_blob(imageStream)
        print(f"Image '{blobName}' uploaded successfully to '{containerName}'.")


    except Exception as e:
        print(f"Error uploading image: '{e}'")
        raise

def getSasToken(containerName):
    try:
        # Get the blob name from request args
        startTime=datetime.now(timezone.utc)
        # Define the SAS token parameters
        sasToken = generate_container_sas(
            account_name=accountName,
            container_name=containerName,
            account_key=accountKey,
            permission=ContainerSasPermissions(read=True,list=True),
            expiry=startTime + timedelta(minutes=15), 
            start=startTime
        )

        # Construct the full URL with SAS token

        return sasToken
    
    except Exception as e:
        print(f"Error generating SAS token: {e}")
        return None

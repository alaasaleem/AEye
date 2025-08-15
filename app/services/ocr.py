import io
from app.services.azureServices import cvClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes

def processImage(imageData):
    imageStream = io.BytesIO(imageData)

    ocrRead = cvClient.read_in_stream(imageStream, raw=True)

    operationLocation = ocrRead.headers["Operation-Location"]
    operationId = operationLocation.split("/")[-1]

    while True:
        getResult = cvClient.get_read_result(operationId)
        if getResult.status not in ['notStarted', 'running']:
            break

    if getResult.status == OperationStatusCodes.succeeded:
        extractedText = ""
        for textResult in getResult.analyze_result.read_results:
            for line in textResult.lines:
                extractedText += line.text + "\n"
        
        print(extractedText)
        return extractedText
    else:
        raise Exception("OCR failed")

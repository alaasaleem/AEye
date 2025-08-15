from app.services.azureServices import nlpClient,projectName,deploymentName
from app.services.objectDetection import ObjectDetection
from app.services.ocr import processImage
def analyzeText(STTOutput):
      result = nlpClient.analyze_conversation(
         task={
               "kind": "Conversation",
               "analysisInput": {
                  "conversationItem": {
                     "participantId": "1",
                     "id": "1",
                     "modality": "text",
                     "language": "en",
                     "text": STTOutput
                  },
                  "isLoggingEnabled": False
               },
               
               "parameters": {
                  "projectName": projectName,
                  "deploymentName": deploymentName,
                  "verbose": True
               }
         }
      )
      print("analyzing text.............")
      if not result["result"]["prediction"]["intents"]:
         return None,None
      if result["result"]["prediction"]["intents"][0]["confidenceScore"] > 0.66:
         if result["result"]["prediction"]["entities"] :
          entity = result["result"]["prediction"]["entities"][0]["text"] 
         else :
          entity = None
         if  result["result"]["prediction"]["topIntent"] =="DetectObject" and entity==None:
            return None,None
         return result["result"]["prediction"]["topIntent"],entity
      else:
         return None,None
from app.services.repeat import repeat,prevObj,setValues
def dynamicActionMapping(intent,entity=None,data=None):
    global prevObj
    
    if intent != "Replay" :
        setValues(intent,entity,data)

    if intent=="DetectObject":
       return  ObjectDetection(data,entity)
    elif intent=="AddFace":
        pass
    elif intent=="ReadText":
        return processImage(data)
    elif intent=="Replay":
        return  repeat()
        
    elif intent=="DetectFace":
        pass
    elif intent=="FaceExistCheck":
        pass
    else:
        pass

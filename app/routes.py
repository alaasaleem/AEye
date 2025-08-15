from io import BytesIO
import io
import random
import re
from flask import render_template, request, jsonify, send_from_directory
from app import app
import os
import base64
from app.services.textSpeechConversion import startSpeechToText,textToSpeech
from app.services.nlp import analyzeText,dynamicActionMapping
from app.services.repeat import prevObj,setValues
from app.services.ocr import processImage
from azure.cognitiveservices.speech.audio import AudioStreamFormat,PushAudioInputStream
from app.services.azureServices import uploadImageToContainer, createUserContainer,getSasToken
from app.database.database import insertUser, checkUser
from pydub import AudioSegment
from googletrans import Translator

channels = 1
bitsPerSample = 16
samplesPerSecond = 16000
audioFormat = AudioStreamFormat(samplesPerSecond, bitsPerSample, channels)
topIntent, entity =None,None
language = 'en-US'

@app.route('/getSasToken', methods=['POST'])
def getSas():
    try:
        data=request.json
        # Get the blob name from request args
        containerName = data['container']
        if not containerName:
            return jsonify({"error": "container name is required"}), 400

        token = getSasToken(containerName=containerName)
        return jsonify({"success": True,"sasToken": token}),200
    
    except Exception as e:
        print(f"Error generating SAS token: {e}")
        return jsonify({"success": False,"error": "Error generating SAS token"}), 500


@app.route('/get_image_labels', methods=['GET'])
def get_image_labels():
    image_folder = os.path.join(app.root_path, 'storage', 'images')
    image_files = [f for f in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, f))]

    labels = [os.path.splitext(f)[0] for f in image_files]
    
    return jsonify(labels=labels, image_files=image_files)
 

@app.route('/static/models/<filename>')
def serve_file(filename):
    base_dir = os.path.join(app.static_folder, 'models')
    return send_from_directory(base_dir, filename)
 

@app.route('/')
def home():
    global language
    global entity
    global topIntent
    topIntent,entity,language=None,None,"en-US"
    return render_template('home.html')

@app.route('/storage/images/<filename>')
def serve_image(filename):
    base_dir = os.path.join(app.root_path, 'storage', 'images')
    return send_from_directory(base_dir, filename)

@app.route('/save-image', methods=['POST'])
def save_image_only():
    data = request.json
    image_data = data.get('image')

    if not image_data:
        return jsonify({'error': 'No image data provided'}), 400

    try:
        image_data = base64.b64decode(image_data.split(',')[1])
        
        import time
        filename = f"image_{int(time.time())}.png"
        base_dir = os.path.join(app.root_path, 'storage', 'images')
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        
        file_path = os.path.join(base_dir, filename)
        
        with open(file_path, 'wb') as f:
            f.write(image_data)

        
        return jsonify({'filename': filename}), 200

    except Exception as e:
        print(f"Error saving image: {e}")
        return jsonify({'error': 'Error saving image'}), 500
 
@app.route('/detect-object', methods=['POST'])
def detect():
    global topIntent
    global entity
    data = request.json
    
    image_data = data['image']
    image_data = base64.b64decode(image_data.split(',')[1])
    
    setValues("DetectObject",entity,image_data)
    detection_result = dynamicActionMapping(topIntent, entity, image_data)

    new_image_data = detection_result['newImageData']
   
    img_base64 = base64.b64encode(new_image_data).decode('utf-8')
        
    if detection_result['objectDetected']:
        return {"detected": detection_result['objectDetected'], "image": img_base64, "audio": detection_result['audio']}, 200
    else:
        response = {"detected": detection_result['objectDetected']}
        if detection_result['audio']:
            response["audio"] = detection_result['audio']
        return response, 200
    
@app.route('/repeat-prev',methods=['GET'])
def rep():
    if prevObj.prevIntent == None:
        tts = textToSpeech(text="please do at least one action")
        return {"success": False,"audio" :tts }
   
    try :
        result =  dynamicActionMapping("Replay")
        if prevObj.prevIntent =="DetectObject" :

            new_image_data = result['newImageData']
        
            img_base64 = base64.b64encode(new_image_data).decode('utf-8')
        
            if result['objectDetected'] :
                return {"detected": result['objectDetected'],"image": img_base64,"audio":result['audio'],"intent" : prevObj.prevIntent}, 200
            elif (result['audio']) :
                return {"detected": result['objectDetected'],"audio" :result['audio']}, 500
            else:
                return {"detected": result['objectDetected']}, 500
        
        elif prevObj.prevIntent =="ReadText":
            result = ' '.join(result.splitlines())
            ttsAudio = textToSpeech(text=result)
            return jsonify({"success": True,'ocrText': result, 'audio': ttsAudio,"intent" : prevObj.prevIntent}), 200
    except Exception:
        tts=textToSpeech(text="Couldnt repeat your command")
        return {"success": False,"audio" :tts}, 500
       
 
    
@app.route('/get-capture-audio',methods=['GET'])
def captureAudio():
    try:
        tts= textToSpeech(text="Now, Take a clear picture of the person")
        return jsonify({'success': True,"audio" : tts }), 200
    except Exception:
        return jsonify({"success": False}),500

@app.route('/change-language',methods=['POST'])
def changeLanguage():
   data=request.json
   global language
   language=data['language']          
   return jsonify({'success': True}), 200
    
@app.route('/upload-audio', methods=['POST'])
def uploadAudio():
    global language
    try:
        file = request.files['audio']
        file_bytes =  file.read()
        custom_push_stream = PushAudioInputStream(stream_format=audioFormat)
        audio = AudioSegment.from_file(BytesIO(file_bytes)) 
        audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
        audio_data = audio.raw_data
        custom_push_stream.write(audio_data)
        custom_push_stream.close()
        recognizedText = startSpeechToText(custom_push_stream,language)
        if recognizedText:
          return jsonify({'success': True,"text" : recognizedText }), 200
        else:
             tts = textToSpeech(text="Speech could not be recognized.")
             return jsonify({'success': False, 'audio': tts}), 500
    except Exception as e:
      print(f"Error saving image: {e}")  
      tts = textToSpeech(text="Speech could not be recognized.")
      return jsonify({'success': False, 'audio': tts}), 500
    
@app.route('/analyze-text', methods=['POST'])   
def analyze():
    global topIntent
    global entity
    data = request.json
    recognizedText = data['text']
    analysisResult = analyzeText(recognizedText)
    if analysisResult != (None, None):
     topIntent, entity = analysisResult
     page = getRedirectPage(topIntent) 
     if page:
        return jsonify({'success': True,  'entity': entity, 'page': page,'intent' : topIntent}), 200
     else:
         tts = textToSpeech(text="Please Say something related.")
         return jsonify({'success': False, 'message': 'Text analysis failed.', "audio": tts}), 500
    else:
        tts = textToSpeech(text="I didn't understand your command, please say it again")
        return jsonify({'success': False, 'message': 'Text analysis failed.', "audio": tts}), 500
   
@app.route('/add-face', methods=['GET'])
def addFace():
    if entity:
        tts = textToSpeech(text="Whats their relation to you?")
        return jsonify({'success': True, "audio": tts,"name" : True}), 200
    else:
         tts = textToSpeech(text="Whats their name?")
         return jsonify({'success': True, "audio": tts,"name" : False}), 200
     
@app.route('/cont-add-face', methods=['POST'])
def addFaceCont():
    data = request.json
    global entity
    if not entity:
     entity=data['entity']
     tts = textToSpeech(text="Whats their relation to you?")
     return jsonify({'success': True, "audio": tts,"name" : True}), 200
 
def parseEntity(entity):
    # Split the entity into first name and last name
    parts = entity.split()
    last_name=None
    first_name = parts[0]
    if parts[1:]:
     last_name = ' '.join(parts[1:])  # Join remaining parts for the last name
    return first_name, last_name

def formatFilename(firstName, lastName, relation):
    # Format the filename as "FirstName-LastName-Relation"
    firstName = firstName.lower()
    relation =  relation.lower()
    pronouns = ["he", "she", "they", "we", "i", "you", "it", "my", "our", "his", "her", "their", "mine", "ours", "yours", "hers", "theirs","a"]
    pattern = r'\b(' + '|'.join(pronouns) + r')\s+(is|was|are|were|am|be|been|being)?\b'
    cleaned = re.sub(pattern, '', relation, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    if not lastName:
       fileName=  f"{firstName}-{cleaned}"
    else : 
       lastName =  lastName.lower()
       fileName=  f"{firstName}-{lastName}-{cleaned}"

    fileName = fileName.replace('.', '')
    fileName = fileName.replace('?', '')
    fileName = fileName.replace('!', '')
    fileName = fileName.replace(',', '')
    return fileName

@app.route('/insert-user', methods=['GET'])
def insert_user():
    def generate_uuid():
        return ''.join(
            ['%x' % random.randint(0, 15) if c == 'x' else '%x' % (random.randint(0, 15) & 0x3 | 0x8) for c in 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx']
        )
    userUUID = generate_uuid()
    while checkUser(userUUID):
        userUUID = generate_uuid()
    container_url = createUserContainer(userUUID)
    insertUser(userUUID,container_url)
    if container_url:
        return jsonify({'success': True, 'UUID': userUUID}), 200
    else:
        return jsonify({'success': False, 'message': 'Container creation failed'}), 500

@app.route('/finish-adding', methods=['POST'])
def add_to_db():
    data = request.json
    userUUID = data.get('userUUID')
    if not userUUID:
        return jsonify({'error': 'UUID is missing'}), 400
    global entity
    translator = Translator()
    translated = translator.translate(entity,dest="ar")
    relation = data.get('relation', '')
    imageData = data.get('image', '')
    if not translated.pronunciation:
        result = translator.translate('My name is '+entity,dest="ar",src="en")
        result = translator.translate(result.text,dest="en",src="ar")
        # Assuming the name is always after "is"
        match = re.search(r"My name is (.+)", result.text)
        if match:
         translated=match.group(1)
    else:
        translated=translated.pronunciation
    
    # Parse the entity into first name and last name
    firstName, lastName = parseEntity(translated)
    # Format the filename
    formattedName = formatFilename(firstName, lastName, relation)
    fileExtension = '.jpg'  # You may want to derive this from the image data if needed
    fileName = formattedName + fileExtension
    
    #assume just for test the container name is hala
    contName = userUUID

    # Decode the image data
    try:
        # Remove the data URL scheme part if present
        if imageData.startswith('data:image/jpeg;base64,'):
            imageData = imageData.replace('data:image/jpeg;base64,', '')
        elif imageData.startswith('data:image/png;base64,'):
            imageData = imageData.replace('data:image/png;base64,', '')

        imageBytes = base64.b64decode(imageData)
        
        # Create a BytesIO object for the image
        imageFile = io.BytesIO(imageBytes)
        
        # Upload the in-memory file to Azure Blob Storage
        uploadImageToContainer(containerName= contName , imageStream= imageFile , blobName= fileName)
        
        tts=textToSpeech(text=translated+" Has been added")
        return jsonify({'success':True, 'fileName': fileName,'audio' : tts}),200

    except Exception as e:
        print(f"Error uploading image: {e}")
        tts=textToSpeech("Couldnt add " + translated)
        return jsonify({'success':False,'audio' : tts}),500

@app.route('/objectDetection')
def object_detection():
    return render_template('objectDetection.html')

@app.route('/repeat')
def repeat():
    return render_template('repeat.html')

@app.route('/faceRecognition')
def faceRecognition():
    return render_template('faceRecognition.html')

@app.route('/addFace')
def addFaceRoute():
    return render_template('addFace.html')
@app.route('/readText')
def textReading():
    return render_template('textReading.html')

def getRedirectPage(intent):
    pages = {
        "DetectObject": "objectDetection",
        "Replay": "repeat",
        "ReadText": "readText",
        "AddFace" : "addFace",
        "None":None
    }
    return pages.get(intent, "")

@app.route('/process-ocr' , methods=['POST'])
def process_ocr():
    data = request.json
    imageData = data.get('imageData')
    imageData = base64.b64decode(imageData.split(',')[1])
    setValues("ReadText",entity,imageData)
    if not imageData:
        return jsonify({'error': 'No image provided'}), 400
    
    try:
        ocrText = processImage(imageData)
        if ocrText:
            ocrText = ' '.join(ocrText.splitlines())
            ttsAudio = textToSpeech(text=ocrText)
            return jsonify({"success":True,'ocrText': ocrText, 'audio': ttsAudio}), 200
        else :
            ttsAudio = textToSpeech(text="No text recognized")
            return jsonify ({"success":False,'error': 'Error OCR','audio': ttsAudio}), 500
       
    except Exception as e:
        ttsAudio = textToSpeech(text="Couldnt read this text")
        return jsonify ({"success":False,'error': 'Error OCR','audio': ttsAudio}), 500
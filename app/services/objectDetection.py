from app.services.azureServices import imageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from app.services.azureServices import imageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from app.services.textSpeechConversion import textToSpeech
from PIL import Image, ImageDraw
import io


def ObjectDetection(image_data, target_obj):
    print("Image received for detection...\n")
    visual_features = [VisualFeatures.DENSE_CAPTIONS]
    image_stream = io.BytesIO(image_data)

    try:
        # Analyze the image using analyze_image_in_stream
        analysis_result = imageAnalysisClient.analyze(image_stream, visual_features=visual_features)
        
        image_width = analysis_result.metadata.width
        image_height = analysis_result.metadata.height

        # Extract objects from the result
        dense_captions = analysis_result.dense_captions.list
        filtered_captions = [
        (caption.text, caption.bounding_box)
        for caption in dense_captions
        if target_obj.lower() in caption.text.lower()]
        
        if  filtered_captions:
           def bbox_area(bbox):
                 return bbox['w'] * bbox['h']
           smallest_bbox_caption = min(filtered_captions, key=lambda x: bbox_area(x[1]))
           smallest_bbox_caption=smallest_bbox_caption[1]
           x,y,w,h=smallest_bbox_caption['x'],smallest_bbox_caption['y'],smallest_bbox_caption['w'],smallest_bbox_caption['h']
           x_center, y_center = findTheCenterOfTheObject(x,y,w,h)
           feedbackInstruction = PrepareFeedback(x_center, y_center, image_width, image_height)
           tts = textToSpeech(text=feedbackInstruction)
           image_with_box_data = addBoundingBox(x,y,w,h,image_data)
           return {"objectDetected": True, "newImageData": image_with_box_data,"audio":tts}

        else:
                tts= textToSpeech(text="Object not found. Please turn left to scan another side...")
                return {"objectDetected": False, "newImageData": image_data,"audio":tts}
        

    except Exception as e:
        print(f"Error during object detection: {str(e)}")
        return {"objectDetected": False, "newImageData": image_data}

def findTheCenterOfTheObject(x,y,w,h):
    x_center = x + w/2
    y_center = y + h/2
    return x_center, y_center

def PrepareFeedback(x_center, y_center, image_width, image_height):
    if x_center < image_width * 0.33:
        horizontal_position = "left"
    elif x_center > image_width * 0.66:
        horizontal_position = "right"
    else:
        horizontal_position = "center"
    
    if y_center < image_height * 0.33:
        vertical_position = "top"
    elif y_center > image_height * 0.66:
        vertical_position = "bottom"
    else:
        vertical_position = "middle"

    return (f"The object is at the {vertical_position}-{horizontal_position} of the image.")

def addBoundingBox(x,y,w,h, image_data):

    image = Image.open(io.BytesIO(image_data))

    draw = ImageDraw.Draw(image)

    top_left = (x, y)
    bottom_right = (x + w, y + h)

    draw.rectangle([top_left, bottom_right], outline="red", width=2)

    image_with_box = io.BytesIO()
    image.save(image_with_box, format='PNG')

    image_with_box_data = image_with_box.getvalue()

    image_with_box.close()

    print("Bounding box drawn and image data returned")
    return image_with_box_data

import base64
import io
from threading import Event
from pydub import AudioSegment
from app.services.azureServices import speechConfig
from azure.cognitiveservices.speech import SpeechRecognizer, AudioConfig, SpeechSynthesizer, ResultReason, CancellationReason
import azure.cognitiveservices.speech as speechsdk
text=None
def convertAudioFormat(inputPath, outputPath):
    try:
        audio = AudioSegment.from_file(inputPath)
        audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
        audio.export(outputPath, format='wav')
    except Exception as e:
        print(f"Error converting audio file: {e}")
        return None

def textToSpeech(text):
    try:
        pullStream = speechsdk.audio.PullAudioOutputStream()
        audioOutput = AudioConfig(stream=pullStream)
        synthesizer = SpeechSynthesizer(speech_config=speechConfig,audio_config=audioOutput)

        result = synthesizer.speak_text_async(text).get()

        if result.reason == ResultReason.SynthesizingAudioCompleted:
            audio_data = result.audio_data
             # Convert audio data to an in-memory file (BytesIO)
            audio_io = io.BytesIO(audio_data)
             # Encode the audio data as base64
            audio_segment = AudioSegment.from_raw(io.BytesIO(audio_data), sample_width=2, frame_rate=16000, channels=1)
            mp3_io = io.BytesIO()
            audio_segment.export(mp3_io, format="mp3")

    # Encode the MP3 audio data as base64
            audio_base64 = base64.b64encode(mp3_io.getvalue()).decode('utf-8')
            audio_base64 = audio_base64.replace('\n', '')
            print("Speech synthesized successfully.")
            return audio_base64
        elif result.reason == ResultReason.Canceled:
            cancellationDetails = result.cancellation_details
            print(f"Speech synthesis canceled: {cancellationDetails.reason}")
            if cancellationDetails.reason == CancellationReason.Error:
                print(f"Error details: {cancellationDetails.errorDetails}")
            return None
        else:
            print(f"Speech synthesis failed. Reason: {result.reason}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")

def startSpeechToText(audio_bytes,language):
    global text
    global speechConfig
    speechConfig.speech_recognition_language=language
    synthesis_done = Event()
    textL =  speechToText(audio_bytes,synthesis_done)
    text = None
    return textL

    
def speechToText(audio_bytes,synthesis_done):
    global text

    def resCll(evt):
        global text
        try:
            result = evt.result
            if result.reason == ResultReason.RecognizedSpeech:
                text=result.text
                print(f"Recognized Text: {result.text}")
            elif result.reason == ResultReason.NoMatch:
                print("No speech could be recognized.")
            elif result.reason == ResultReason.Canceled:
                cancellationDetails = result.cancellation_details
                print(f"Speech recognition canceled: {cancellationDetails.reason}")
                if cancellationDetails.reason == CancellationReason.Error:
                    print(f"Error details: {cancellationDetails.errorDetails}")
            else:
                print(f"Speech could not be recognized. Reason: {result.reason}")
            
            synthesis_done.set()
        except Exception as e:
            print(f"Exception occurred: {e}")

    audioConfig = AudioConfig(stream=audio_bytes)
    recognizer = SpeechRecognizer(speech_config=speechConfig, audio_config=audioConfig)
    recognizer.recognized.connect(resCll)
    recognizer.start_continuous_recognition()
    synthesis_done.wait()
    recognizer.stop_continuous_recognition()
    return text
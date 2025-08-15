import { recordButton, buttonContainer, waveform, processingMessage, delay } from './constants.js';
import { playAudio } from './utils.js';

export const siriWave = new SiriWave({
  container: waveform,
  width: 700,
  height: 500,
  speed: 0.08,
  amplitude: 1,
  frequency: 2,
  cover: true,
  style: "ios9"
});
export var action = analyzeAudio;
// Save initial display values
const initialRecordButtonDisplay = recordButton.style.display;
const initialButtonContainerDisplay = buttonContainer.style.display;
// Declare the timeout variable
let stopTimeout;

const myvad = await vad.MicVAD.new({
  positiveSpeechThreshold: 0.8,
  minSpeechFrames: 3,
  preSpeechPadFrames: 10,
  onSpeechStart() {
    clearTimeout(stopTimeout); // Clear the timeout if speech is detected
  },
  onSpeechEnd: (arr) => {

    recordButton.style.display = initialRecordButtonDisplay; // Show the button again
    buttonContainer.style.display = initialButtonContainerDisplay; // Show button container again
    recordButton.disabled = true;  //disable the record button
    waveform.style.display = 'none'; // Hide waveform
    siriWave.stop();
    myvad.pause()
    const wavBuffer = vad.utils.encodeWAV(arr);  // Encoded WAV data as an ArrayBuffer

    processingMessage.style.display = 'flex';
    // Create a Blob from the ArrayBuffer
    const audioBlob = new Blob([wavBuffer], { type: 'audio/wav' });

    // Create a FormData object to hold the Blob
    const formData = new FormData();
    formData.append('audio', audioBlob, 'audio.wav');
    uploadAudio(formData, action)

  },
})
recordButton.addEventListener('click', () => {
  stopTimeout = setTimeout(() => {
    recordButton.style.display = initialRecordButtonDisplay; // Show the button again
    buttonContainer.style.display = initialButtonContainerDisplay; // Show button container again
    waveform.style.display = 'none'; // Hide waveform
    siriWave.stop();
    myvad.pause()

  }, 3000);
  recordButton.style.display = 'none'; // Hide the button
  buttonContainer.style.display = 'none'; // Hide the button container
  waveform.style.display = 'block'; // Show waveform
  siriWave.start(); // Start the waveform animation

  myvad.start()

});
export function uploadAudio(formData, action) {
  fetch('/upload-audio', {
    method: 'POST',
    body: formData
  })
    .then(response => response.json())
    .then(async data => {
      console.log("Response from server:", data);

      if (data.success) {
        action(data.text)
      }
      else {
        processingMessage.style.display = 'none';
        await playAudio(data.audio)
        await delay(1000);
        window.location.href = '/';

      }
    });

}
export function analyzeAudio(textl) {
  fetch('/analyze-text', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ text: textl })
  })
    .then(response => response.json())
    .then(async data => {
      if (data.success) {
          processingMessage.style.display = 'none';
          window.location.href = `/${data.page}`;
        
      }
      else {
        await  playAudio(data.audio);
       await delay(1000);
        window.location.href = `/`;
      }
    });
}
export function changeAction(actionl) {
action = actionl;
}
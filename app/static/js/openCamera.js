import { delay } from "./constants.js";

export const webCamElement = document.getElementById('webcam');
let currentFacingMode = 'user'; // Default to front camera

// Function to start the webcam using a specific device
async function startWebcam(facingModeOrDeviceId) {
  try {
    const constraints =  facingModeOrDeviceId === 'environment' || facingModeOrDeviceId==='user'
    ?  // Use deviceId if provided
     { video: { facingMode: { ideal: facingModeOrDeviceId } } } : { video: { deviceId: { exact: facingModeOrDeviceId } } }; // Otherwise, use facingMode
    const stream = await navigator.mediaDevices.getUserMedia(constraints);
    webCamElement.srcObject = stream;
    webCamElement.play();
    console.log(`Webcam started with ${facingModeOrDeviceId} camera.`);
  } catch (err) {
    console.error("Error accessing the webcam: ", err);
    alert("Failed to access the webcam.");
  }
}

// Function to check for the back camera and return its device object
async function getBackCameraDevice() {
  try {
    const devices = await navigator.mediaDevices.enumerateDevices();
    const videoDevices = devices.filter(device => device.kind === 'videoinput');

    for (const device of videoDevices) {
      const constraints = { video: { deviceId: { exact: device.deviceId } } };
      const testStream = await navigator.mediaDevices.getUserMedia(constraints);
      const videoTrack = testStream.getVideoTracks()[0];
      const capabilities = videoTrack.getCapabilities();

      // Assuming focal length is in mm; adjust the threshold as needed
      if (capabilities.focalLength > 18 && capabilities.focalLength < 60) {
        testStream.getTracks().forEach(track => track.stop()); // Stop test stream
        return device; // Return the device with normal focal length
      }

      testStream.getTracks().forEach(track => track.stop()); // Stop test stream if not suitable
    }
    
    return null; // Return null if no suitable device is found
  } catch (err) {
    console.error("Error checking for environment camera: ", err);
    return null;
  }
}

// Flip camera functionality
document.getElementById('flipButton').addEventListener('click', async () => {
  // Flip between user and environment modes, or switch by deviceId if we have a back camera device
  currentFacingMode = currentFacingMode === 'user' ? 'environment' : 'user';

  // Stop the current stream before starting a new one
  if (webCamElement.srcObject) {
    const tracks = webCamElement.srcObject.getTracks();
    tracks.forEach(track => track.stop());
  }

  // Get the back camera device if available, or fall back to 'user'
  const backCameraDevice = await getBackCameraDevice();
  if (currentFacingMode === 'environment' && backCameraDevice) {
    startWebcam(backCameraDevice.deviceId); // Start with the back camera using deviceId
  } else {
    startWebcam(currentFacingMode); // Otherwise, start with facingMode
  }
});

// Initial camera setup
getBackCameraDevice().then(backCameraDevice => {
  if (backCameraDevice) {
    document.getElementById('flipButton').style.display = 'block'; // Show flip button if back camera is available
    currentFacingMode = 'environment'; // Default to back camera if available
    startWebcam(backCameraDevice.deviceId); // Start with back camera using its deviceId
  } else {
    currentFacingMode = 'user'; // Default to front camera if no back camera found
    startWebcam(currentFacingMode); 
  }
});

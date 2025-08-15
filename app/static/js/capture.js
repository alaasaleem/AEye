import { captureTimer, canvasElement, processingMessage } from './constants.js';
import { webCamElement ,delay} from './constants.js';
import { startTimer } from './timer.js';



export async function captureImage() {
    try {
        startTimer(captureTimer, 'Captured', 3, 1000);
        await delay(4000);
        processingMessage.style.display = 'flex';

        // Set canvas dimensions to match the video feed

        const context = canvasElement.getContext('2d');
        context.imageSmoothingEnabled = true; // Ensures the quality is maintained when drawing

        // Draw the current video frame onto the canvas
        context.drawImage(webCamElement, 0, 0, canvasElement.width, canvasElement.height);
        canvasElement.style.display = 'none';

        // Get the image data from the canvas as a PNG (can use JPEG for compression)
        const imageData = canvasElement.toDataURL('image/png'); // Use 'image/jpeg' for a compressed format

        console.log("Captured image data:", imageData); // For debugging
        return imageData;
    } catch (error) {
        console.error("Error capturing image:", error);
        processingMessage.style.display = 'none';
        throw error;
    }
}

export async function captureImageForFace() {
    try {
        startTimer(captureTimer, 'Captured', 3, 1000);
        await delay(4000);
        processingMessage.style.display = 'flex';

        // Set canvas dimensions to match the video feed
        const videoWidth = webCamElement.videoWidth;
        const videoHeight = webCamElement.videoHeight;

        canvasElement.width = videoWidth;
        canvasElement.height = videoHeight;

        const context = canvasElement.getContext('2d');
        context.imageSmoothingEnabled = true; // Ensures the quality is maintained when drawing

        // Draw the current video frame onto the canvas
        context.drawImage(webCamElement, 0, 0, canvasElement.width, canvasElement.height);
        canvasElement.style.display = 'none';

        // Get the image data from the canvas as a PNG (can use JPEG for compression)
        const imageData = canvasElement.toDataURL('image/png'); // Use 'image/jpeg' for a compressed format

        return imageData;
    } catch (error) {
        console.error("Error capturing image:", error);
        processingMessage.style.display = 'none';
        throw error;
    }
}



export async function saveImage() {
    startTimer(captureTimer, 'Captured', 3, 1000);
    await delay(4000);
    processingMessage.style.display = 'flex';
    const context = canvasElement.getContext('2d');
    context.drawImage(webCamElement, 0, 0, canvasElement.width, canvasElement.height);
    const imageData = canvasElement.toDataURL('image/png');

    console.log("Captured image data:", imageData);

    try {
        const response = await fetch('/save-image', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ image: imageData })
        });

        const data = await response.json();
        console.log("Server response:", data);
        processingMessage.style.display = 'none';

        if (response.ok) {
            return data.filename;
        } else {
            console.error("Error saving image:", data);
            return null;
        }
    } catch (err) {
        console.error("Error sending image data:", err);
        processingMessage.style.display = 'none';
        return null;
    }
}

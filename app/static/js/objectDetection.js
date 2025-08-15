import { processingMessage, delay } from './constants.js';
import { captureImage } from './capture.js';
import { playAudio, getURL, showDetectedImage, returnHome } from './utils.js';
let count = 5;

export async function detectAndHandleObject() {
    const image_data = await captureImage();

    const response = await fetch('/detect-object', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ image: image_data })
    });

    const data = await response.json();

    if (response.ok) {
        if (data.detected) {
            processingMessage.style.display = 'none';
            playAudio(data.audio);
            await showDetectedImage(getURL(data.image));
        } else {
            if (count > 0 && data.audio) {
                await playAudio(data.audio);
                count--;
                await delay(2000);
                await detectAndHandleObject();
            }
            else {
                count = 5;
                returnHome();
            }
            console.log("Object not detected.");
        }
    } else {
        console.error('Detection failed:', data);
    }
}

detectAndHandleObject();

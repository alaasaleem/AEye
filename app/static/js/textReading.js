import { captureTextButton, canvasElement, webCamElement, borderBox , ocrTextBox, ocrTextElement } from './constants.js';
import { playAudio } from './utils.js';

captureTextButton.addEventListener('click', function () {
    const canvasContext = canvasElement.getContext('2d');

    canvasElement.width = webCamElement.videoWidth;
    canvasElement.height = webCamElement.videoHeight;

    const boxRect = borderBox.getBoundingClientRect();
    const videoRect = webCamElement.getBoundingClientRect();
    
    const scaleX = webCamElement.videoWidth / videoRect.width;
    const scaleY = webCamElement.videoHeight / videoRect.height;
    
    const x = (boxRect.left - videoRect.left) * scaleX;
    const y = (boxRect.top - videoRect.top) * scaleY;
    const width = boxRect.width * scaleX;
    const height = boxRect.height * scaleY;

    canvasContext.drawImage(webCamElement, x, y, width, height, 0, 0, width, height);
 
    const capturedImage = canvasElement.toDataURL('image/png');
    canvasContext.clearRect(0, 0, canvasElement.width, canvasElement.height);
    captureTextButton.disabled = true;
    borderBox.style.display = 'none'; // Hide the borderBox

    //request OCR
    fetch('/process-ocr', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ imageData: capturedImage })
    })
        .then(response => response.json())
        .then(async data => {
            if (data.ocrText) {
                console.log('OCR Text:', data.ocrText);
                ocrTextElement.textContent = data.ocrText;
                ocrTextBox.style.display = 'block';
                captureTextButton.disabled = false;
                borderBox.style.display = 'flex'; // Hide the borderBox

    
                if (data.audio) {
                    captureTextButton.disabled = false;
                    borderBox.style.display = 'flex'; // Hide the borderBox
                    playAudio(data.audio);
                    // highlightText(data.ocrText);
    
                }
            } else {
             await   playAudio(data.audio);
                borderBox.style.display = 'flex'; // Hide the borderBox
                captureTextButton.disabled = false;
                console.error('Error processing OCR:', data.error);
            }
        })
        .catch(error => {
            console.error('Request failed:', error);
        });
});

function highlightText(text) {
    const wordsArray = text.split(' ');
    ocrTextElement.innerHTML = wordsArray.map(word => `<span class="word">${word}</span>`).join(' ');

    const updatedWords = Array.from(ocrTextElement.getElementsByClassName('word'));

    updatedWords.forEach((word, index) => {
        setTimeout(() => {
            if (index > 0) {
                updatedWords[index - 1].classList.remove('highlight');
            }
            if (index < updatedWords.length) {
                updatedWords[index].classList.add('highlight');

            }
        }, index * 600);
    });
}

export function closeModal() {
    ocrTextBox.style.display = 'none';
}
document.querySelector('#ocrTextBox .close').addEventListener('click', closeModal);

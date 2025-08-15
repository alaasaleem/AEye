import {getURL,playAudio,showDetectedImage,returnHome,} from './utils.js'
import { processingMessage ,delay,ocrTextElement,ocrTextBox,doneButton,startButton} from './constants.js';
doneButton.style.display='none';

startButton.addEventListener('click', function () {
    doneButton.style.display='flex';
    startButton.style.display='none';

processingMessage.style.display = 'flex';

function repeat() {
    fetch('/repeat-prev')
        .then(response => response.json())
        .then(async data => {
            if (data.intent == 'DetectObject') {
                if (data.detected) {
                    processingMessage.style.display = 'none';
                    playAudio(data.audio);
                    await showDetectedImage(getURL(data.image));      
                }
                else if (data.audio) {
                   await playAudio(data.audio);
                    await delay(1500);
                    returnHome();
                }

            }
            else if (data.intent == "ReadText") {
                if(data.success){
                ocrTextElement.textContent = data.ocrText;
                ocrTextBox.style.display = 'block';
                processingMessage.style.display='none';
                doneButton.style.background = "green";
                doneButton.disabled = false;
                doneButton.style.cursor = "pointer"; 
                doneButton.style.display = "flex";
                await playAudio(data.audio);
            }
            else{
               await playAudio(data.audio);
                await delay(1500);
                returnHome();

            }
        }
            else if (!data.success){
                await playAudio(data.audio)
                await delay(1500);
                returnHome();
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
        

}
repeat();
});
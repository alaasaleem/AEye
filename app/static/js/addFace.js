import { recordButton, delay, processingMessage ,doneButton,timer, exitButton} from "./constants.js";
import {  changeAction } from "./buttonRecord.js";
import { playAudio ,returnHome} from "./utils.js";
import { captureImageForFace } from "./capture.js";
import { startTimer } from "./timer.js";
let name = false

 const captureImageButton = document.getElementById('captureImageButton');
 captureImageButton.disabled=true;

 async function startAdding() {
    const response = await fetch('/add-face');
    const data = await response.json();
    if (data.success) {
        if (data.name) {
            name = true;
            await fetch('/change-language', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json'
                },
                body: JSON.stringify({ language: "en-US" })
              })
        }
        else{
            await fetch('/change-language', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json'
                },
                body: JSON.stringify({ language: "ar-JO" })
              })
        }
        playAudio(data.audio);
        await delay(1500);
        recordButton.disabled = false;
    }
}
async function contAdding(text) {
    if (name) {
        await fetch('/get-capture-audio')
        .then(async response => await response.json())
        .then(async data =>  {
            if(data.success)
                playAudio(data.audio)
        });
        captureImageButton.disabled=false;
        recordButton.style.display='none';
        exitButton.style.display='none';
        captureImageButton.style.display='flex'
        processingMessage.style.display='none';

        captureImageButton.addEventListener('click',async () => {
            const image_data = await captureImageForFace();
            const response = await fetch('/finish-adding', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ image: image_data, relation: text ,userUUID: localStorage.getItem('userUUID')})
            });
           const data = await response.json();
           console.log(data)
            if (data.success) {
                captureImageButton.style.display='none';
                processingMessage.style.display='none';
                doneButton.style.display = "flex";
                doneButton.style.background = "green";
                doneButton.disabled = false;
                doneButton.style.cursor = "pointer"; 
                timer.style.display = 'block';
            
                startTimer(timer, "", 10, 1000);
                playAudio(data.audio);
                await delay(11000);
                returnHome();
            }
            else {
                playAudio(data.audio);
                await delay(2000);
                returnHome();
            }
        })
    }
    else {
        const response = await fetch('/cont-add-face', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ nameAdded: true, entity: text })
        });
        const data = await response.json();
        if (data.success) {
            processingMessage.style.display='none';
            name = true;
            playAudio(data.audio);
            recordButton.disabled = false;
            await fetch('/change-language', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json'
                },
                body: JSON.stringify({ language: "en-US" })
              })
        }

    }

}
changeAction(contAdding);
await delay(1500);
startAdding();
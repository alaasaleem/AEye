
import { webCamElement, canvasElement, processingMessage, statusMessageElement, cacheName } from "./constants.js";
import { downloadContainer } from './downloadContainer.js';

const startTime = performance.now();

statusMessageElement.textContent = 'Syncing...';
processingMessage.style.display = 'flex';
const containerName =localStorage.getItem('userUUID');
await downloadContainer(containerName)

processingMessage.style.display = 'none';
statusMessageElement.textContent = 'loading...';
const endTime = performance.now();
const duration = endTime - startTime;
let cacheCount = 0;
console.log(`Download and caching completed in ${duration.toFixed(2)} milliseconds.`);

async function startFaceRecognition() {

    let labeledFaceDescriptors;
    let faceMatcher;
    processingMessage.style.display = 'flex';

    //  await faceapi.nets.ssdMobilenetv1.loadFromUri('/static/models');
    await faceapi.nets.tinyFaceDetector.loadFromUri('/static/models');
    await faceapi.nets.faceLandmark68Net.loadFromUri('/static/models'); // faceLandmark68TinyNet , useTinyModel= True
    await faceapi.nets.faceRecognitionNet.loadFromUri('/static/models');

    async function loadLabeledImages() {
        try {
            // Open the cache
            const cache = await caches.open(cacheName);

            // Get all cached requests
            const cachedRequests = await cache.keys();
            cacheCount = cachedRequests.length;

            // Extract filenames from request URLs
            const imageFiles = cachedRequests.map(request => {
                const url = new URL(request.url);
                return url.pathname.split('/').pop(); // Extract filename from URL path
            });

            // Load and process images from cache
            return await Promise.all(
                imageFiles.map(async (fileName) => {
                    const label = formatFilename(fileName);
                    const cacheKey = new Request(`/${fileName}`); // Adjust the path based on where the file is cached
                    const cachedResponse = await cache.match(cacheKey);

                    if (!cachedResponse) {
                        throw new Error(`Image ${fileName} not found in cache.`);
                    }

                    const imgBlob = await cachedResponse.blob();
                    const img = await faceapi.bufferToImage(imgBlob);
                    const fullFaceDescription = await faceapi.detectSingleFace(img, new faceapi.TinyFaceDetectorOptions())
                        .withFaceLandmarks()
                        .withFaceDescriptor();

                        if (!fullFaceDescription || !fullFaceDescription.descriptor) {
                            return null; // Skip processing if no valid face descriptor is found
                        }
                  
                    const faceDescriptors = [fullFaceDescription.descriptor];
                    return new faceapi.LabeledFaceDescriptors(label, faceDescriptors);
                })
            );
        } catch (error) {
            console.error('Error loading labeled images:', error);
        }
    }

    // Function to format the filename into a readable label
    function formatFilename(filename) {
        // Remove the file extension
        const nameWithoutExtension = filename.replace(/\.[^/.]+$/, '');

        // Handle the case where there is a duplicate suffix
        const baseName = nameWithoutExtension.replace(/-\d+$/, '');

        // Split the base name into parts
        const parts = baseName.split('-');

        // Extract and format the parts
        if (parts.length >= 3) {
            const firstName = capitalize(parts[0]);
            const lastName = capitalize(parts[1]);
            const relation = capitalize(parts.slice(2).join(' ')); // Handle multiple parts if needed

            return `${firstName} ${lastName} (${relation})`;
        } else {
            return nameWithoutExtension; // Fallback if the format is unexpected
        }
    }

    // Helper function to capitalize the first letter of each word
    function capitalize(str) {
        return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
    }

    labeledFaceDescriptors = await loadLabeledImages();

    const validLabeledFaceDescriptors = labeledFaceDescriptors.filter(
        descriptor => descriptor !== null && descriptor.descriptors.length > 0
    );

    // Initialize FaceMatcher only if there are valid descriptors
    if (validLabeledFaceDescriptors.length > 0) {
        try {
            faceMatcher = new faceapi.FaceMatcher(validLabeledFaceDescriptors, 0.6);
        } catch (error) {
            console.error('Error initializing FaceMatcher:', error);
        }
    } else {
        console.warn('No valid face descriptors available for FaceMatcher initialization.');
    }
    processingMessage.style.display = 'none';

    const displaySize = { width: webCamElement.getBoundingClientRect().width, height: webCamElement.getBoundingClientRect().height };
    faceapi.matchDimensions(canvasElement, displaySize);

    setInterval(async () => {
        // SsdMobilenetv1Options   // TinyFaceDetectorOptions
        const detections = await faceapi.detectAllFaces(webCamElement, new faceapi.TinyFaceDetectorOptions())
            .withFaceLandmarks()
            .withFaceDescriptors();
        const resizedDetections = faceapi.resizeResults(detections, displaySize);
        canvasElement.getContext('2d').clearRect(0, 0, canvasElement.width, canvasElement.height);

        resizedDetections.forEach(detection => {
            const box = detection.detection.box;
            if (faceMatcher) {
                const bestMatch = faceMatcher.findBestMatch(detection.descriptor);
                const text = bestMatch.toString();
                const drawBox = new faceapi.draw.DrawBox(box, { label: text });
                drawBox.draw(canvasElement);
            }
            else {
                const text = "Unkown";
                const drawBox = new faceapi.draw.DrawBox(box, { label: text });
                drawBox.draw(canvasElement);
            }
        });
    }, 100);


}
startFaceRecognition();
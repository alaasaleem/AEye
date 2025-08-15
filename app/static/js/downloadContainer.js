import { cacheName } from "./constants.js";

const accountName = 'aeyestorageacc';
let sasToken;
const batchSize = 15; // Number of files to download concurrently

export async function downloadContainer(containerName) {
    try {
        await fetch('/getSasToken', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ container: containerName })
        })
        .then(async response =>await response.json())
        .then(data => {
            if(data.success){
                sasToken=data.sasToken
            }
            else {
                return [];
            }
        });
        // Construct the URL to fetch the list of blobs
        const url = `https://${accountName}.blob.core.windows.net/${containerName}?restype=container&comp=list&${sasToken}`;
        const response = await fetch(url);
        if (!response.ok) {
            return [];
        }
        const xml = await response.text();
        const blobs = parseBlobsFromXml(xml);

        // Open the cache
        const cache = await caches.open(cacheName);

        // Process blobs in batches
        await processBlobsInBatches(blobs, cache, containerName);
        console.log('All files have been downloaded and cached.');
    } catch (error) {
        console.error('Error during download and cache:', error);
    }
}

function parseBlobsFromXml(xml) {
    const parser = new DOMParser();
    const xmlDoc = parser.parseFromString(xml, "application/xml");
    return Array.from(xmlDoc.getElementsByTagName("Name")).map(node => ({
        name: node.textContent
    }));
}

async function processBlobsInBatches(blobs, cache, containerName) {
    for (let i = 0; i < blobs.length; i += batchSize) {
        const batch = blobs.slice(i, i + batchSize);
        await Promise.all(batch.map(blob => downloadAndCacheFile(blob.name, cache, containerName)));
        console.log(`Processed batch ${Math.floor(i / batchSize) + 1}`);
    }
}

async function downloadAndCacheFile(blobName, cache, containerName) {
    try {
        const fileUrl = `https://${accountName}.blob.core.windows.net/${containerName}/${blobName}?${sasToken}`;
        
        // Check cache first
        const cachedResponse = await cache.match(blobName);
        if (cachedResponse) {
            console.log(`Skipping ${blobName}, already cached.`);
            return;
        }

        // Download the file
        const response = await fetch(fileUrl);
        if (!response.ok) {
            throw new Error(`Failed to fetch ${blobName}`);
        }
        const blob = await response.blob();

        // Cache the file
        await cache.put(blobName, new Response(blob));
        console.log(`Downloaded and cached ${blobName}.`);
    } catch (error) {
        console.error(`Error downloading and caching ${blobName}:`, error);
    }}
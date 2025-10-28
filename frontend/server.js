const express = require('express');
const path = require('path');
const fetch = require('node-fetch');

const app = express();
const PORT = process.env.PORT || 3000;
// Backend URL for server-side requests
const BACKEND_URL = process.env.BACKEND_URL_EXTERNAL || 'http://localhost:5000';

// Microsoft Graph API configuration
const GRAPH_API_ENDPOINT = 'https://graph.microsoft.com/v1.0';

// Azure Storage configuration for profile images
const STORAGE_BASE_URL = process.env.STORAGE_BASE_URL || 'https://azuretest001profiles.blob.core.windows.net';
const PROFILE_IMAGES_URL = `${STORAGE_BASE_URL}/profile-images`;
const MAPPING_CSV_URL = `${STORAGE_BASE_URL}/mappings/profile_image_mapping.csv`;
const TENANT_ID = process.env.TENANT_ID;
const CLIENT_ID = process.env.CLIENT_ID;
const CLIENT_SECRET = process.env.CLIENT_SECRET;

// Cache for access token
let cachedToken = null;
let tokenExpiry = null;

// Function to get access token using client credentials
async function getAccessToken() {
    // Return cached token if still valid
    if (cachedToken && tokenExpiry && Date.now() < tokenExpiry) {
        return cachedToken;
    }

    try {
        const tokenEndpoint = `https://login.microsoftonline.com/${TENANT_ID}/oauth2/v2.0/token`;
        
        const params = new URLSearchParams();
        params.append('client_id', CLIENT_ID);
        params.append('client_secret', CLIENT_SECRET);
        params.append('scope', 'https://graph.microsoft.com/.default');
        params.append('grant_type', 'client_credentials');

        const response = await fetch(tokenEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: params
        });

        if (!response.ok) {
            const error = await response.text();
            throw new Error(`Failed to get access token: ${error}`);
        }

        const data = await response.json();
        cachedToken = data.access_token;
        // Set expiry to 5 minutes before actual expiry
        tokenExpiry = Date.now() + ((data.expires_in - 300) * 1000);
        
        return cachedToken;
    } catch (error) {
        console.error('Error getting access token:', error);
        throw error;
    }
}

// Serve static files
app.use(express.static(path.join(__dirname, 'public')));
app.use(express.json({ limit: '10mb' })); // Parse JSON bodies with larger limit for images

// API proxy endpoint - frontend server calls backend, then returns to browser
app.get('/api/health', async (req, res) => {
    try {

        const response = await fetch(`${BACKEND_URL}/health`);
        const data = await response.json();
        res.json(data);
    } catch (error) {
        console.error('Error fetching from backend:', error);
        res.status(500).json({ 
            error: 'Backend unreachable',
            message: error.message,
            backend_url: BACKEND_URL
        });
    }
});

// Get user count from Microsoft Graph API
app.get('/api/users/count', async (req, res) => {
    try {
        console.log('Attempting to get access token...');
        console.log(`Tenant: ${TENANT_ID}, ClientID: ${CLIENT_ID}, Has Secret: ${!!CLIENT_SECRET}`);
        
        // Get access token using client credentials
        const accessToken = await getAccessToken();
        
        console.log('Access token obtained successfully');
        

        
        // Query Microsoft Graph for user count
        const response = await fetch(`${GRAPH_API_ENDPOINT}/users/$count`, {
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'ConsistencyLevel': 'eventual'
            }
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Graph API error:', response.status, errorText);
            return res.status(response.status).json({ 
                error: 'Failed to fetch user count',
                message: errorText,
                status: response.status
            });
        }

        const count = await response.text();
        console.log(`User count retrieved: ${count}`);
        res.json({ 
            count: parseInt(count),
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        console.error('Error fetching user count:', error);
        res.status(500).json({ 
            error: 'Failed to fetch user count',
            message: error.message
        });
    }
});

// Get all users with their profile photos from Azure Storage
app.get('/api/users/profiles', async (req, res) => {
    try {
        console.log('Loading profiles from Azure Storage...');
        

        
        // Fetch the CSV mapping file
        const csvResponse = await fetch(MAPPING_CSV_URL);
        
        if (!csvResponse.ok) {
            console.error('Failed to fetch CSV:', csvResponse.status);
            return res.status(csvResponse.status).json({ 
                error: 'Failed to fetch mapping CSV',
                message: await csvResponse.text()
            });
        }

        const csvText = await csvResponse.text();
        console.log('CSV fetched successfully');
        
        // Parse CSV (simple parsing - assumes no commas in fields)
        const lines = csvText.trim().split('\n');
        const headers = lines[0].split(',');
        
        const users = lines.slice(1).map(line => {
            // Handle potential commas in display names by using regex
            const matches = line.match(/(?:\"([^\"]*)\"|([^,]*))(,|$)/g);
            const values = matches.map(m => m.replace(/,$/g, '').replace(/^\"|\"$/g, ''));
            
            const userId = values[0];
            const displayName = values[1];
            const userPrincipalName = values[2];
            const imageType = values[3];
            const imagePath = values[4];
            
            let photoUrl = null;
            let hasPhoto = false;
            
            if (imageType !== 'no_pic' && imagePath) {
                photoUrl = `${PROFILE_IMAGES_URL}/${imagePath.split('/')[1]}`; // Extract filename from path
                hasPhoto = true;
            }
            
            return {
                id: userId,
                displayName: displayName,
                userPrincipalName: userPrincipalName,
                imageType: imageType,
                photo: photoUrl,
                hasPhoto: hasPhoto
            };
        });

        console.log(`Loaded ${users.length} user profiles`);
        console.log(`Profiles with photos: ${users.filter(u => u.hasPhoto).length}`);
        
        res.json({
            users: users,
            total: users.length,
            withPhotos: users.filter(u => u.hasPhoto).length,
            timestamp: new Date().toISOString()
        });
        
    } catch (error) {
        console.error('Error loading profiles:', error);
        res.status(500).json({ 
            error: 'Failed to load profiles',
            message: error.message
        });
    }
});

// In-memory storage for corrections
let corrections = {};

// Get weekly analytics data
app.get('/api/analytics/weekly', async (req, res) => {
    try {
        const fs = require('fs');
        const path = require('path');
        const csvPath = path.join(__dirname, 'data', 'weekly_analytics.csv');
        
        if (!fs.existsSync(csvPath)) {
            return res.status(404).json({ error: 'Analytics data not found' });
        }
        
        const csvText = fs.readFileSync(csvPath, 'utf8');
        const lines = csvText.trim().split('\n');
        const headers = lines[0].split(',');
        
        const data = lines.slice(1).map(line => {
            const values = line.split(',');
            return {
                week: parseInt(values[0]),
                weekStartDate: values[1],
                human: parseInt(values[2]),
                avatar: parseInt(values[3]),
                other: parseInt(values[4]),
                noPic: parseInt(values[5])
            };
        });
        
        res.json({ data, timestamp: new Date().toISOString() });
    } catch (error) {
        console.error('Error loading analytics:', error);
        res.status(500).json({ error: 'Failed to load analytics', message: error.message });
    }
});

// Classify all profiles
app.post('/api/classify/all-profiles', async (req, res) => {
    try {
        console.log('Loading profiles for classification...');
        
        // Fetch the CSV mapping file
        const csvResponse = await fetch(MAPPING_CSV_URL);
        
        if (!csvResponse.ok) {
            return res.status(csvResponse.status).json({ 
                error: 'Failed to fetch mapping CSV'
            });
        }

        const csvText = await csvResponse.text();
        const lines = csvText.trim().split('\n');
        
        const users = lines.slice(1).map(line => {
            const matches = line.match(/(?:\"([^\"]*)\"|([^,]*))(,|$)/g);
            const values = matches.map(m => m.replace(/,$/g, '').replace(/^\"|\"$/g, ''));
            
            const userId = values[0];
            const displayName = values[1];
            const userPrincipalName = values[2];
            const imageType = values[3];
            const imagePath = values[4];
            
            let photoUrl = null;
            let hasPhoto = false;
            let classification = 'no_pic';
            
            if (imageType !== 'no_pic' && imagePath) {
                photoUrl = `${PROFILE_IMAGES_URL}/${imagePath.split('/')[1]}`;
                hasPhoto = true;
                classification = null; // Will be classified
            }
            
            return {
                id: userId,
                displayName: displayName,
                userPrincipalName: userPrincipalName,
                imageType: imageType,
                photo: photoUrl,
                hasPhoto: hasPhoto,
                classification: classification
            };
        });

        console.log(`Loaded ${users.length} users for classification`);
        
        // Classify images that have photos
        const usersWithPhotos = users.filter(u => u.hasPhoto);
        console.log(`Classifying ${usersWithPhotos.length} profiles with photos...`);
        
        for (const user of usersWithPhotos) {
            try {
                console.log(`[CLASSIFY] Processing ${user.displayName}`);
                console.log(`[CLASSIFY] Image URL: ${user.photo}`);
                
                // Fetch the image directly from Azure Storage
                const imageResponse = await fetch(user.photo);
                if (!imageResponse.ok) {
                    console.error(`[CLASSIFY] Failed to fetch image for ${user.displayName}: ${imageResponse.status}`);
                    user.classification = 'error';
                    user.confidence = 0;
                    continue;
                }
                
                // Convert to base64
                const buffer = await imageResponse.buffer();
                const base64 = buffer.toString('base64');
                const contentType = imageResponse.headers.get('content-type') || 'image/jpeg';
                const dataUrl = `data:${contentType};base64,${base64}`;
                
                console.log(`[CLASSIFY] Got image (${buffer.length} bytes), calling backend for ${user.displayName}`);
                
                // Call backend to classify with base64 image
                const classifyResponse = await fetch(`${BACKEND_URL}/classify`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ image: dataUrl })
                });
                
                console.log(`[CLASSIFY] Backend response status: ${classifyResponse.status} ${classifyResponse.statusText}`);
                
                if (classifyResponse.ok) {
                    const result = await classifyResponse.json();
                    console.log(`[CLASSIFY] Result for ${user.displayName}: ${result.classification} (${result.confidence})`);
                    // Map 'animal' to 'other' for frontend compatibility
                    user.classification = result.classification === 'animal' ? 'other' : result.classification;
                    user.confidence = result.confidence;
                } else {
                    const errorText = await classifyResponse.text();
                    console.error(`[CLASSIFY] Backend error for ${user.displayName}: ${classifyResponse.status} - ${errorText}`);
                    user.classification = 'error';
                    user.confidence = 0;
                }
            } catch (error) {
                console.error(`[CLASSIFY] Error classifying ${user.displayName}:`, error.message);
                user.classification = 'error';
                user.confidence = 0;
            }
        }
        
        res.json({
            users: users,
            total: users.length,
            classified: usersWithPhotos.length,
            timestamp: new Date().toISOString()
        });
        
    } catch (error) {
        console.error('Error classifying profiles:', error);
        res.status(500).json({ 
            error: 'Failed to classify profiles',
            message: error.message
        });
    }
});

// Save correction
app.post('/api/corrections', async (req, res) => {
    try {
        const { userId, originalClassification, correctedClassification } = req.body;
        
        if (!userId || !correctedClassification) {
            return res.status(400).json({ error: 'Missing required fields' });
        }
        
        corrections[userId] = {
            originalClassification,
            correctedClassification,
            timestamp: new Date().toISOString()
        };
        
        console.log(`Saved correction for user ${userId}: ${originalClassification} -> ${correctedClassification}`);
        
        res.json({ success: true, corrections: Object.keys(corrections).length });
    } catch (error) {
        console.error('Error saving correction:', error);
        res.status(500).json({ error: 'Failed to save correction', message: error.message });
    }
});

// Get non-human report
app.get('/api/reports/non-human', async (req, res) => {
    try {
        // Get all classified profiles (from cache or re-classify)
        // For now, return structure - in production this would query the classification results
        
        res.json({
            report: 'non-human',
            users: [
                // This will be populated when classifications are run
            ],
            totalCount: 0,
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        console.error('Error generating non-human report:', error);
        res.status(500).json({ error: 'Failed to generate report', message: error.message });
    }
});

// Get misclassification report
app.get('/api/reports/misclassified', async (req, res) => {
    try {
        const misclassifications = [];
        
        for (const [userId, correction] of Object.entries(corrections)) {
            misclassifications.push({
                userId,
                ...correction
            });
        }
        
        res.json({
            report: 'misclassified',
            misclassifications: misclassifications,
            totalMisclassified: misclassifications.length,
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        console.error('Error generating misclassification report:', error);
        res.status(500).json({ error: 'Failed to generate report', message: error.message });
    }
});

// Serve static HTML file
app.use(express.static('public'));

// Redirect root to index.html
app.get('/', (req, res) => {
    res.sendFile(__dirname + '/public/index.html');
});

// Image proxy endpoint - fetches images from Azure Storage and converts to base64
app.get('/api/proxy-image', async (req, res) => {
    try {
        const { url } = req.query;
        
        if (!url) {
            console.error('[PROXY] No URL provided');
            return res.status(400).json({ 
                error: 'No image URL provided' 
            });
        }
        
        console.log(`[PROXY] Fetching image from: ${url}`);
        const response = await fetch(url);
        console.log(`[PROXY] Response status: ${response.status} ${response.statusText}`);
        
        if (!response.ok) {
            console.error(`[PROXY] Failed to fetch: ${response.status} ${response.statusText}`);
            return res.status(response.status).json({ 
                error: `Failed to fetch image: ${response.status} ${response.statusText}` 
            });
        }
        
        const buffer = await response.buffer();
        console.log(`[PROXY] Buffer size: ${buffer.length} bytes`);
        const base64 = buffer.toString('base64');
        const contentType = response.headers.get('content-type') || 'image/jpeg';
        const dataUrl = `data:${contentType};base64,${base64}`;
        
        console.log(`[PROXY] Successfully proxied image (${contentType})`);
        res.json({ dataUrl });
    } catch (error) {
        console.error('[PROXY] Error proxying image:', error.message);
        console.error('[PROXY] Stack:', error.stack);
        res.status(500).json({ 
            error: 'Failed to proxy image',
            message: error.message
        });
    }
});

// Classify image endpoint - proxies to backend
app.post('/api/classify', async (req, res) => {
    try {
        const { image } = req.body;
        
        if (!image) {
            return res.status(400).json({ 
                error: 'No image data provided' 
            });
        }
        

        const response = await fetch(`${BACKEND_URL}/classify`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ image })
        });
        
        if (!response.ok) {
            const error = await response.json();
            return res.status(response.status).json(error);
        }
        
        const data = await response.json();
        res.json(data);
    } catch (error) {
        console.error('Error classifying image:', error);
        res.status(500).json({ 
            error: 'Failed to classify image',
            message: error.message
        });
    }
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Frontend server running on port ${PORT}`);
    console.log(`Backend URL configured as: ${BACKEND_URL}`);
    console.log(`Graph API Config - Tenant: ${TENANT_ID}, ClientID: ${CLIENT_ID}, Has Secret: ${!!CLIENT_SECRET}`);
});

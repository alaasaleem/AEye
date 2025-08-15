# AEye - AI Vision System for Low Vision Individuals

<p align="center">
  <img src="https://github.com/alaasaleem/AEye/blob/main/app/static/images/logo.png?raw=true" alt="AEye Logo" width="600"/>
</p>


## 🎯 Project Overview

AEye is an innovative AI-powered vision assistance system designed to enhance independence and improve the quality of life for individuals with low vision. By leveraging Microsoft Azure AI services, our system provides voice-controlled assistance for daily tasks through object detection, text reading, and facial recognition capabilities.

## 👥 Team

- [Ahmad Ghazawneh](https://github.com/ahmadghz17)
- [Alaa Saleem](https://github.com/alaasaleem)
- [Baraa Khanfar](https://github.com/baraakh30)
- [Hala Gholeh](https://github.com/HalaGholeh)
- [Jamila Fawaqa](https://github.com/JamilaFawaqa)

## 📊 Team Contribution Breakdown

<table>
<thead>
<tr>
<th style="text-align:left;">Task Type</th>
<th style="text-align:center;">% of Total Project</th>
<th style="text-align:center;">Ahmad</th>
<th style="text-align:center;">Alaa</th>
<th style="text-align:center;">Baraa</th>
<th style="text-align:center;">Hala</th>
<th style="text-align:center;">Jamila</th>
</tr>
</thead>
<tbody>
<tr>
<td>🎨 <b>Frontend</b></td>
<td style="text-align:center; color:#00bfff;"><b>35.4%</b></td>
<td style="text-align:center;">37.5%</td>
<td style="text-align:center;">33.3%</td>
<td style="text-align:center;">34.4%</td>
<td style="text-align:center; background-color:#ffe4e1;"><b>66.7%</b></td>
<td style="text-align:center;">55.6%</td>
</tr>
<tr>
<td>⚙️ <b>Backend</b></td>
<td style="text-align:center; color:#00bfff;"><b>44.6%</b></td>
<td style="text-align:center;">50.0%</td>
<td style="text-align:center;">55.6%</td>
<td style="text-align:center;">34.4%</td>
<td style="text-align:center;">16.7%</td>
<td style="text-align:center;">44.4%</td>
</tr>
<tr>
<td>🤖 <b>AI Services</b></td>
<td style="text-align:center; color:#00bfff;"><b>16.6%</b></td>
<td style="text-align:center;">12.5%</td>
<td style="text-align:center;">11.1%</td>
<td style="text-align:center; background-color:#e6ffe6;"><b>31.2%</b></td>
<td style="text-align:center;">-</td>
<td style="text-align:center;">-</td>
</tr>
<tr>
<td>🗄️ <b>Database</b></td>
<td style="text-align:center; color:#00bfff;"><b>3.1%</b></td>
<td style="text-align:center;">-</td>
<td style="text-align:center;">-</td>
<td style="text-align:center;">-</td>
<td style="text-align:center; background-color:#ffffcc;"><b>16.7%</b></td>
<td style="text-align:center;">-</td>
</tr>
</tbody>
</table>

> **Notes:**  
> - Column **"% of Total Project"** = percentage of this task type from the overall project.  
> - Numbers next to each member's name = percentage of this task type from that member’s own tasks.  
> - `-` means no contribution in that task type.

## 🚀 Motivation

People with low vision face daily challenges that:
- Compromise their independence
- Increase the risk of accidents  
- Require constant assistance
- Limit their ability to perform routine tasks confidently

Our solution addresses these challenges by providing an intelligent, voice-controlled assistant that acts as digital eyes.

## ✨ Features

### Core MVP Features

#### 🔍 Object Detection
- **Voice Input**: Users speak the name of an object they're looking for
- **Smart Detection**: AI analyzes the camera feed to locate the requested object
- **Audio Feedback**: Provides voice guidance on the object's location (e.g., "The object is at the top-right of the image")
- **Visual Feedback**: Draws bounding boxes around detected objects

#### 📖 Text Reading (OCR)
- Users request text reading from images
- Advanced OCR technology extracts text from captured images
- Converts extracted text to speech with natural voice synthesis
- Provides feedback when text cannot be detected

#### 👤 Facial Recognition
- **Add Person Feature**: 
  - Voice-guided process to add new faces to the system
  - Captures and stores facial data with names and relationships
  - Multilingual name support with Arabic pronunciation
- **Real-time Recognition**:
  - Live detection of known faces through camera feed
  - Visual labels with bounding boxes around recognized faces
  - Audio announcements of recognized individuals

#### 🔄 Repeat Last Action
- Automatically stores the last performed action
- Users can say "repeat" to re-execute the previous command
- Maintains context across interactions

## 🛠 Technology Stack

### Frontend
- **HTML5/CSS3/JavaScript**: web interface
- **Face-API.js**: Client-side facial recognition processing
- **Canvas API**: Real-time video processing and overlay graphics
- **Web APIs**: Camera access and media handling

### Backend
- **Python Flask**: RESTful web server
- **SQLite3**: Local database for user management
- **Azure SDK**: Integration with Microsoft AI services

### AI & Cloud Services
- **Azure Cognitive Services**:
  - Speech-to-Text & Text-to-Speech
  - Computer Vision (OCR)
  - AI Vision (Object Detection)
  - Language Understanding (LUIS/CLU)
- **Azure Blob Storage**: Secure image and user data storage
- **Bing Search API**: Spell checking and validation

### Machine Learning
- **spaCy**: Natural language processing
- **YOLO v8**: Advanced object detection model
- **Custom NLP Models**: Intent recognition and entity extraction

## 🏗 Architecture

### System Architecture
<p align="center">
<img src=https://github.com/alaasaleem/AEye/blob/main/app/static/images/Architecture.png?raw=true" alt="AEye Logo" width="800"/>
</p>

### Protocols
- **HTTP/HTTPS**: Web communication
- **Azure SDKs**: Cloud service integration
- **WebRTC**: Real-time camera access

## 🎯 Development Methodology

### Process Model: Scrum
- **Daily Scrum Meetings**: Regular team coordination
- **Sprint Planning**: Feature-focused development cycles
- **Iterative Development**: Continuous improvement and testing

### Key Learnings
- Improved task division and estimation
- Importance of thorough code reviews
- Regular issue addressing in daily meetings
- Avoiding task duplication across team members

## 🔮 Future Roadmap

### Planned Enhancements
- **Navigation Assistant**: GPS integration for outdoor guidance
- **Enhanced Multilingual Support**: Additional language packs
- **Custom Object Detection**: User-trainable object recognition
- **Sign Detection Model**: Traffic and informational sign reading
- **Mobile Application**: Native iOS/Android apps
- **Offline Capabilities**: Local processing for privacy

### Hardware Integration
- **Dedicated Device**: Custom wearable or handheld device
- **Camera Optimization**: Specialized cameras for better detection
- **Audio Enhancement**: Directional audio feedback

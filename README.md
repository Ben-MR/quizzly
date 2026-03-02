# Quizly Project - Backend

Quizly is a robust Django-based backend application that automates the process of creating educational content. By leveraging the power of Google Gemini AI, the application transforms YouTube videos into interactive quizzes.

Users simply provide a YouTube URL, and the system handles the audio extraction, transcription analysis, and quiz generation (including titles, descriptions, and multiple-choice questions) in a matter of seconds.

## Core Features
* **AI Quiz Generation**: Automatically creates quizzes from YouTube audio using Gemini 1.5 Flash.
* **Secure Authentication**: Implements JWT (JSON Web Token) authentication stored in HTTP-only cookies for enhanced security.
* **Question Management**: Full CRUD (Create, Read, Update, Delete) functionality for quizzes and questions.
* **Ownership Control**: Quizzes are linked to user accounts, ensuring that only creators can modify or delete their content.

## Tech Stack
* **Framework**: Django & Django REST Framework (DRF)
* **AI Integration**: Google Generative AI (Gemini API)
* **Authentication**: SimpleJWT (with Cookie-based implementation)
* **Media Processing**: yt-dlp (Audio extraction) & FFmpeg
* **Database**: SQLite (Development) / PostgreSQL (Optional Production)

## System Dependencies
### Core Web Framework
* **Django (6.0.2) & Django REST Framework (3.16.1)**: The backbone of the API.
* **python-dotenv**: For secure management of environment variables.

### AI & Google Integration
* **google-generativeai (0.8.6)**: The official SDK to interact with Gemini 1.5 Flash.
* **google-genai (1.65.0)**: Enhanced support for Google's latest generative models.
* **protobuf & grpcio**: High-performance communication layers for Google APIs.

### Authentication (JWT & Cookies)
* **djangorestframework-simplejwt (5.5.1)**: Handles JSON Web Token generation.
* **PyJWT (2.11.0)**: Core library for encoding and decoding tokens.
* **cryptography**: Ensures secure encryption for authentication processes.

### Media & Video Processing
* **yt-dlp (2026.2.21)**: Powerful utility for downloading and extracting audio from YouTube.
* **FFmpeg (External dependency)**: Required by yt-dlp for audio transcoding.

## Installation

Clone the project:

``` bash
git clone git@github.com:Ben-MR/quizly.git
cd quizly
```

## Create Virtual Environment

### Create

``` bash
python -m venv venv
```

### Activate (Linux/Mac)

``` bash
source venv/bin/activate
```

### Activate (Windows)

``` bash
venv\Scripts\activate
```

## Install Dependencies

``` bash
pip install -r requirements.txt
```

### Initialize Database

``` bash
python manage.py makemigrations
python manage.py migrate
```

### Start Server

``` bash
python manage.py runserver
```

The API is now accessible at http://127.0.0.1:8000.

## Create Superuser (Admin)

The project supports the default Django command for creating
administrators:

``` bash
python manage.py createsuperuser
```

A corresponding UserProfile is created and correctly assigned
automatically.

## Project Structure
``` bash
quizly-backend/
├── core/                  # Project settings and WSGI/ASGI configuration
├── authentication/        # User and session management
│   ├── api/               # API Layer
│   │   ├── serializers.py # Registration and Token serializers
│   │   ├── views.py       # Auth endpoints (Login, Logout, Register)
│   │   └── urls.py        # Auth routing
│   └── models.py          # Custom user models (if applicable)
├── quiz/                  # Main quiz application
│   ├── api/               # API Layer
│   │   ├── serializers.py # Quiz and Question serializers
│   │   ├── views.py       # Quiz CRUD and AI logic
│   │   └── urls.py        # Quiz routing
│   ├── models.py          # Database schema for Quizzes and Questions
│   └── utils.py           # Gemini AI and Media processing helpers
├── media/                 # Temporary storage for YouTube audio
├── .env                   # Environment variables (API keys)
├── manage.py
└── requirements.txt
```

## Security & Authentication Concept
* **HTTP-Only Cookies**: JWT Access and Refresh tokens are stored in secure cookies. This prevents XSS (Cross-Site Scripting) attacks as the tokens are inaccessible via client-side JavaScript.
* **CSRF Mitigatio**n: Using samesite='Lax' provides a robust baseline protection against Cross-Site Request Forgery.
* **Token Rotation & Blacklisting**: Every session refresh provides a new access token, and logging out immediately invalidates the refresh token via a database-backed blacklist.

## AI Logic & Processing
* **Extraction**: yt-dlp extracts high-quality audio (.m4a) from the provided YouTube URL.
* **AI Analysis**: The audio file is uploaded to the Google Gemini 1.5 Flash model.
* **Prompt Engineering**: A specialized system prompt ensures the AI returns data strictly in a structured JSON format.
* **Database Integration**: The backend parses the AI response using Regex and maps it to the Django models (Quiz and Questions).

## External Dependency: FFmpeg
This project requires FFmpeg to process and convert YouTube video streams into high-quality audio files (.m4a). Without it, the yt-dlp library will fail to extract the audio track.

### Installation Instructions
### Windows
1. Download the latest build from Gyan.dev.
2. Extract the folder and move it to a permanent location (e.g., C:\ffmpeg).
3. Add the bin folder to your System Path (Environment Variables).
4. Verify by running ffmpeg -version in your terminal.

### macOS
Install via Homebrew:


``` bash
brew install ffmpeg
Linux (Ubuntu/Debian)
```

Install via APT:

``` bash
sudo apt update
sudo apt install ffmpeg

### Filtering (Sidebar Support)
The quiz list endpoint supports time-based filtering via query parameters:
- `GET /api/quizzes/?filter=today` - Retrieves quizzes created within the current day.
- `GET /api/quizzes/?filter=week` - Retrieves quizzes from the last 7 days.

## License

This project was created as a learning project and is currently not
under any specific license.

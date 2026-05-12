# Manga Reader Web

A modern, fast, and serverless-oriented Progressive Web App (PWA) for reading Manga in PDF format. Built with FastAPI, PDF.js, and Backblaze B2 cloud storage.

## Features

- **Cloud Storage Integration**: Reads and streams manga seamlessly from Backblaze B2 (S3-compatible).
- **Direct Cloud Upload**: Upload new manga PDFs directly from the browser to the B2 bucket using presigned URLs without proxying through the app server.
- **Offline Mode & PWA**: Installs on mobile devices as a native-like app. Uses Service Workers and the Cache API to save downloaded manga locally, eliminating repeat data usage and ensuring offline availability.
- **High Performance & Prefetching**: Renders PDFs in chunks via `pdf.js`. Automatically prefetches the next pages in the background for zero-lag reading.
- **Mobile Optimized**:
  - Hammer.js integration for left/right swipe navigation.
  - High-DPI (Retina) Canvas rendering for crystal-clear text on modern smartphone screens.
  - Granular zoom functionality.
- **Smart Progress Tracking**: 
  - Saves your current volume to the cloud.
  - Remembers your exact pixel scroll position locally via `localStorage` so you return exactly where you left off.

## Tech Stack

- **Backend**: Python, FastAPI, `boto3` (AWS S3 SDK)
- **Frontend**: HTML5, Vanilla JavaScript, CSS3
- **Libraries**: PDF.js, Hammer.js
- **Infrastructure**: Render.com (App Hosting), Backblaze B2 (Object Storage)

## Local Setup

1. Clone the repository.
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory with your Backblaze B2 credentials:
   ```env
   B2_KEY_ID=your_key_id
   B2_APPLICATION_KEY=your_app_key
   B2_ENDPOINT=your_s3_endpoint
   B2_BUCKET_NAME=your_bucket_name
   ```
4. Run the development server:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```
5. Open `http://localhost:8000` in your browser.


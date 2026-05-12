# Changelog

All notable changes to this project will be documented in this file.

## [1.1.0] - 2026-05-12

### Added
- **Direct PDF Upload**: Added the ability to upload new manga volumes directly from the browser to Backblaze B2 using presigned PUT URLs, bypassing server payload limits.
- **Precise Scroll Memory**: Integrated `localStorage` to save the user's exact scroll position (in pixels) with a 500ms debounce. Automatically restores the view to the exact frame after page reloads.

### Changed
- Improved Cloud UI integration: Added an upload button to the top navigation bar with visual feedback (upload progress states).

## [1.0.0] - 2026-05-11

### Added
- **Serverless Migration**: Migrated local storage to Backblaze B2 via `boto3`. Endpoints updated to deliver 2-hour presigned URLs for reading.
- **Render Deployment**: Configured app for cloud hosting on Render.com with environment variables.
- **PWA & Offline Support**: Added `manifest.json` and a Service Worker (`sw.js`) to allow "Add to Home Screen" installation and app shell caching.
- **Smart PDF Caching (Cache API)**: Raw PDF blobs are now cached locally in the browser to bypass repeated network requests, securing offline access and saving cloud bandwidth constraints.
- **High-DPI Support**: Added `devicePixelRatio` scaling to Canvas to fix blurry images on Retina mobile displays.
- **Background Rendering**: Engineered background chunk rendering and 20-page prefetching for zero-latency reading.
- **Swipe Gestures**: Built-in Hammer.js configuration for intuitive previous/next chunk swiping on mobile.

### Removed
- Deprecated Local Streamlit MVP codebase in favor of the new SPA + FastAPI architecture.


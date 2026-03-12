# Family Photos

A web application for organizing and sharing family photos in albums.

## About

Family Photos is a Flask-based photo management system developed as a final project for Harvard Extension's CSCI-E 50. Users can register accounts, create albums, and upload photos with captions.

## Features

- User authentication and registration
- Album creation and management
- Photo uploads with captions
- Album cover photo selection
- Soft delete functionality for photos

## Technology Stack

- **Backend**: Flask, SQLAlchemy
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite
- **Session Management**: Flask-Session
- **Security**: Werkzeug (password hashing)

## Database Schema

- **users**: id, username, email, password_hash
- **albums**: album_id, user_id, album_name
- **photos**: photo_id, user_id, album_id, image_link, caption, is_deleted, is_cover

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
flask run
```

## Notes

- Uploaded images are stored in `static/uploads/`
- Deleted photos are marked as deleted in the database but files remain on disk
- Photo links are stored in the database and rendered dynamically

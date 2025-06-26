<<<<<<< HEAD
# Parcel Info Extractor (Django)

A Django web application for extracting parcel label information using Typhoon OCR and OpenAI.

## Features
- Upload parcel label images or PDFs
- Extract parcel number, recipient name, address, phone, and postal code
- Display results in a modern, responsive UI
- Download extracted data as Excel

## Getting Started
1. Install dependencies:
   ```
   pip install django typhoon-ocr openai pandas openpyxl
   ```
2. Run migrations:
   ```
   python manage.py migrate
   ```
3. Start the server:
   ```
   python manage.py runserver
   ```
4. Open your browser at http://127.0.0.1:8000/

## Project Structure
- `extractor/` : Main Django app for extraction logic and UI
- `parcelinfo/` : Django project settings

## Notes
- Place your Typhoon OCR and OpenAI API keys in environment variables or Django settings as needed.
=======
# Extract-Parcel-Info
>>>>>>> b576470c417f5c6ab251ccdf955dd0abbc599c83

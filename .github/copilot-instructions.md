<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

This is a Django project for parcel label extraction. The main app is 'extractor'.
- Users can upload parcel label images or PDFs.
- The backend uses Typhoon OCR and OpenAI to extract parcel number, recipient name, address, phone, and postal code.
- Results are shown in a modern UI and can be downloaded as Excel.
- Use Django best practices for file upload, view, and template structure.

from flask import Flask, render_template, request, redirect, url_for
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

app = Flask(__name__)

# Configura tu carpeta temporal local (solo mientras se sube)
UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ID de la carpeta en Google Drive (📁 pon aquí la tuya)
DRIVE_FOLDER_ID = "11iZx3uyaOatF9ee1SuY2E7T9FcwTKx5G"

# Cargar las credenciales desde el JSON
SCOPES = ['https://www.googleapis.com/auth/drive']
creds = service_account.Credentials.from_service_account_file(
    'credentials.json', scopes=SCOPES)
service = build('drive', 'v3', credentials=creds)

def upload_to_drive(filepath, filename):
    """Sube un archivo al Drive y devuelve el enlace público."""
    file_metadata = {'name': filename, 'parents': [DRIVE_FOLDER_ID]}
    media = MediaFileUpload(filepath, resumable=True)
    uploaded = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

def list_drive_files():
    """Devuelve una lista de URLs públicas de las imágenes en la carpeta del Drive."""
    results = service.files().list(
        q=f"'{DRIVE_FOLDER_ID}' in parents and trashed=false",
        fields="files(id, name, mimeType)"
    ).execute()

    files = results.get('files', [])
    image_urls = []
    for file in files:
        if file["mimeType"].startswith("image/"):
            image_urls.append(f"https://drive.google.com/uc?id={file['id']}")
        elif file["mimeType"].startswith("video/"):
            image_urls.append(f"https://drive.google.com/file/d/{file['id']}/preview")
    return image_urls

def index():
    if request.method == 'POST':
        files = request.files.getlist('file')
        for file in files:
            if file:
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filepath)
                upload_to_drive(filepath, file.filename)
                os.remove(filepath)  # borra el archivo local
        return redirect(url_for('index'))

    # No necesitamos listar archivos locales
    return render_template('index.html', files=[])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)



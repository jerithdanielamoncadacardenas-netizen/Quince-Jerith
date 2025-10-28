from flask import Flask, render_template, request, redirect, url_for
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import json

app = Flask(__name__)

# Carpeta temporal local (solo mientras se sube)
UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ID de tu carpeta de Google Drive 📁
DRIVE_FOLDER_ID = "11iZx3uyaOatF9ee1SuY2E7T9FcwTKx5G"

# Cargar credenciales desde la variable de entorno
SCOPES = ['https://www.googleapis.com/auth/drive']
creds_info = json.loads(os.getenv('GOOGLE_CREDENTIALS'))
creds = service_account.Credentials.from_service_account_info(creds_info, scopes=SCOPES)
service = build('drive', 'v3', credentials=creds)

# Función para subir a Drive
def upload_to_drive(filepath, filename):
    """Sube un archivo al Drive y lo hace público."""
    file_metadata = {'name': filename, 'parents': [DRIVE_FOLDER_ID]}
    media = MediaFileUpload(filepath, resumable=True)
    uploaded = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    # 🔓 Hacer el archivo público
    service.permissions().create(
        fileId=uploaded.get('id'),
        body={'type': 'anyone', 'role': 'reader'}
    ).execute()

    return uploaded.get('id')

# Función para listar archivos desde Drive
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

# 🌐 Ruta principal
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        files = request.files.getlist('file')
        for file in files:
            if file:
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filepath)
                upload_to_drive(filepath, file.filename)
                os.remove(filepath)
        return redirect(url_for('index'))

    # Mostrar los archivos de Drive en la galería
    files = list_drive_files()
    return render_template('index.html', files=files)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)






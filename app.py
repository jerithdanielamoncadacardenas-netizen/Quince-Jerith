from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join('uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    files = os.listdir(UPLOAD_FOLDER)
    return render_template('index.html', files=files)

@app.route('/upload', methods=['POST'])
def upload():
    files = request.files.getlist('file')
    for file in files:
        if file.filename:
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)
    return redirect(url_for('index'))

@app.route('/delete/<filename>', methods=['POST'])
def delete(filename):
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

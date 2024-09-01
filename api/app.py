import os
import zipfile
from flask import Flask, render_template, request, send_from_directory, send_file
from rembg import remove
from PIL import Image
import io
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/images/'
app.config['PROCESSED_FOLDER'] = 'static/processed/'

# Crear carpetas si no existen
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        uploaded_files = request.files.getlist('image')
        processed_filenames = []

        for file in uploaded_files:
            if file.filename == '':
                continue

            # Procesar la imagen
            img_data = file.read()
            result = remove(img_data)
            img = Image.open(io.BytesIO(result)).convert("RGBA")

            # Crear imagen con fondo blanco
            white_bg = Image.new("RGBA", img.size, "WHITE")
            white_bg.paste(img, (0, 0), img)

            # Convertir a RGB y guardar con un nombre único
            final_img = white_bg.convert("RGB")
            output_filename = str(uuid.uuid4()) + '.jpg'
            output_path = os.path.join(app.config['PROCESSED_FOLDER'], output_filename)
            final_img.save(output_path)
            processed_filenames.append(output_filename)

        return render_template('index.html', uploaded_images=processed_filenames)

    return render_template('index.html')

@app.route('/static/processed/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename)

@app.route('/download_all')
def download_all():
    # Crear un archivo ZIP con todas las imágenes procesadas
    zip_filename = "processed_images.zip"
    zip_path = os.path.join(app.config['PROCESSED_FOLDER'], zip_filename)

    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for root, dirs, files in os.walk(app.config['PROCESSED_FOLDER']):
            for file in files:
                if file != zip_filename:  # No incluir el archivo ZIP en sí mismo
                    zipf.write(os.path.join(root, file), arcname=file)

    return send_file(zip_path, as_attachment=True)
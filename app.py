from flask import Flask, request, jsonify
import trimesh
import requests
import os
import random
import numpy as np
import io
from PIL import Image
from pygltflib import GLTF2
from pygltflib.utils import ImageFormat
from pygltflib.utils import glb2gltf, gltf2glb
import pygltflib
from gltflib import GLTF
import subprocess

app = Flask(__name__)


def glb_to_png(glb_path, png_path):
    command = f"sudo screenshot-glb -i {glb_path} -o {png_path}"
    try:
        subprocess.run(command, shell=True, check=True)
        return png_path
    except subprocess.CalledProcessError as e:
        print(f"Hata: {e}")
        return None

def generate_unique_filename(extension):
    """Belirtilen uzantı için benzersiz bir dosya adı oluşturur."""
    random_prefix = random.randint(1000, 9999)
    return f"model_{random_prefix}.{extension}"

@app.route('/convert', methods=['GET'])
def convert_file():
    url = request.args.get('url')
    
    if not url:
        return jsonify({"error": "URL parametresi gereklidir."}), 400
    
    # Benzersiz dosya isimleri oluştura
    temp_file_name = generate_unique_filename('glb')
    output_file_name = generate_unique_filename('stl')
    output_obj_file_name = generate_unique_filename('obj')
    output_ply_file_name = generate_unique_filename('ply')
    thumbnail_file_name = generate_unique_filename('png')
    
    # Dosyaların kaydedileceği tam yol
    temp_file_path = os.path.join("/var/www/wordpress/magic3d", temp_file_name)
    output_file_path = os.path.join("/var/www/wordpress/magic3d", output_file_name)
    output_obj_file_path = os.path.join("/var/www/wordpress/magic3d", output_obj_file_name)
    output_ply_file_path = os.path.join("/var/www/wordpress/magic3d",output_ply_file_name)
    thumbnail_file_path = os.path.join("/var/www/wordpress/magic3d", thumbnail_file_name)

    
    # URL'den dosyayı indir ve benzersiz isimle kaydet
    response = requests.get(url)
    if response.status_code == 200:
        with open(temp_file_path, 'wb') as f:
            f.write(response.content)
    else:
        return jsonify({"error": "URL'den dosya indirilemedi."}), 400

    # Dosyayı yükle ve istenen formata dönüştür
    try:
        mesh = trimesh.load(temp_file_path)
        mesh.export(output_file_path)
        mesh.export(output_obj_file_path)
        mesh.export(output_ply_file_path)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Dönüştürülen dosyanın URL'ini geri dön
    converted_file_url = f"https://heyzekai.com/magic3d/{output_file_name}"
    converted_file_url_obj = f"https://heyzekai.com/magic3d/{output_obj_file_name}"
    converted_file_url_ply = f"https://heyzekai.com/magic3d/{output_ply_file_name}"

    glb_to_png(temp_file_path, thumbnail_file_path)

    thumbnail_url = f"https://heyzekai.com/magic3d/{thumbnail_file_name}"
    
    return jsonify({"converted_file_url": converted_file_url,"thumbnail_url": thumbnail_url,"converted_file_url_obj":converted_file_url_obj,"converted_file_url_ply":converted_file_url_ply})

if __name__ == '__main__':
    app.run(debug=True,port=8889,host='0.0.0.0')

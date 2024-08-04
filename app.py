from flask import Flask, request, jsonify, send_from_directory
import trimesh
import requests
import os
import random
import subprocess

app = Flask(__name__)

UPLOAD_FOLDER = '/app/assets'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def glb_to_png(glb_path, png_path):
    command = f"screenshot-glb -i {glb_path} -o {png_path}"
    try:
        subprocess.run(command, shell=True, check=True)
        return png_path
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return None

def generate_unique_filename(extension):
    random_prefix = random.randint(1000, 9999)
    return f"model_{random_prefix}.{extension}"

@app.route('/convert', methods=['GET'])
def convert_file():
    url = request.args.get('url')
    
    if not url:
        return jsonify({"error": "URL parameter is required."}), 400
    
    temp_file_name = generate_unique_filename('glb')
    output_file_name = generate_unique_filename('stl')
    output_obj_file_name = generate_unique_filename('obj')
    output_ply_file_name = generate_unique_filename('ply')
    thumbnail_file_name = generate_unique_filename('png')
    
    temp_file_path = os.path.join(UPLOAD_FOLDER, temp_file_name)
    output_file_path = os.path.join(UPLOAD_FOLDER, output_file_name)
    output_obj_file_path = os.path.join(UPLOAD_FOLDER, output_obj_file_name)
    output_ply_file_path = os.path.join(UPLOAD_FOLDER, output_ply_file_name)
    thumbnail_file_path = os.path.join(UPLOAD_FOLDER, thumbnail_file_name)

    response = requests.get(url)
    if response.status_code == 200:
        with open(temp_file_path, 'wb') as f:
            f.write(response.content)
    else:
        return jsonify({"error": "Could not download file from URL."}), 400

    try:
        mesh = trimesh.load(temp_file_path)
        mesh.export(output_file_path)
        mesh.export(output_obj_file_path)
        mesh.export(output_ply_file_path)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    glb_to_png(temp_file_path, thumbnail_file_path)

    converted_file_url = f"/assets/{output_file_name}"
    converted_file_url_obj = f"/assets/{output_obj_file_name}"
    converted_file_url_ply = f"/assets/{output_ply_file_name}"
    thumbnail_url = f"/assets/{thumbnail_file_name}"
    
    return jsonify({"converted_file_url": converted_file_url,
                    "thumbnail_url": thumbnail_url,
                    "converted_file_url_obj": converted_file_url_obj,
                    "converted_file_url_ply": converted_file_url_ply})

@app.route('/assets/<path:filename>', methods=['GET'])
def serve_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True, port=8889, host='0.0.0.0')

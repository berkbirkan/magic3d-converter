from flask import Flask, request, jsonify, send_from_directory
import trimesh
import requests
import os
import random
import subprocess
from PIL import Image
from io import BytesIO_

app = Flask(__name__)

UPLOAD_FOLDER = '/app/assets'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def glb_to_png(glb_path, png_path):
    command = f"DOCKER_IMAGE=bwasty/gltf-viewer ./screenshot_docker.sh {glb_path}"
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

    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(temp_file_path, 'wb') as f:
            f.write(response.content)
    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")
        return jsonify({"error": f"Could not download file from URL. {e}"}), 400

    try:
        mesh = trimesh.load(temp_file_path)
        mesh.export(output_file_path)
        mesh.export(output_obj_file_path)
        mesh.export(output_ply_file_path)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    glb_to_png(temp_file_path, thumbnail_file_path)

    base_url = request.host_url.rstrip('/')
    converted_file_url = f"{base_url}/assets/{output_file_name}"
    converted_file_url_obj = f"{base_url}/assets/{output_obj_file_name}"
    converted_file_url_ply = f"{base_url}/assets/{output_ply_file_name}"
    thumbnail_url = f"{base_url}/assets/{thumbnail_file_name}"
    
    return jsonify({"converted_file_url": converted_file_url,
                    "thumbnail_url": thumbnail_url,
                    "converted_file_url_obj": converted_file_url_obj,
                    "converted_file_url_ply": converted_file_url_ply})



@app.route('/img2glb', methods=['POST'])
def img2glb():
    image_url = request.json.get('image_url')
    api_key = request.json.get('stabilityai_api_key')
    
    if not image_url:
        return jsonify({"error": "Image URL parameter is required."}), 400
    
    temp_image_name = generate_unique_filename('png')
    output_file_name = generate_unique_filename('glb')
    
    temp_image_path = os.path.join(UPLOAD_FOLDER, temp_image_name)
    output_file_path = os.path.join(UPLOAD_FOLDER, output_file_name)

    try:
        response = requests.get(image_url)
        response.raise_for_status()
        
        image = Image.open(BytesIO(response.content))
        width, height = image.size
        pixel_count = width * height
        
        if pixel_count < 4096 or pixel_count > 4194304:
            max_dimension = int((4194304 ** 0.5))  # Calculate max dimension to fit within 4,194,304 pixels
            if width * height > 4194304:
                scale_factor = (max_dimension ** 2 / pixel_count) ** 0.5
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                image = image.resize((new_width, new_height), Image.ANTIALIAS)
            elif width * height < 4096:
                return jsonify({"error": "Image dimensions are too small. Minimum dimension is 4096 pixels."}), 400

        image.save(temp_image_path, 'PNG')
        
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image: {e}")
        return jsonify({"error": f"Could not download image from URL. {e}"}), 400
    except Exception as e:
        print(f"Error processing image: {e}")
        return jsonify({"error": f"Could not process image. {e}"}), 500

    try:
        api_response = requests.post(
            f"https://api.stability.ai/v2beta/3d/stable-fast-3d",
            headers={
                "authorization": f"Bearer {api_key}" ,
            },
            files={
                "image": open(temp_image_path, "rb")
            },
            data={},
        )

        if api_response.status_code == 200:
            with open(output_file_path, 'wb') as file:
                file.write(api_response.content)
        else:
            raise Exception(str(api_response.json()))
    except Exception as e:
        print(f"Error creating GLB: {e}")
        return jsonify({"error": f"Could not create GLB from image. {e}"}), 500

    converted_file_url = f"/assets/{output_file_name}"
    
    return jsonify({"converted_file_url": converted_file_url})

@app.route('/assets/<path:filename>', methods=['GET'])
def serve_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True, port=8889, host='0.0.0.0')

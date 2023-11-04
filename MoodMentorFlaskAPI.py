from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import os

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['POST'])
def recognize():
    # Receive the image from the Flutter app
    image = request.files['image']

    # Save the received image
    image_path = 'received_image.jpg'
    image.save(image_path)

    # Run the LoginMoodMentor.py script on the received image
    try:
        command = f'python LoginMoodMentor.py {image_path}'
        result = subprocess.check_output(command, shell=True)
        result = result.decode('utf-8').strip()
    except Exception as e:
        result = str(e)

    # Delete the temporary image file
    if os.path.exists(image_path):
        os.remove(image_path)

    # Return the result to the Flutter app
    response = {
        'result': result
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

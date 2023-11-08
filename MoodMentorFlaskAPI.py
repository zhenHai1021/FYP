from flask import Flask, request, jsonify
from urllib.parse import urlparse 
import subprocess
import requests
import json
import os
import boto3
import subprocess
import botocore
import sys

app = Flask(__name__)

 # Modify this path if necessary

@app.route('/hello_world', methods=['POST'])
def hello_world():
    try:
        S3_PUBLIC_URL = 'https://facial-login-model-bucket.s3.amazonaws.com/hello_world.py'  # Replace with your S3 bucket URL

        # Define the full path to the Python interpreter
        PYTHON_PATH = '/usr/bin/python3' 
        # Fetch the 'hello_world.py' script from the public S3 URL
        s3_script = requests.get(S3_PUBLIC_URL)
        
        if s3_script.status_code == 200:
            with open('/tmp/hello_world.py', 'wb') as f:
                f.write(s3_script.content)
            
            # Use the full path to the Python interpreter
            result = subprocess.check_output([PYTHON_PATH, '/tmp/hello_world.py'], stderr=subprocess.STDOUT, text=True)
            
            return jsonify({'result': result})
        else:
            return jsonify({'error': f"Failed to fetch 'hello_world.py' from S3: {s3_script.status_code}"})
    except Exception as e:
        return jsonify({'error': str(e)})





@app.route('/recognize', methods=['POST'])
def recognize_face():
    return 'Hi'

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)

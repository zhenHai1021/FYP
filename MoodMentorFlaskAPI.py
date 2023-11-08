from flask import Flask, request, jsonify
from urllib.parse import urlparse 
import subprocess
import requests
import json
import boto3
import botocore
import sys

app = Flask(__name__)

 # Modify this path if necessary

@app.route('/hello_world')
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

# Function to download the script from S3 using the S3 object URL
def download_script_from_s3():
    try:
        import boto3
        from botocore.exceptions import NoCredentialsError, ClientError

        # Initialize the S3 client
        s3 = boto3.client('s3')

        # Extract the S3 bucket and key from the S3 object URL
        S3_BUCKET_NAME = 'facial-login-model-bucket'
        S3_SCRIPT_KEY = 'LoginMoodMentor.py'

        # Download the script and save it as 'LoginMoodMentorTmp.py'
        s3.download_file(S3_BUCKET_NAME, S3_SCRIPT_KEY, 'LoginMoodMentor.py')
        return None
    except NoCredentialsError:
        return "S3 credentials not found"
    except ClientError as e:
        return f"Error downloading script from S3 in API: {str(e)}"



@app.route('/recognize', methods=['POST'])
def recognize_face():
    # Receive image data from the client (e.g., a mobile app)
    image_data = request.data

    # Save the received image data as an image file (you can modify this part if needed)
    with open('captured_frame.jpg', 'wb') as image_file:
        image_file.write(image_data)

    # Download the script from S3
    #s3_download_error = download_script_from_s3()

    #if s3_download_error:
    #    return jsonify({"error": s3_download_error})
     
    # Specify the full path to your Python interpreter
    python_path = '/usr/bin/python3' # Replace with the actual path
    # Execute the downloaded face recognition Python script using subprocess
    cmd = ['python', 'LoginMoodMentor.py']  # Replace with the actual script name
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    # Check if the script execution was successful
    if process.returncode == 0:
        # Parse and convert the script's output to a JSON format (if needed)
        recognition_results = json.loads(stdout)

        return jsonify(recognition_results)
    else:
        return jsonify({"error": "Face recognition script encountered an error"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)

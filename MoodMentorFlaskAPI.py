from flask import Flask, request, jsonify
import subprocess
import requests
import os

app = Flask(__name__)

@app.route('/facialLogin', methods=['POST', 'GET'])
def facialLogin():
    try:
        s3_script_url = 'https://facial-login-model-bucket.s3.amazonaws.com/LoginMoodMentor.py'  # Replace with your S3 script URL
        python_path = '/usr/bin/python3'  # Use the correct Python interpreter path

        s3_script = requests.get(s3_script_url)

        if s3_script.status_code == 200:
            script_path = '/tmp/LoginMoodMentor.py'
            with open(script_path, 'wb') as f:
                f.write(s3_script.content)

            result = subprocess.check_output([python_path, script_path], stderr=subprocess.STDOUT, text=True)

            return jsonify({'result': result})
        else:
            return jsonify({'error': f"Failed to fetch script from S3: {s3_script.status_code}"})
    except Exception as e:
        return jsonify({'error': str(e)})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)

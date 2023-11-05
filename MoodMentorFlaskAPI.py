from flask import Flask, request, jsonify
import subprocess
import requests

app = Flask(__name__)

def get_s3_script_url():
    # Define the S3 bucket URL and object key for the LoginMoodMentor.py script
    S3_BUCKET_URL = 'https://facial-login-model-bucket.s3.amazonaws.com/'
    S3_OBJECT_KEY = 'LoginMoodMentor.py'
    return f"{S3_BUCKET_URL}{S3_OBJECT_KEY}"

@app.route('/facialLogin', methods=['GET'])
def facial_login():
    try:
        s3_script_url = get_s3_script_url()

        # Fetch the 'LoginMoodMentor.py' script from the S3 bucket URL
        s3_script = requests.get(s3_script_url)

        if s3_script.status_code == 200:
            with open('/tmp/LoginMoodMentor.py', 'wb') as f:
                f.write(s3_script.content)

            # Execute the script
            result = subprocess.check_output(['python', '/tmp/LoginMoodMentor.py'], stderr=subprocess.STDOUT, text=True)

            return jsonify({'result': result})
        else:
            return jsonify({'error': f"Failed to fetch 'LoginMoodMentor.py' from S3: {s3_script.status_code}"})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)

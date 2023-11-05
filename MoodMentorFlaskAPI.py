from flask import Flask, request, jsonify
import subprocess
import requests

app = Flask(__name__)

S3_PUBLIC_URL = 'https://s3.amazonaws.com/YOUR_BUCKET_NAME/hello_world.py'  # Replace with your S3 bucket URL

@app.route('/')
def hello_world():
    try:
        # Fetch the 'hello_world.py' script from the public S3 URL
        s3_script = requests.get(S3_PUBLIC_URL)
        
        if s3_script.status_code == 200:
            with open('/tmp/hello_world.py', 'wb') as f:
                f.write(s3_script.content)
            
            # Execute the script
            result = subprocess.check_output(['python', '/tmp/hello_world.py'], stderr=subprocess.STDOUT, text=True)
            
            # Return the result as JSON
            response_data = {'result': result}
            return jsonify(response_data)
        else:
            return jsonify({'error': f"Failed to fetch 'hello_world.py' from S3: {s3_script.status_code}"})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)

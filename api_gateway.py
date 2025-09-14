from flask import Flask, request, jsonify
import jwt
from datetime import datetime,timezone, timedelta
from functools import wraps
import requests # To forward requests to the internal service

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a_super_secret_key_for_jwt'
INTERNAL_API_KEY = "secret_key_between_services"
INTERNAL_SERVICE_URL = "http://127.0.0.1:5001/api/v1/report"

# Dummy user database
users = {"mrs_citizen": "password123"}

# --- Authentication Logic (IAM Component Function) ---
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            # Format: "Bearer <token>"
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = data['user']
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/login', methods=['POST'])
def login():
    auth = request.authorization
    if auth and auth.username in users and auth.password == users[auth.username]:
        token = jwt.encode({
            'user': auth.username,
            'exp': datetime.now(timezone.utc) + timedelta(minutes=30)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        
        print(f"✅ [API Gateway] User '{auth.username}' logged in successfully. Token issued.")
        return jsonify({'token': token})

    return jsonify({'message': 'Login failed!'}), 401

# --- Protected Endpoint ---
@app.route('/submit_report', methods=['POST'])
@token_required
def submit_report(current_user):
    print(f"🔐 [API Gateway] Receiving request from authenticated user: '{current_user}'")
    
    # Get data from the original request
    location = request.form.get('location')
    description = request.form.get('description')
    photo = request.files.get('photo')

    if not all([location, description, photo]):
        return jsonify({'message': 'Report data is incomplete'}), 400

    # Securely forward the request to the internal service
    try:
        # Prepare data to be forwarded
        payload = {
            'user_id': current_user,
            'location': location,
            'description': description
        }
        files = {'photo': (photo.filename, photo.read(), photo.content_type)}
        headers = {'X-Internal-API-Key': INTERNAL_API_KEY}

        print(f"➡️ [API Gateway] Forwarding request to Internal Service...")
        internal_response = requests.post(INTERNAL_SERVICE_URL, data=payload, files=files, headers=headers)
        
        # Return the response from the internal service to the client
        return jsonify(internal_response.json()), internal_response.status_code

    except requests.exceptions.RequestException as e:
        print(f"❌ [API Gateway] Failed to contact internal service: {e}")
        return jsonify({'message': 'Internal service is unavailable'}), 503

if __name__ == '__main__':
    # Runs on port 5000, accessible from the internet (via HTTPS)
    app.run(port=5000, debug=True)

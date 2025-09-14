from flask import Flask, request, jsonify
import os

app = Flask(__name__)
INTERNAL_API_KEY = "secret_key_between_services" 
# In a real-world scenario, this would be managed via a secret manager

# Create a directory to store reports
if not os.path.exists("secure_storage"):
    os.makedirs("secure_storage")

@app.route('/api/v1/report', methods=['POST'])
def process_report():
    # 1. Internal Security: Only accept requests from the Gateway
    api_key = request.headers.get('X-Internal-API-Key')
    if api_key != INTERNAL_API_KEY:
        return jsonify({"error": "Access denied: For internal services only"}), 403

    # 2. Process data that is already considered secure
    try:
        user_id = request.form['user_id']
        location = request.form['location']
        description = request.form['description']
        photo = request.files['photo']
        
        filename = f"report_{user_id}_{photo.filename}"
        photo.save(os.path.join("secure_storage", filename))
        
        print(f"✅ [Internal Service] Report from user '{user_id}' at location '{location}' successfully saved as '{filename}'")
        return jsonify({"message": "Report successfully processed by the internal service"}), 200
        
    except Exception as e:
        print(f"❌ [Internal Service] Error: {str(e)}")
        return jsonify({"error": "Incomplete data"}), 400

if __name__ == '__main__':
    # Runs on port 5001, only accessible from within the internal network
    app.run(port=5001)
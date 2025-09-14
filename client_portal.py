import requests
import os

GATEWAY_URL = "http://127.0.0.1:5000"

# --- Report Data from Mrs. Citizen ---
username = "mrs_citizen"
password = "password123"
report_data = {
    "location": "Jl. Gajah Mada, Pontianak",
    "description": "There is a large and deep hole, dangerous for motorcyclists."
}
# Make sure there is an image file named 'broken_road.jpeg' in the same directory
report_photo_path = "broken_road.jpeg" 

# Create a dummy file if it doesn't exist
if not os.path.exists(report_photo_path):
    with open(report_photo_path, "w") as f:
        f.write("This is a simulation of a broken road photo.")

def run_scenario():
    print("--- Starting 'LaporKuy' Reporting Scenario ---")
    
    # 1. Mrs. Citizen logs in to get a JWT Token
    print("\n[Step 1] Mrs. Citizen is trying to log in...")
    try:
        login_response = requests.post(f"{GATEWAY_URL}/login", auth=(username, password))
        login_response.raise_for_status() # Check for http errors
        
        token = login_response.json()['token']
        print(f"✅ Login successful! Token received.")
    except requests.exceptions.HTTPError as e:
        print(f"❌ Login Failed! Status: {e.response.status_code}, Message: {e.response.json()}")
        return

    # 2. Mrs. Citizen submits the report with the Authentication Token
    print("\n[Step 2] Mrs. Citizen is submitting a road damage report...")
    try:
        headers = {'Authorization': f'Bearer {token}'}
        files = {'photo': open(report_photo_path, 'rb')}
        
        submit_response = requests.post(f"{GATEWAY_URL}/submit_report", headers=headers, data=report_data, files=files)
        submit_response.raise_for_status()

        print(f"✅ Report submitted successfully!")
        print(f"Response from server: {submit_response.json()}")
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ Report Submission Failed! Status: {e.response.status_code}, Message: {e.response.json()}")
    
    print("\n--- Scenario Finished ---")

if __name__ == '__main__':
    run_scenario()

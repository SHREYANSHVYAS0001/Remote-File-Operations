from flask import Flask, request, send_from_directory, abort, jsonify
import os
import requests
import threading
import time
import json

app = Flask(__name__)
UPLOAD_FOLDER = 'primary_server_files'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# List of secondary servers
SECONDARY_SERVERS = []

# Log file to store changes
LOG_FILE = "log.json"

# Function to log changes
def log_change(action, filename, data=None):
    with open(LOG_FILE, 'a') as f:
        log_entry = {"action": action, "filename": filename, "data": data}
        f.write(json.dumps(log_entry) + "\n")  # Added newline character here

# List of secondary servers
SECONDARY_SERVERS = []

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400
    
    file = request.files['file']  # Access the file directly from the request
    if file.filename == '':
        return "No selected file", 400
    
    filename = file.filename
    file.save(os.path.join(UPLOAD_FOLDER, filename))  # Save the file to the upload folder
    
    # Propagate upload to secondary servers
    for secondary_server in SECONDARY_SERVERS:
        try:
            with open(os.path.join(UPLOAD_FOLDER, filename), 'rb') as f:
                files = {'file': (filename, f)}  # Create a dictionary containing the file data
                response = requests.post(f"{secondary_server}/upload", files=files)
                if response.status_code == 200:
                    print(f"Successfully propagated upload to {secondary_server}")
                else:
                    print(f"Failed to propagate upload to {secondary_server}: {response.text}")
        except Exception as e:
            print(f"Error while propagating upload to {secondary_server}: {str(e)}")
    log_change("upload", filename)
    return "Success", 200


@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    if os.path.exists(os.path.join(UPLOAD_FOLDER, filename)):
        return send_from_directory(UPLOAD_FOLDER, filename)
    else:
        abort(404)

@app.route('/list', methods=['GET'])
def list_files():
    try:
        # Attempt to list files locally
        files = os.listdir(UPLOAD_FOLDER)
        return {"files": files}, 200
    except FileNotFoundError:
        try:
            # If files not found locally, fetch from primary server
            response = requests.get(f"{PRIMARY_SERVER}/list")
            if response.status_code == 200:
                files = response.json().get('files', [])
                return {"files": files}, 200
            else:
                return f"Failed to list files: {response.text}", response.status_code
        except requests.exceptions.RequestException as e:
            return f"Failed to list files: {str(e)}", 500


@app.route('/write/<filename>', methods=['POST'])
def write_file(filename):
    data = request.get_data(as_text=True)
    try:
        with open(os.path.join(UPLOAD_FOLDER, filename), 'w') as file:
            file.write(data)
        
        # Propagate write to secondary servers
        for secondary_server in SECONDARY_SERVERS:
            try:
                requests.post(f"{secondary_server}/write/{filename}", data=data)
            except requests.exceptions.RequestException as e:
                print(f"Failed to propagate write to {secondary_server}: {e}")
        log_change("write", filename, data)
        return "File written successfully.", 200
    except Exception as e:
        return f"Failed to write file: {str(e)}", 500
    
@app.route('/append/<filename>', methods=['POST'])
def append_file(filename):
    data = request.get_data(as_text=True)
    try:
        with open(os.path.join(UPLOAD_FOLDER, filename), 'a') as file:
            file.write(data)
        
        # Propagate append to secondary servers
        for secondary_server in SECONDARY_SERVERS:
            try:
                requests.post(f"{secondary_server}/append/{filename}", data=data)
            except requests.exceptions.RequestException as e:
                print(f"Failed to propagate append to {secondary_server}: {e}")
        log_change("append", filename, data)
        return "Data appended to file successfully.", 200
    except Exception as e:
        return f"Failed to append data to file: {str(e)}", 500


@app.route('/read/<filename>', methods=['GET'])
def read_file(filename):
    try:
        with open(os.path.join(UPLOAD_FOLDER, filename), 'r') as file:
            content = file.read()
            return content, 200
    except FileNotFoundError:
        abort(404)


@app.route('/rename/<old_filename>/<new_filename>', methods=['PUT'])
def rename_file(old_filename, new_filename):
    try:
        os.rename(os.path.join(UPLOAD_FOLDER, old_filename), os.path.join(UPLOAD_FOLDER, new_filename))
        
        # Propagate rename to secondary servers using PUT requests
        for secondary_server in SECONDARY_SERVERS:
            try:
                requests.put(f"{secondary_server}/rename/{old_filename}/{new_filename}")
            except requests.exceptions.RequestException as e:
                print(f"Failed to propagate rename to {secondary_server}: {e}")
        log_change("rename", old_filename, new_filename)        
        return "File renamed successfully.", 200
        
    except FileNotFoundError:
        abort(404)



@app.route('/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    try:
        os.remove(os.path.join(UPLOAD_FOLDER, filename))
        # Propagate rename to secondary servers using PUT requests
        for secondary_server in SECONDARY_SERVERS:
            try:
                response = requests.delete(f"{secondary_server}/delete/{filename}")
            except requests.exceptions.RequestException as e:
                print(f"Failed to propagate rename to {secondary_server}: {e}")
        log_change("delete", filename)        
        return f"File {filename} deleted successfully.", 200
    except FileNotFoundError:
        return "File not found.", 404
    except Exception as e:
        return str(e), 500

@app.route('/check_file/<filename>', methods=['GET'])
def check_file(filename):
    try:
        client_id = request.args.get('ClientId')
        
        # Forward the request to the primary server
        response = requests.get(f"{PRIMARY_SERVER_URL}/check_file/{filename}", params={'ClientId': client_id})
        
        if response.status_code == 200:
            return response.text, 200
        else:
            return "Failed to check file lock.", 500
    except Exception as e:
        return str(e), 500
    
@app.route('/log', methods=['GET'])
def log():
    try:
        with open(LOG_FILE, 'r') as log_1:
            entries = [json.loads(line) for line in log_1]
        return {'log': entries}, 200
    except Exception as e:
        return {'error': str(e)}, 500

##################
@app.route('/get_server', methods=['GET'])
def get_server():
    try:
        # Return the list of server URLs in JSON format
        return jsonify({'array_data': SECONDARY_SERVERS}), 200
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'error': 'An error occurred while fetching server URLs.'}), 500

    
def heartbeat():
    while True:
        for secondary_server in SECONDARY_SERVERS:
            try:
                response = requests.get(f"{secondary_server}/heartbeat")
                if response.status_code == 200:
                    print(f"Heartbeat check passed for {secondary_server}")
                else:
                    print(f"Heartbeat check failed for {secondary_server}")
            except Exception as e:
                print(f"Error while sending heartbeat to {secondary_server}: {str(e)}")
        time.sleep(5)  # wait for 5 seconds before next heartbeat


if __name__ == '__main__':

    num_secondary_servers = int(input("Enter the number of secondary servers: "))

    # Iterate through the range of the number of secondary servers
    for i in range(num_secondary_servers):
        # Ask the user for the IP address of each secondary server
        ip_address = input(f"Enter the IP address of secondary server {i+1}: ")
        # Construct the URL and append it to the list
        SECONDARY_SERVERS.append(ip_address)
    
    heartbeat_thread = threading.Thread(target=heartbeat)
    heartbeat_thread.start()

    app.run(port=6000)

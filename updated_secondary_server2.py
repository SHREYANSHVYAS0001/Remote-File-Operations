from flask import Flask, request, send_from_directory, abort, jsonify
import os
import time
import requests
import threading

app = Flask(__name__)
UPLOAD_FOLDER = 'secondary_server_2_files'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

PRIMARY_SERVER = None

@app.route('/upload2', methods=['POST'])
def upload_file2():
    file = request.files['file']  # Access the file directly from the request
    files = {'file': (file.filename, file.stream)}  # Create a dictionary containing the file data
    response = requests.post(f"{PRIMARY_SERVER}/upload", files=files)  # Send the file data to the primary server
    if response.status_code == 200:
        print("File uploaded successfully.")
        return "File uploaded successfully."  # Return a simple success message
    else:
        print("Failed to upload file.", response.status_code)
        return jsonify({"error": "Failed to upload file.", "status_code": response.status_code})

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    if file:
        filename = file.filename
        file.save(os.path.join(UPLOAD_FOLDER, filename))
    return "success", 200

@app.route('/read/<filename>', methods=['GET'])
def read_file(filename):
    try:
        with open(os.path.join(UPLOAD_FOLDER, filename), 'r') as file:
            content = file.read()
            return content, 200
    except FileNotFoundError:
        abort(404)

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

        return "File written successfully.", 200
    except Exception as e:
        return f"Failed to write file: {str(e)}", 500

@app.route('/write2/<filename>', methods=['POST'])
def write_file2(filename):
    data = request.get_data(as_text=True)
    # Forward write request to primary server
    response = requests.post(f"{PRIMARY_SERVER}/write/{filename}", data=data)
    if response.status_code == 200:
        return "File written successfully.", 200
    else:
        print(f"Failed to write content to {filename}.")

@app.route('/append/<filename>', methods=['POST'])
def append_file(filename):
    data = request.get_data(as_text=True)
    try:
        with open(os.path.join(UPLOAD_FOLDER, filename), 'a') as file:  # Change 'w' to 'a'
            file.write(data)

        return "Data appended to file successfully.", 200
    except Exception as e:
        return f"Failed to append data to file: {str(e)}", 500

@app.route('/append2/<filename>', methods=['POST'])
def append_file2(filename):
    data = request.get_data(as_text=True)
    # Forward append request to primary server
    response = requests.post(f"{PRIMARY_SERVER}/append/{filename}", data=data)
    if response.status_code == 200:
        return "Data appended to file successfully.", 200
    else:
        print(f"Failed to append content to {filename}.")


@app.route('/rename/<old_filename>/<new_filename>', methods=['PUT'])
def rename_file(old_filename, new_filename):
    try:
        os.rename(os.path.join(UPLOAD_FOLDER, old_filename), os.path.join(UPLOAD_FOLDER, new_filename))
        return "File renamed successfully.", 200
    except FileNotFoundError:
        abort(404)

@app.route('/rename2/<old_filename>/<new_filename>', methods=['PUT'])
def rename_file2(old_filename, new_filename):
    try:
        # Proxy the rename request to the primary server
        response = requests.put(f"{PRIMARY_SERVER}/rename/{old_filename}/{new_filename}")
        if response.status_code == 200:
            return "File renamed successfully.", 200
        else:
            return "Failed to rename file.", 500
    except Exception as e:
        return str(e), 500

@app.route('/delete2/<filename>', methods=['DELETE'])
def delete_file2(filename):
    response = requests.delete(f"{PRIMARY_SERVER}/delete/{filename}")
    if response.status_code == 200:
        return f"{filename} deleted successfully."
    else:
        return f"Failed to delete {filename}."

@app.route('/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    try:
        os.remove(os.path.join(UPLOAD_FOLDER, filename))                
        return f"File {filename} deleted successfully.", 200
    except FileNotFoundError:
        return "File not found.", 404
    except Exception as e:
        return str(e), 500

@app.route('/heartbeat', methods=['GET'])
def heartbeat():
    return "Alive", 200

def sync_with_primary():
    # Fetch the log from the primary server
    response = requests.get(f"{PRIMARY_SERVER}/log")
    if response.status_code == 200:
        log_entries = response.json().get('log', [])
        
        # For each log entry
        for log_entry in log_entries:
            action = log_entry["action"]
            filename = log_entry["filename"]
            data = log_entry.get("data")
            
            # Perform the action
            if action == "upload":
                # Download the file from the primary server
                response = requests.get(f"{PRIMARY_SERVER}/download/{filename}")
                if response.status_code == 200:
                    with open(os.path.join(UPLOAD_FOLDER, filename), 'w') as file:
                        file.write(response.text)
                else:
                    print(f"Failed to download {filename} from primary server.")
            elif action == "write":
                with open(os.path.join(UPLOAD_FOLDER, filename), 'w') as file:
                    file.write(data)
            elif action == "append":
                with open(os.path.join(UPLOAD_FOLDER, filename), 'a') as file:
                    file.write(data)
            elif action == "rename":
                os.rename(os.path.join(UPLOAD_FOLDER, filename), os.path.join(UPLOAD_FOLDER, data))
            elif action == "delete":
                os.remove(os.path.join(UPLOAD_FOLDER, filename))
    else:
        print(f"Failed to fetch log from primary server: {response.text}")

    # while True:
    time.sleep(5)  # wait for 5 seconds before next sync


if __name__ == '__main__':
    primary_ip_address = input("Enter the IP address of the primary server: ")
    # Construct the URL for the primary server
    PRIMARY_SERVER = primary_ip_address
    sync_with_primary()
    
    app.run(port=5001)

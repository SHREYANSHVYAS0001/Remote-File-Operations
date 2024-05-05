import requests
import os
import uuid

SERVER_URL = None
CLIENT_ID = None

def connect(server_url):
    global SERVER_URL
    SERVER_URL = server_url
    global CLIENT_ID
    CLIENT_ID = str(uuid.uuid4())

def upload_file(filepath):
    if not os.path.exists(filepath):
        print("File not found.")
        return
    
    with open(filepath, 'rb') as f:
        files = {'file': (os.path.basename(filepath), f)}
        response = requests.post(f"{SERVER_URL}/upload2", files=files)
        if response.status_code == 200:
            print("File uploaded successfully.")
        else:
            print("Failed to upload file.",response.status_code)

def download_file(filename):
    response = requests.get(f"{SERVER_URL}/download/{filename}")
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"{filename} downloaded successfully.")
    else:
        print(f"Failed to download {filename}.")

def list_files():
    response = requests.get(f"{SERVER_URL}/list")
    if response.status_code == 200:
        files = response.json().get('files', [])
        if files:
            print("Files on server:")
            for file in files:
                print(file)
        else:
            print("No files on server.")
    else:
        print("Failed to list files.")

def read_file(filename):
    response = requests.get(f"{SERVER_URL}/read/{filename}")
    if response.status_code == 200:
        content = response.text
        print(f"Content of {filename}:\n{content}")
    else:
        print(f"Failed to read {filename}.")

def write_file(filename):
    content = input("Enter content to write into the file: ")
    response = requests.post(f"{SERVER_URL}/write2/{filename}", data=content)
    if response.status_code == 200:
        print(f"Content written to {filename} successfully.")
    else:
        print(f"Failed to write content to {filename}.")

def append_file(filename):
    content = input("Enter content to append into the file: ")
    response = requests.post(f"{SERVER_URL}/append2/{filename}", data=content)
    if response.status_code == 200:
        print(f"Content append to {filename} successfully.")
    else:
        print(f"Failed to append content to {filename}.")

def rename_file(old_filename, new_filename):
    response = requests.put(f"{SERVER_URL}/rename2/{old_filename}/{new_filename}")
    if response.status_code == 200:
        print(f"{old_filename} renamed to {new_filename} successfully.")
    else:
        print(f"Failed to rename {old_filename} to {new_filename}.")

def delete_file(filename):
    response = requests.delete(f"{SERVER_URL}/delete2/{filename}")
    if response.status_code == 200:
        print(f"{filename} deleted successfully.")
    else:
        print(f"Failed to delete {filename}.")

def check_file(filename):
    response = requests.get(f"{SERVER_URL}/check_file/{filename}")
    if response.status_code == 200:
        return 1
    else:
        return 0


def main():
    global SERVER_URL
    SERVER_URL = input("Enter the server URL (e.g., http://127.0.0.1:7000): ")
    connect(SERVER_URL)  # Connect to the server    

    while True:
        print("\nActions:")
        print("1. Upload file")
        print("2. Download file")
        print("3. List files")
        print("4. Read file")
        print("5. Write file")
        print("6. Rename file")
        print("7. Delete file")
        print("8. Append into file")
        print("9. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            filepath = input("Enter the file path to upload: ")
            upload_file(filepath)
        elif choice == '2':
            filename = input("Enter the filename to download: ")
            download_file(filename)
        elif choice == '3':
            list_files()
        elif choice == '4':
            filename = input("Enter the filename to read: ")
            read_file(filename)
        elif choice == '5':
            filename = input("Enter the filename to write: ")
            write_file(filename)
        elif choice == '6':
            old_filename = input("Enter the old filename: ")
            new_filename = input("Enter the new filename: ")
            rename_file(old_filename, new_filename)
        elif choice == '7':
            filename = input("Enter the filename to delete: ")
            delete_file(filename)
        elif choice == '8':
            filename = input("Enter the filename to append: ")
            append_file(filename)
        elif choice == '9':
            print("Exiting.")
            break
        else:
            print("Invalid choice. Please choose again.")

if __name__ == '__main__':
    main()

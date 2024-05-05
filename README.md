# File Server System

This system consists of a primary server, secondary server, and client scripts for interacting with the servers. It enables file upload, download, modification, and deletion while ensuring synchronization between the primary and secondary servers.

## Installation

1. Ensure you have Python installed on your system.
2. Install Flask for server scripts and requests library for the client script using the following commands:


## Primary Server

The primary server facilitates file operations and synchronization with secondary servers.

### Usage

1. Run the primary server script using the following command:

2. Upon running, you'll be prompted to enter the number of secondary servers and their IP addresses. Enter the required information as prompted.
3. The primary server will listen for incoming requests on port 6000 by default.

### Endpoints

- **POST /upload**: Uploads a file to the primary server and propagates the upload to secondary servers.
- **GET /download/<filename>**: Downloads a file from the primary server.
- **GET /list**: Lists files available on the primary server.
- **POST /write/<filename>**: Writes data to a file on the primary server and propagates the write to secondary servers.
- **POST /append/<filename>**: Appends data to a file on the primary server and propagates the append to secondary servers.
- **PUT /rename/<old_filename>/<new_filename>**: Renames a file on the primary server and propagates the rename to secondary servers.
- **DELETE /delete/<filename>**: Deletes a file from the primary server and propagates the delete to secondary servers.
- **GET /check_file/<filename>?ClientId=<client_id>**: Checks the lock status of a file on the primary server.
- **GET /log**: Retrieves the log of changes made to files.

### Heartbeat

The primary server periodically sends heartbeat requests to secondary servers to check their availability and health status.

### Logging

All file-related actions performed on the primary server are logged in a JSON log file named `log.json`.

## Secondary Server

The secondary server synchronizes file operations with the primary server and serves client requests.

### Usage

1. Run the secondary server script using the following command:

2. Upon running, you'll be prompted to enter the IP address of the primary server.
3. The secondary server will listen for incoming requests on port 5000 by default.

### Endpoints

- **POST /upload**: Uploads a file to the secondary server.
- **GET /download/<filename>**: Downloads a file from the secondary server.
- **GET /list**: Lists files available on the secondary server.
- **POST /write/<filename>**: Writes data to a file on the secondary server.
- **POST /append/<filename>**: Appends data to a file on the secondary server.
- **PUT /rename/<old_filename>/<new_filename>**: Renames a file on the secondary server.
- **DELETE /delete/<filename>**: Deletes a file from the secondary server.
- **GET /heartbeat**: Checks the availability of the secondary server.

### Synchronization with Primary Server

- **Sync Process**: The secondary server periodically synchronizes its file operations with the primary server. This includes fetching the log of changes from the primary server and applying them locally.
- **Sync Interval**: By default, the synchronization occurs every 5 seconds.

### Proxying Requests to Primary Server

- **Write Requests**: Write and append requests are forwarded to the primary server for consistency.
- **Rename and Delete Requests**: Rename and delete requests are proxied to the primary server for synchronization.

## Client

The client script allows users to interact with the file server.

### Usage

1. Run the client script using the following command:

2. Upon running, you'll be prompted to enter the server URL (e.g., http://127.0.0.1:5000).
3. Choose from the available actions to interact with the file server.

### Actions

1. **Upload file**: Uploads a file to the server.
2. **Download file**: Downloads a file from the server.
3. **List files**: Lists files available on the server.
4. **Read file**: Reads the content of a file from the server.
5. **Write file**: Writes content to a file on the server.
6. **Append into file**: Appends content to a file on the server.
7. **Rename file**: Renames a file on the server.
8. **Delete file**: Deletes a file from the server.
9. **Exit**: Quits the client application.

## Note

- Ensure that the primary and secondary servers are running and accessible before using the client script.

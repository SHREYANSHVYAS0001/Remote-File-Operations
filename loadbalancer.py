from flask import Flask, jsonify
import requests

app = Flask(__name__)
    
def get_server(LOAD_URL):
    try:
        response = requests.get(f"{LOAD_URL}/get_server")
        if response.status_code == 200:
            server_urls = response.json().get('array_data')
            # Return server_urls to use it outside this function
            return server_urls
        else:
            print("Failed to get server URLs from the server.")
            return None
    except Exception as e:
        print("An error occurred:", e)
        return None

PRIMARY_URL = "http://localhost:6000"  
SERVER_URLS = get_server(PRIMARY_URL)

current_server_index = 0
@app.route('/load_balancer', methods=['POST'])
def load_balancer():
    global current_server_index
    try:        
        current_server_url = SERVER_URLS[current_server_index]
        current_server_index = (current_server_index + 1) % len(SERVER_URLS)
        return jsonify({'current_server_url': current_server_url}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=7000)

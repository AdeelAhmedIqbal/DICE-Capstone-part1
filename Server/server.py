import socket
import os
import hashlib
import random
import struct

SERVER_IP = '0.0.0.0'    # # Use '0.0.0.0' to bind to all available network interfaces
SERVER_PORT = 12345      # Server port
SERVER_DATA_DIR = '/serverdata'  # Relative path to server data directory

def generate_random_file(file_path):
    with open(file_path, 'wb') as file:
        random_data = ''.join(random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(1024))
        file.write(random_data.encode())

def calculate_checksum(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as file:
        while True:
            data = file.read(8192)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()

def main():
    if not os.path.exists(SERVER_DATA_DIR):
        os.makedirs(SERVER_DATA_DIR)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen(1)
    print(f"Server is listening on {SERVER_IP}:{SERVER_PORT}")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Accepted connection from {client_address}")

        # Generate a random file with random data
        file_name = 'random_data.txt'
        file_path = os.path.join(SERVER_DATA_DIR, file_name)
        generate_random_file(file_path)

        # Calculate checksum of the file
        checksum = calculate_checksum(file_path)

        # Send the length of the checksum and checksum to the client
        checksum_length = len(checksum)
        client_socket.send(struct.pack('!Q', checksum_length))
        client_socket.send(checksum.encode())

        # Send the length of the file and file data to the client
        file_size = os.path.getsize(file_path)
        client_socket.send(struct.pack('!Q', file_size))
        with open(file_path, 'rb') as file:
            while True:
                data = file.read(8192)
                if not data:
                    break
                client_socket.send(data)

        print(f"File and checksum sent to {client_address}")
        client_socket.close()

if __name__ == "__main__":
    main()

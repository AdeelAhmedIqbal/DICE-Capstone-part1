import socket
import os
import hashlib
import struct

SERVER_IP = 'server'  # Server IP address
SERVER_PORT = 12345      # Server port
CLIENT_DATA_DIR = '/clientdata'  # Relative path to client data directory

def receive_data_with_length(client_socket, data_length):
    data = b''
    while len(data) < data_length:
        chunk = client_socket.recv(data_length - len(data))
        if not chunk:
            break
        data += chunk
    return data

def receive_file(client_socket, file_name, file_size):
    file_path = os.path.join(CLIENT_DATA_DIR, file_name)
    with open(file_path, 'wb') as file:
        bytes_received = 0
        while bytes_received < file_size:
            data = client_socket.recv(8192)
            if not data:
                break
            file.write(data)
            bytes_received += len(data)
    return file_path

def calculate_checksum(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as file:
        while True:
            data = file.read(8192)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()

def verify_integrity(file_path, received_checksum):
    calculated_checksum = calculate_checksum(file_path)
    return received_checksum == calculated_checksum

def main():
    if not os.path.exists(CLIENT_DATA_DIR):
        os.makedirs(CLIENT_DATA_DIR)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, SERVER_PORT))

    # Receive the length of the checksum and checksum from the server
    checksum_length = struct.unpack('!Q', receive_data_with_length(client_socket, 8))[0]
    received_checksum = receive_data_with_length(client_socket, checksum_length).decode()

    # Receive the length of the file and file data from the server
    file_size = struct.unpack('!Q', receive_data_with_length(client_socket, 8))[0]
    file_name = 'received_data.txt'
    received_file_path = receive_file(client_socket, file_name, file_size)
    print(f"File received and saved as {received_file_path}")

    # Verify the integrity of the received file
    if verify_integrity(received_file_path, received_checksum):
        print("File integrity verified successfully.")
    else:
        print("File integrity verification failed.")

    client_socket.close()

if __name__ == "__main__":
    main()

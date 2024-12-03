import socket
from threading import Thread
import argparse
from pathlib import Path
import gzip

# Constants
RN = b'\r\n'  # Carriage Return and New Line


def parse_request(conn):
    """
    Parses an incoming HTTP request from the client.
    """
    request_data = {}
    headers = {}
    body = []

    target = 0  # Indicates the part of the request being parsed
    rest = b''
    body_len = 0
    body_received = 0

    while data := conn.recv(1024):
        if rest:
            data = rest + data
            rest = b''

        if target == 0:  # Parse the request line (e.g., "GET /path HTTP/1.1")
            ind = data.find(RN)
            if ind == -1:
                rest = data
                continue
            request_line = data[:ind].decode()
            request_data['request'] = request_line
            method, url, _ = request_line.split()
            request_data['method'] = method
            request_data['url'] = url
            data = data[ind + 2:]
            target = 1  # Move to headers parsing

        if target == 1:  # Parse headers
            while True:
                ind = data.find(RN)
                if ind == -1:
                    rest = data
                    break
                if ind == 0:  # End of headers (blank line)
                    data = data[ind + 2:]
                    target = 2
                    break
                header_line = data[:ind].decode()
                key, value = header_line.split(':', maxsplit=1)
                headers[key.lower()] = value.strip()
                data = data[ind + 2:]
            if target == 1:
                continue

        if target == 2:  # Determine if there is a body
            if 'content-length' not in headers:
                break
            body_len = int(headers['content-length'])
            if body_len == 0:
                break
            target = 3

        if target == 3:  # Parse the body
            body.append(data)
            body_received += len(data)
            if body_received >= body_len:
                break

    request_data['headers'] = headers
    request_data['body'] = b''.join(body)
    return request_data


def handle_request(conn, base_dir):
    """
    Handles a single HTTP request.
    """
    with conn:
        # Parse the incoming HTTP request
        request = parse_request(conn)
        url = request['url']
        method = request['method']
        headers = request['headers']
        body = request.get('body', b'')

        # Root endpoint
        if url == '/':
            conn.sendall(b"HTTP/1.1 200 OK\r\n\r\n")

        # Echo endpoint
        elif url.startswith('/echo/'):
            response_body = url[6:].encode()
            conn.send(b'HTTP/1.1 200 OK\r\n')
            conn.send(b'Content-Type: text/plain\r\n')
            if 'accept-encoding' in headers:
                encodings = headers['accept-encoding'].split(', ')
                if 'gzip' in encodings:
                    conn.send(b'Content-Encoding: gzip\r\n')
                    response_body = gzip.compress(response_body)
            conn.send(f'Content-Length: {len(response_body)}\r\n'.encode())
            conn.send(RN)
            conn.send(response_body)

        # User-Agent endpoint
        elif url == '/user-agent':
            user_agent = headers.get('user-agent', 'Unknown')
            response_body = user_agent.encode()
            conn.send(b'HTTP/1.1 200 OK\r\n')
            conn.send(b'Content-Type: text/plain\r\n')
            conn.send(f'Content-Length: {len(response_body)}\r\n'.encode())
            conn.send(RN)
            conn.send(response_body)

        # File handling endpoint
        elif url.startswith('/files/'):
            file_path = Path(base_dir) / url[7:]
            if method == 'GET':
                if file_path.exists():
                    conn.send(b'HTTP/1.1 200 OK\r\n')
                    conn.send(b'Content-Type: application/octet-stream\r\n')
                    with file_path.open('rb') as file:
                        response_body = file.read()
                    conn.send(f'Content-Length: {len(response_body)}\r\n'.encode())
                    conn.send(RN)
                    conn.send(response_body)
                else:
                    conn.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")
            elif method == 'POST':
                with file_path.open('wb') as file:
                    file.write(body)
                conn.send(b"HTTP/1.1 201 Created\r\n\r\n")
            else:
                conn.sendall(b"HTTP/1.1 405 Method Not Allowed\r\n\r\n")

        # Unknown endpoint
        else:
            conn.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")


def main():
    """
    Main function to start the HTTP server.
    """
    parser = argparse.ArgumentParser(description='Simple HTTP Server')
    parser.add_argument('--directory', default='.', help='Base directory for file operations')
    args = parser.parse_args()

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    print("Server started on localhost:4221")

    while True:
        conn, _ = server_socket.accept()
        Thread(target=handle_request, args=(conn, args.directory)).start()


if __name__ == "__main__":
    main()

import socket
import threading
import sys
import os
import gzip

def gzip_compress(data):
    """Compress data using gzip."""
    compressed_data = gzip.compress(data.encode())
    return compressed_data

def main():
    def handle_req(client, addr):
        try:
            data = client.recv(1024).decode()
            if not data:
                return
            
            req = data.split("\r\n")
            request_line = req[0].split(" ")
            method = request_line[0]
            path = request_line[1]

            # Extract headers and body
            headers = {line.split(": ")[0]: line.split(": ")[1] for line in req[1:] if ": " in line}
            body = req[-1] if req[-1] else ""

            if method == "GET":
                if path.startswith('/echo/'):
                    response_body = path[6:]  # Extract the data after '/echo/'
                    accept_encoding = headers.get("Accept-Encoding", "")
                    if "gzip" in accept_encoding:
                        compressed_body = gzip_compress(response_body)
                        response = (
                            f"HTTP/1.1 200 OK\r\n"
                            f"Content-Type: text/plain\r\n"
                            f"Content-Encoding: gzip\r\n"
                            f"Content-Length: {len(compressed_body)}\r\n\r\n"
                        ).encode() + compressed_body
                    else:
                        response = (
                            f"HTTP/1.1 200 OK\r\n"
                            f"Content-Type: text/plain\r\n"
                            f"Content-Length: {len(response_body)}\r\n\r\n"
                            f"{response_body}"
                        ).encode()
                else:
                    response = "HTTP/1.1 404 Not Found\r\n\r\nInvalid path".encode()
                client.send(response)

            elif method == "POST":
                if path.startswith("/files/"):
                    # Extract file name from the path
                    directory = sys.argv[2] if len(sys.argv) > 2 else "."
                    filename = path[7:]

                    # Write the body content to the file
                    try:
                        file_path = os.path.join(directory, filename)
                        with open(file_path, "w") as f:
                            f.write(body)
                        response = "HTTP/1.1 201 Created\r\n\r\n".encode()
                    except Exception as e:
                        response = f"HTTP/1.1 500 Internal Server Error\r\n\r\n{str(e)}".encode()
                else:
                    response = "HTTP/1.1 404 Not Found\r\n\r\nInvalid path".encode()
                client.send(response)

            else:
                response = "HTTP/1.1 405 Method Not Allowed\r\n\r\n".encode()
                client.send(response)
        except Exception as e:
            response = f"HTTP/1.1 500 Internal Server Error\r\n\r\n{str(e)}".encode()
            client.send(response)
        finally:
            client.close()

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    print("Server started on localhost:4221")
    while True:
        try:
            client, addr = server_socket.accept()
            threading.Thread(target=handle_req, args=(client, addr), daemon=True).start()
        except KeyboardInterrupt:
            print("\nServer shutting down...")
            break
    server_socket.close()

if __name__ == "__main__":
    main()

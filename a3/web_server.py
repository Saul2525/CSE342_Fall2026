#!/usr/bin/env python3
"""Starter code for the CSE 342 TCP Web Server assignment.

Complete every numbered TODO between the ``Fill in start`` and ``Fill in end``
markers. The program takes no command-line arguments.
"""

from __future__ import annotations

import mimetypes
from pathlib import Path
from socket import (
    AF_INET,
    SOCK_STREAM,
    SOL_SOCKET,
    SO_REUSEADDR,
    socket,
    timeout as SocketTimeout,
)
from urllib.parse import unquote, urlsplit

SERVER_HOST = ""
SERVER_PORT = 8888
BACKLOG = 5
MAX_REQUEST_BYTES = 8192
CLIENT_TIMEOUT_SECONDS = 5.0
SERVER_DIRECTORY = Path(__file__).resolve().parent
INDEX_PAGE = SERVER_DIRECTORY / "index.html"
NOT_FOUND_PAGE = SERVER_DIRECTORY / "404.html"

# These complete HTML pages for index.html and 404.html.
INDEX_HTML = b"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Hello World</title>
</head>
<body>
    <h1>Hello World</h1>
</body>
</html>
"""

NOT_FOUND_HTML = b"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>404 Not Found</title>
</head>
<body>
    <h1>404 Not Found</h1>
    <p>The requested file could not be found.</p>
</body>
</html>
"""

def resolve_request_target(target: str) -> Path:
    """Return a safe file path inside the server program's directory."""

    url_path = unquote(urlsplit(target).path)
    if url_path in ("", "/", "/index"):
        relative_path = "index.html"
    else:
        relative_path = url_path.lstrip("/")
    requested_path = (SERVER_DIRECTORY / relative_path).resolve()
    try:
        requested_path.relative_to(SERVER_DIRECTORY)
    except ValueError as error:
        raise PermissionError("request escaped the server directory") from error
    return requested_path

def build_response(status_line: str, body: bytes, content_type: str) -> bytes:
    """Return one complete HTTP response containing the supplied body."""

    response_header = (
        f"{status_line}\r\n"
        f"Content-Length: {len(body)}\r\n"
        f"Content-Type: {content_type}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).encode("ascii")
    return response_header + body

def main() -> None:
    """Handle one HTTP request at a time until Ctrl-C."""

    # Build both supplied HTML files before the server starts.
    INDEX_PAGE.write_bytes(INDEX_HTML)
    NOT_FOUND_PAGE.write_bytes(NOT_FOUND_HTML)

    server_socket = socket(AF_INET, SOCK_STREAM)

    # Allow the server to restart without waiting for an old TCP connection's
    # TIME_WAIT state to expire.
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    # Prepare a server socket.
    # Fill in start -- TODO 1
    # Bind to (SERVER_HOST, SERVER_PORT), listen with BACKLOG, and print the
    # directory and listening URL.

    # Bind the server socket to the specified host and port, begin listening for
    # incoming connections, and print the server directory and listening URL.
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen(BACKLOG)
    print(f"Serving from {SERVER_DIRECTORY}")
    print(f"Listening on http://localhost:{SERVER_PORT}")

    try:
        while True:
            print("Ready to serve...")

            # Establish the connection.
            # Fill in start -- TODO 2
            # Accept one client and save both the connected socket and address.

            # Accept an incoming client connection and store its socket and address.
            connection_socket, client_address = server_socket.accept()

            try:
                connection_socket.settimeout(CLIENT_TIMEOUT_SECONDS)

                # Receive the HTTP request.
                # Fill in start -- TODO 3
                # Repeatedly call recv until CRLF CRLF, client close, or
                # MAX_REQUEST_BYTES. Store the result as bytes in message.

                # Receive the client's HTTP request until the header terminator is found,
                # the client disconnects, or the maximum request size is reached.
                message = b""
                while True:
                    chunk = connection_socket.recv(MAX_REQUEST_BYTES - len(message))
                    if not chunk:
                        break
                    message += chunk
                    if b"\r\n\r\n" in message:
                        break
                    if len(message) >= MAX_REQUEST_BYTES:
                        break
                if b"\r\n\r\n" not in message:
                    raise ValueError("Incomplete or oversized request.")

                # Parse the request and read the requested file.
                # Fill in start -- TODO 4
                # Decode with ISO-8859-1, parse method/target/version from the
                # request line, require GET and an HTTP version, resolve target
                # with resolve_request_target, and read the file as bytes into
                # output_data.
                # Hint: use request_line = message.decode("iso-8859-1").split("\r\n", 1)[0]

                # Decode and parse the HTTP request line, validate the GET method and HTTP
                # version, resolve the requested file path, and read its contents as bytes.
                request_line = message.decode("iso-8859-1").split("\r\n", 1)[0]
                method, target, version = request_line.split()
                if method != "GET" or not version.startswith("HTTP/"):
                    raise ValueError("Invalid request.")
                requested_path = resolve_request_target(target)
                output_data = requested_path.read_bytes()

                content_type = mimetypes.guess_type(requested_path.name)[0]
                if content_type is None:
                    content_type = "application/octet-stream"
                elif content_type.startswith("text/"):
                    content_type += "; charset=utf-8"

                # Send the success response.
                # Fill in start -- TODO 5
                # Construct the HTTP/1.1 200 OK header, including
                # Content-Length, Content-Type using content_type,
                # Connection: close, and the required blank line. Encode the
                # header as bytes and send it with output_data using sendall.

                # Build and send an HTTP 200 OK response containing the requested file and
                # its appropriate content type.
                response = build_response("HTTP/1.1 200 OK", output_data, content_type)
                connection_socket.sendall(response)

                print(f"200 {requested_path.name} | client={client_address}")

            except (FileNotFoundError, IsADirectoryError, PermissionError):
                # Send a response message for a file that cannot be served.
                # The 404 page was built from the supplied starter-code HTML.
                body = NOT_FOUND_PAGE.read_bytes()

                # Fill in start -- TODO 6
                # Construct the HTTP/1.1 404 Not Found header,
                # including Content-Length, Content-Type, Connection: close,
                # and the required blank line. Send the provided body with it.

                # Build and send an HTTP 404 Not Found response containing the supplied
                # error page when the requested file cannot be served.
                response_header = (
                    "HTTP/1.1 404 Not Found\r\n"
                    f"Content-Length: {len(body)}\r\n"
                    "Content-Type: text/html; charset=utf-8\r\n"
                    "Connection: close\r\n"
                    "\r\n"
                ).encode("ascii")
                connection_socket.sendall(response_header + body)

                print(f"404 | client={client_address}")

            except (SocketTimeout, UnicodeDecodeError, ValueError):
                body = b"<h1>400 Bad Request</h1>\n"
                response_header = (
                    "HTTP/1.1 400 Bad Request\r\n"
                    f"Content-Length: {len(body)}\r\n"
                    "Content-Type: text/html; charset=utf-8\r\n"
                    "Connection: close\r\n"
                    "\r\n"
                ).encode("ascii")
                connection_socket.sendall(response_header + body)
                print(f"400 | client={client_address}")

            finally:
                # Close the client socket.
                # Fill in start -- TODO 7

                # Close the client connection after handling the request, regardless of
                # whether it succeeded or encountered an error.
                connection_socket.close()

    except KeyboardInterrupt:
        print("\nWeb server stopped.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()

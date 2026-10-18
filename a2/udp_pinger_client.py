from socket import socket, timeout, AF_INET, SOCK_DGRAM
import time

# Sets the server host and port to connect to.
SERVER_HOST = "128.180.120.92"
SERVER_PORT = 4041

# Sets the number of pings to send, the timeout for receiving data, and the maximum datagram size.
PING_COUNT = 10
TIMEOUT_SECONDS = 1.0
MAX_DATAGRAM_BYTES = 1024

# Creates the UDP socket and sets the timeout for receiving data.
client_socket  = socket(AF_INET, SOCK_DGRAM)
client_socket.settimeout(TIMEOUT_SECONDS)

# Prints the target server and port, the number of pings to send, and the timeout for receiving data.
print(f"Target: {SERVER_HOST}:{SERVER_PORT}/udp")
print(f"Pings: {PING_COUNT}; timeout: {TIMEOUT_SECONDS} second")

try:
    # Loops through the number of pings to send, sending a request and waiting for a reply.
    for i in range(PING_COUNT):
        request = f"Ping {i + 1} {time.time()}".encode('utf-8')

        # Records the start time using a high-resolution timer to measure RTT.
        start_time = time.perf_counter()
        try:
            # Sends the request to the server and waits for a reply.
            client_socket.sendto(request, (SERVER_HOST, SERVER_PORT))

            # Receives the server's reply and records the address it came from.
            reply, server_address = client_socket.recvfrom(MAX_DATAGRAM_BYTES)

            # Records the end time and calculates the round-trip time (RTT).
            end_time = time.perf_counter()
            rtt = (end_time - start_time)

            # Checks whether the server returned the original request in uppercase.
            # Prints the reply details if valid, or an error message if it does not match.
            if (reply == request.upper()):
                print(f"Reply from {server_address[0]}:{server_address[1]}: {reply.decode('utf-8')} | sequence={i + 1} | RTT={rtt:.6f} s")
            else:
                print(f"Invalid request and/or reply | sequence={i + 1}")
        # Catches a timeout exception if the request times out, printing a message with the sequence number and timeout value.
        except timeout:
            print(f"Request timed out | sequence={i + 1} | timeout={TIMEOUT_SECONDS} s")
        # Catches an OSError exception if there is an unexpected OS error, printing a message with the error and breaking the loop.
        except OSError as e:
            print(f"There was an unexpected OS error: {e}.")
            break
# Ensures the socket is gracefully closed after the loop, even if an exception occurs.
finally:
    client_socket.close()

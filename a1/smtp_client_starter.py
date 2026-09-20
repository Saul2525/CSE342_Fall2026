#!/usr/bin/env python3
"""
Starter code for Assignment 1: SMTP and Socket Programming.

Complete the seven Fill regions and add your own concise comments explaining
the SMTP purpose, expected reply, and important protocol details in each one.
"""

from socket import AF_INET, SOCK_STREAM, socket
import re
import sys

MAX_REPLY_LINE = 8192

def receive_reply(reader):
    """Read, print, and return one complete SMTP reply."""
    lines = []
    reply_code = None

    while True:
        raw = reader.readline(MAX_REPLY_LINE + 1)
        if raw == b"":
            raise ConnectionError("server closed the connection unexpectedly")
        if len(raw) > MAX_REPLY_LINE:
            raise RuntimeError("SMTP reply line is too long")

        line = raw.decode("utf-8", errors="replace").rstrip("\r\n")
        print(f"S: {line}")

        if len(line) < 4 or not line[:3].isdigit() or line[3] not in " -":
            raise RuntimeError(f"malformed SMTP reply: {line!r}")

        current_code = int(line[:3])
        if reply_code is None:
            reply_code = current_code
        elif current_code != reply_code:
            raise RuntimeError("inconsistent status codes in multiline reply")

        lines.append(line)
        if line[3] == " ":
            return reply_code, lines


def require_code(actual, allowed, step):
    """Stop the conversation when a reply code is not allowed."""
    if actual not in allowed:
        expected = "/".join(str(code) for code in sorted(allowed))
        raise RuntimeError(f"{step}: expected {expected}, received {actual}")


def main():
    if len(sys.argv) != 4:
        print("Usage: python3 smtp_client_starter.py SERVER_HOST PORT LEHIGH_ID")
        return 1

    server_host = sys.argv[1]
    try:
        serverPort = int(sys.argv[2])
    except ValueError:
        print("PORT must be an integer between 1 and 65535")
        return 1
    if not 1 <= serverPort <= 65535:
        print("PORT must be between 1 and 65535")
        return 1

    LEHIGH_ID = sys.argv[3]
    if not re.fullmatch(r"[A-Za-z0-9._-]+", LEHIGH_ID):
        print("LEHIGH_ID may contain only letters, numbers, ., _, and -")
        return 1

    sender = f"{LEHIGH_ID}@cse342.test"
    recipient = "mushu@sunlab.test"
    client_name = f"{LEHIGH_ID}.cse342.test"
    msg = (
        f"From: {sender}\r\n"
        f"To: {recipient}\r\n"
        f"Subject: SMTP Programming Assignment - {LEHIGH_ID}\r\n"
        "\r\n"
        "I love computer networks!"
    )

    mailserver = server_host
    clientSocket = None
    reader = None

    try:
        # Fill in start 1: create the socket, set a timeout, connect, and create reader.
        # Student comment required: explain the timeout and line-oriented reader.

        # The timeout limits how long the client will wait for the connection to the server.
        # Otherwise, it might wait indefinitely if the connection cannot be established.
        # The line-oriented reader allows the client to read the server's SMTP replies one line at a time using readline().
        # This is useful because SMTP protocol lines end with CRLF.

        clientSocket = socket(AF_INET, SOCK_STREAM)
        clientSocket.settimeout(10)
        clientSocket.connect((mailserver, serverPort))
        reader = clientSocket.makefile("rb")

        # Fill in end 1

        code, _ = receive_reply(reader)
        require_code(code, {220}, "server greeting")

        # This provided HELO example shows how to encode text and send bytes.
        helo_command = f"HELO {client_name}\r\n"
        print(f"C: HELO {client_name}")
        clientSocket.sendall(helo_command.encode("utf-8"))
        code, _ = receive_reply(reader)
        require_code(code, {250}, "HELO")

        # Fill in start 2: build a CRLF-terminated MAIL FROM command, encode it,
        # Student comment required: explain the sender envelope and reply code.

        # The sender envelope specifies the email address of the sender.
        # The MAIL FROM command starts the SMTP envelope and informs the server of the sender's address.
        # The expected reply code for a successful MAIL FROM command is 250,
        # indicating that the server has accepted the sender's address.

        mail_from_command = f"MAIL FROM:<{sender}>\r\n"
        print(f"C: {mail_from_command.strip()}")
        clientSocket.sendall(mail_from_command.encode("utf-8"))
        code, _ = receive_reply(reader)
        require_code(code, {250}, "MAIL FROM")

        # Fill in end 2

        # Fill in start 3: build, encode, and send a CRLF-terminated RCPT TO
        # Student comment required: explain the recipient envelope and replies.

        # The recipient envelope specifies the email address of the recipient.
        # The RCPT TO command informs the server of the recipient's address.
        # A 250 reply means the recipient was accepted, while a 251 reply
        # means the server will forward the message to the recipient.
        
        rcpt_to_command = f"RCPT TO:<{recipient}>\r\n"
        print(f"C: {rcpt_to_command.strip()}")
        clientSocket.sendall(rcpt_to_command.encode("utf-8"))
        code, _ = receive_reply(reader)
        require_code(code, {250, 251}, "RCPT TO")

        # Fill in end 3

        # Fill in start 4: encode and send "DATA\r\n" with
        # Student comment required: explain why content cannot be sent before 354.

        # The DATA command indicates that the client is ready to send the email content.
        # The client must wait for the server's 354 reply before sending the content to ensure that the server is ready to receive it.

        data_command = "DATA\r\n"
        print(f"C: {data_command.strip()}")
        clientSocket.sendall(data_command.encode("utf-8"))
        code, _ = receive_reply(reader)
        require_code(code, {354}, "DATA")

        # Fill in end 4

        # Fill in start 5: encode the prepared msg value and send it with
        # Student comment required: explain the headers, blank line, and body.

        # The headers provide metadata about the email, such as the sender, recipient, and subject.
        # The blank line separates the headers from the body of the email, which contains the actual message.
        # The body of the email contains the actual message content.

        print(f"C: {msg.strip()}")
        clientSocket.sendall(msg.encode("utf-8"))

        # Fill in end 5

        # Fill in start 6: encode endmsg, send it with clientSocket.sendall(),
        # Student comment required: explain <CRLF>.<CRLF> and the final 250.

        # The <CRLF>.<CRLF> sequence indicates the end of the message data in SMTP.
        # The server responds with a 250 reply code to confirm that it has successfully received the message.
        # Dot-stuffing prevents a line beginning with "." in the message body
        # from being mistaken for the end-of-message marker.

        endmsg = "\r\n.\r\n"
        print(f"C: {endmsg.strip()}")
        clientSocket.sendall(endmsg.encode("utf-8"))
        code, _ = receive_reply(reader)
        require_code(code, {250}, "ENDMSG")

        # Fill in end 6

        # Fill in start 7: encode and send "QUIT\r\n" with
        # Student comment required: explain why the client waits before closing.

        # The client waits for a 221 reply after sending QUIT to confirm that the server
        # has acknowledged the termination of the SMTP session before closing the connection.

        quit_command = "QUIT\r\n"
        print(f"C: {quit_command.strip()}")
        clientSocket.sendall(quit_command.encode("utf-8"))
        code, _ = receive_reply(reader)
        require_code(code, {221}, "QUIT")

        # Fill in end 7

        return 0

    except (OSError, RuntimeError) as error:
        print(f"ERROR: {error}")
        return 1
    finally:
        if reader is not None:
            reader.close()
        if clientSocket is not None:
            clientSocket.close()

if __name__ == "__main__":
    raise SystemExit(main())

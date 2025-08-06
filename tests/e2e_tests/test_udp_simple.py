"""
Simple UDP test to verify communication works.
"""

import socket
import threading
import time


def sender():
    """Send test messages."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", 0))  # Bind to random port

    for i in range(5):
        message = f"TEST|{i}|Hello World"
        print(f"Sending: {message}")
        sock.sendto(message.encode(), ("127.0.0.1", 5001))
        time.sleep(2)

    sock.close()


def receiver():
    """Receive test messages."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(1.0)
    sock.bind(("", 5001))

    print("Receiver started, waiting for messages...")

    try:
        while True:
            try:
                data, addr = sock.recvfrom(4096)
                message = data.decode()
                print(f"Received: {message} from {addr}")
            except socket.timeout:
                print(".", end="", flush=True)
    except KeyboardInterrupt:
        print("\nReceiver stopped")
    finally:
        sock.close()


if __name__ == "__main__":
    # Start receiver in a thread
    receiver_thread = threading.Thread(target=receiver)
    receiver_thread.daemon = True
    receiver_thread.start()

    # Wait a moment for receiver to start
    time.sleep(1)

    # Start sender
    sender()

    # Wait for receiver to finish
    receiver_thread.join(timeout=15)

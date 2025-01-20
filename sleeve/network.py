import socket
import struct

class ESP32Client:
    def __init__(self, host, port=80):
        self.host = host
        self.port = port
        self.socket = None
        self.buffer = b""  # Buffer to store incomplete data

    def connect(self):
        """Connect to the ESP32 server."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))

    def disconnect(self):
        """Disconnect from the ESP32 server."""
        if self.socket:
            self.socket.close()
            self.socket = None

    def fetch_data(self):
        """Fetch data from the ESP32 in binary format."""
        if not self.socket:
            raise RuntimeError("Not connected to ESP32")

        # Ensure the buffer contains enough for the header
        self.buffer = self._receive_data(6, self.buffer)
        if len(self.buffer) < 6:
            return None  # Wait for more data

        # Parse the header
        n_channels, samples_per_packet = struct.unpack("BB", self.buffer[:2])
        timestamp = struct.unpack("<I", self.buffer[2:6])
        self.buffer = self.buffer[6:]  # Remove processed header

        # Calculate the payload size
        payload_size = n_channels * samples_per_packet * 2  # 2 bytes per sample

        # Ensure the buffer contains enough for the payload
        self.buffer = self._receive_data(payload_size, self.buffer)
        if len(self.buffer) < payload_size:
            return None  # Wait for more data

        # Extract and parse the payload
        payload = self.buffer[:payload_size]
        self.buffer = self.buffer[payload_size:]  # Remove processed payload

        # Parse the payload into channel data
        data = []
        for i in range(samples_per_packet):
            start = i * n_channels * 2
            end = start + n_channels * 2
            sample = struct.unpack(f"<{n_channels}H", payload[start:end])
            data.append(sample)

        return {
            "n_channels": n_channels,
            "samples_per_packet": samples_per_packet,
            "timestamp": timestamp,
            "data": data,
        }

    def _receive_data(self, expected_size, buffer):
        """
        Ensure the buffer contains at least `expected_size` bytes by
        receiving data from the socket and appending it to the buffer.
        """
        while len(buffer) < expected_size:
            try:
                chunk = self.socket.recv(expected_size - len(buffer))
                if not chunk:
                    raise RuntimeError("Socket connection lost")
                buffer += chunk
            except socket.timeout:
                break  # Allow non-blocking behavior for partial data
        return buffer

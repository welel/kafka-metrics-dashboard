import struct


class LengthBasedCommunicationMixin:
    """The mixin provides length-based communication using sockets.

    It works with connected sockets and uses a length buffer of size 4.

    Attributes:
        FORMAT_CODE (str): The format code to be used for packing and unpacking
                           the length of the data. Defaults to '>I' which
                           indicates a big-endian (network order) unsigned
                           integer.
        LENGTH_BUFF_SIZE (int): The size of the length buffer. Defaults to 4.
    """

    FORMAT_CODE, LENGTH_BUFF_SIZE = '>I', 4
    """
    The '>I' format in the struct.unpack('>I', data) expression tells the
    function to interpret the data as a big-endian (network order) unsigned
    integer. This representation always requires exactly 4 bytes.
    """

    def send(self, sock, data):
        """Sends the data through the socket after packing it with its length.

        Args:
          sock (socket.socket): The socket through which the data will be sent.
          data (bytes): The data to be sent.
        """
        data = struct.pack(self.FORMAT_CODE, len(data)) + data
        sock.sendall(data)

    def recv(self, sock):
        """Receives data through the socket after unpacking its length.

        Args:
            sock (socket.socket): The socket through which the data will be
                received.

        Returns:
            bytes: The received data.
            None: If no data was received.
        """
        length_buff = sock.recv(self.LENGTH_BUFF_SIZE)
        if not length_buff:
            return None
        length, = struct.unpack(self.FORMAT_CODE, length_buff)
        return self._recvall(sock, length)

    def _recvall(self, sock, count):
        """Receives the specified amount of data through the socket.

        Args:
            sock (socket.socket): The socket through which the data will be
                received.
            count (int): The amount of data to be received.

        Returns:
            bytes: The received data.
            None: If no data was received.
        """
        buffer = []
        while count > 0:
            received_data = sock.recv(count)
            if not received_data:
                return None
            buffer.append(received_data)
            count -= len(received_data)
        return b"".join(buffer)

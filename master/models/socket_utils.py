#!/usr/bin/env python3
# Documentation: https://docs.python.org/3/library/struct.html
import socket, json, struct

def sendJson(socket, object):
    '''Covert the object into JSON string and sent it off via socket.

    Parameters
    ----------
    socket : socket
        Network socket.
    object : object
        An object that can be JOSNified.
    '''

    jsonString = json.dumps(object)
    data = jsonString.encode("utf-8")
    jsonLength = struct.pack("!i", len(data))
    socket.sendall(jsonLength)
    socket.sendall(data)

def recvJson(socket):
    '''Receive a JSON string via socket and covert it back to original object

    Parameters
    ----------
    socket : socket
        Network socket.

    Returns
    -------
    object
        An object sent from the other end of socket connection.
    '''
    buffer = socket.recv(4)
    jsonLength = struct.unpack("!i", buffer)[0]

    # Reference: https://stackoverflow.com/a/15964489/9798310
    buffer = bytearray(jsonLength)
    view = memoryview(buffer)
    while jsonLength:
        nbytes = socket.recv_into(view, jsonLength)
        view = view[nbytes:]
        jsonLength -= nbytes

    jsonString = buffer.decode("utf-8")
    return json.loads(jsonString)

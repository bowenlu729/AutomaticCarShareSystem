import os, sys, socket
import numpy, pickle, face_recognition
from datetime import datetime, timedelta
from models import socket_utils, security, rest, webdata


HOST = ""
PORT = 5678


def main():
    '''Start Master Pi master service'''

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()

        print("Listening on {}...".format((HOST, PORT)))
        while True:
            print("Waiting for Agent Pi...")
            conn, addr = s.accept()
            with conn:
                print("Accepted connection from {}...".format(addr))

                data = socket_utils.recvJson(conn)
                resp = updateReservation(data)
                socket_utils.sendJson(conn, resp)

            print("Agent Pi closed connection")


def updateReservation(data):
    '''Update reservation based on data sent from Agent Pi.

    Parameters
    ----------
    data : dict {
        carId : int
            Car id.
        status : dict
            Status changes.
        auth : dict
            Authentication data - username/password or encodings.
        gps : dict
            Geographic location and coordinates.
    }

    Returns
    -------
    dict {
        body : dict
            A member dict.
        error : str
            Error message if there's any.
    }
        Predefined API return data structure.
    '''

    if "encodings" in data["auth"]:
        member = verifyEncodings(data["auth"]["encodings"])
    else:
        member = security.verifyPassword(
                data["auth"]["username"], data["auth"]["password"])
    if member is None:
        return {"error": "Error on verifying member"}

    reservation = findReservation(
            member["id"], data["carId"], data["status"]["from"])
    if reservation is None:
        return {"error": "Error on finding reservation"}

    if not alterReservation(reservation["id"], data["status"]["to"], data["gps"]):
        return {"error": "Error on altering reservation"}

    return {
        "error": None,
        "body": member
    }


def verifyEncodings(encodings):
    '''Verify facial recognition encodings.

    Parameters
    ----------
    encodings : list
        A list of encodings extracted from an image.

    Returns
    -------
    dict
        Member dict if session is valid. Otherwise, None.
    '''

    if encodings is None:
        return None

    encodings = [numpy.array(e) for e in encodings]
    if len(encodings) != 1:
        return None

    datasetFile = os.path.join("instance", "encodings.pickle")
    dataset = pickle.loads(open(datasetFile, "rb").read())
    matches = face_recognition.compare_faces(dataset["encodings"], encodings[0])
    if True in matches:
        matchedIdxs = [i for (i, b) in enumerate(matches) if b]
        counts = {}
        for i in matchedIdxs:
            name = dataset["names"][i]
            counts[name] = counts.get(name, 0) + 1

        username = max(counts, key=counts.get)
    else:
        return None

    return security.verifyPassword(username, None, noPassword=True)


def findReservation(memberId, carId, status):
    '''Find reservation matching member id, car id and status.

    Parameters
    ----------
    memberId : int
        Member id.
    carId : int
        Car id.
    status : int
        Reservation status.

    Returns
    -------
    dict
        Reservation dict if session is valid. Otherwise, None.
    '''

    params = {
        "memberId": memberId,
        "carId": carId,
        "status": status
    }
    resp = rest.get("reservation", params=params)
    if resp is None or resp["error"] is not None:
        return None

    nowDt = datetime.utcnow()
    reservations = resp["body"]
    for reservation in reservations:
       rsvDt = webdata.strToDatetime(reservation["reservedTime"])
       rtnDt = rsvDt + timedelta(hours=reservation["reservedHours"])
       if nowDt >= rsvDt and nowDt < rtnDt:
           return reservation

    return None


def alterReservation(reservationId, status, gps):
    '''Alter details of reservation.

    Parameters
    ----------
    reservationId : int
        Reservation id.
    status : int
        Reservation status.
    gps : dict
        Geographic location and coordinates.

    Returns
    -------
    bool
        True if success. Otherwise, False.
    '''

    params = {
        "id": reservationId,
        "status": status
    }
    if gps is not None:
        params.update(gps)
    resp = rest.put("reservation", data=params)
    if resp is None or resp["error"] is not None:
        return False

    return True


if __name__ == "__main__":
    main()

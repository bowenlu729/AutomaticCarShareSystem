import os, sys, json, socket, random
import cv2, imutils, face_recognition
sys.path.append(os.path.join("..", "master"))
from models import socket_utils


CONFIG_JSON = os.path.join(os.path.dirname(__file__), "config.json")


with open(CONFIG_JSON, "r") as f:
    config = json.load(f)


def main():
    '''Start Agent Pi application'''

    while True:
        print("[U]nlock")
        print("[R]eturn")
        print("[Q]uit")
        sel = input("Select: ").upper()
        print()

        if sel in ["U", "R"]:
            if sel == "U":
                gps = None
            else:
                gps = getGPSLocation()

            resp = selectAuthType(sel, gps)
            if resp is not None:
                if resp["error"] is None:
                    print("SUCCESS")
                    if sel == "U":
                        print("{} {} starts using this car".format(
                                resp["body"]["firstName"], resp["body"]["lastName"]))
                    else:
                        print("{} {} returns this car at {}".format(
                                resp["body"]["firstName"], resp["body"]["lastName"], gps["location"]))
                    break
                else:
                    print("FAILURE")
        elif sel == "Q":
            print("Bye")
            break
        else:
            print("Unrecognised selection")
        print()


GPS_JSON = os.path.join(os.path.dirname(__file__), "gps.json")

def getGPSLocation():
    '''Obtain geographic location and coordinates.

    Parameters
    ----------
    None

    Returns
    -------
    dict
        Geographic location and coordinates.
    '''

    with open(GPS_JSON, "r") as f:
        locations = json.load(f)

    return locations[random.randint(0, len(locations) - 1)]


def selectAuthType(s1, gps):
    '''Select authentication type.

    Parameters
    ----------
    s1 : str
        "U" for unlock or "R" for return.
    gps : dict
        Geographic location and coordinates.

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

    resp = None
    while resp is None:
        print("[P]assword")
        print("[F]acial Recognition")
        print("[B]ack")
        sel = input("Select: ").upper()
        print()

        if sel == "P":
            auth = {
                "username": input("Username: "),
                "password": input("Password: ")
            }
            resp = execCommand(s1, auth, gps)
        elif sel == "F":
            scanfile = input("Scan file: ")
            auth = {
                    "encodings": encodeImage(scanfile)
            }
            resp = execCommand(s1, auth, gps)
        elif sel == "B":
            break
        else:
            print("Unrecognised selection")
        print()

    return resp


SCAN_DIR = os.path.join(os.path.dirname(__file__), "scan")

def encodeImage(scanfile):
    '''Generate encodings from a file.

    Parameters
    ----------
    scanfile : str
        Filename of image being encoded.

    Returns
    -------
    list
        A list of face encodings on success. Otherwise, None.
    '''

    try:
        image = cv2.imread(os.path.join(SCAN_DIR, scanfile))
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        rgb = imutils.resize(image, width=240)
        boxes = face_recognition.face_locations(rgb, model="hog")
        encodings = face_recognition.face_encodings(rgb, boxes)
    except Exception:
        encodings = None

    return [e.tolist() for e in encodings] if encodings is not None else None


def execCommand(s1, auth, gps):
    '''Send command to Master Pi and execute it.

    Parameters
    ----------
    s1 : str
        "U" for unlock or "R" for return.
    auth : dict
        Authentication data - username/password or encodings.
    gps : dict
        Geographic location and coordinates.

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

    params = {
        "carId": config["agentId"],
        "status": {
            "from": 0 if s1 == "U" else 1,
            "to": 1 if s1 == "U" else 2
        },
        "auth": auth,
        "gps": gps
    }
    hostAddr = (config["masterHost"], config["masterPort"])
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(hostAddr)
        socket_utils.sendJson(s, params)
        resp = socket_utils.recvJson(s)

    return resp



if __name__ == "__main__":
    main()

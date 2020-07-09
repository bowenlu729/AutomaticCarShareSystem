from werkzeug.security import generate_password_hash, check_password_hash
from . import rest


def legitimateClient(ip):
    '''Check if client is legitimate.

    Parameters
    ----------
    ip : str
        Client IP address.

    Returns
    -------
    bool
        True if client is legitimate. Otherwise, False.
    '''

    return ip in ["127.0.0.1", "192.168.0.130"]


def hashPassword(password):
    '''Encrypt password

    Parameters
    ----------
    password : str
        Password in plaintext.

    Returns
    -------
    str
        Ciphertext of the encrypted password.
    '''

    return generate_password_hash(password)


def verifyPassword(username, password, noPassword=False):
    '''Verify username and password.

    Parameters
    ----------
    username: str
        Member's username.
    password: str
        Member's password.
    noPassword: bool (optional)
        Verify username only.

    Returns
    -------
    bool
        True if passed. Otherwise, False.
    '''

    if username is None or (password is None and not noPassword):
        return None

    resp = rest.get("member", params={"username": username})
    if resp["error"] is not None or len(resp["body"]) == 0:
        return None

    member = resp["body"][0]
    if not noPassword and not check_password_hash(member["password"], password):
        return None

    return member


def verifySession(sess):
    '''Check if the session is valid

    Parameters
    ----------
    sess : dict
        Flask session structure.

    Returns
    -------
    dict
        Member dict if session is valid. Otherwise, None.
    '''

    if "m" not in sess:
        return None

    resp = rest.get("member", params={"id": sess["m"]})
    if resp["error"] is not None or len(resp["body"]) == 0:
        return None

    member = resp["body"][0]

    return member

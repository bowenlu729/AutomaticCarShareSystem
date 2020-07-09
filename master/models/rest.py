import requests


REST_ROOT = "http://127.0.0.1:5000/api"


def _parseResponse(r):
    '''Extract data from RESTful API response structure.

    Parameters
    ----------
    r : dict
        RESTful API response structure.

    Returns
    -------
    dict
        The data part of RESTful API response structure.
    '''

    if r.status_code != 200:
        return None

    return r.json()


def get(endpoint, params=None):
    '''Wrapper to call RESTful API via requests GET method.

    Parameters
    ----------
    endpoint : str
        RESTful endpoint.
    params : dict (optional)
        Query string data.

    Returns
    -------
    dict
        The data part of RESTful API response structure.
    '''

    r = requests.get("%s/%s" % (REST_ROOT, endpoint), params=params)
    return _parseResponse(r)


def post(endpoint, data=None):
    '''Wrapper to call RESTful API via requests POST method.

    Parameters
    ----------
    endpoint : str
        RESTful endpoint.
    params : dict (optional)
        Payload data.

    Returns
    -------
    dict
        The data part of RESTful API response structure.
    '''
    r = requests.post("%s/%s" % (REST_ROOT, endpoint), data=data)
    return _parseResponse(r)


def put(endpoint, data=None):
    '''Wrapper to call RESTful API via requests PUT method.

    Parameters
    ----------
    endpoint : str
        RESTful endpoint.
    params : dict (optional)
        Payload data.

    Returns
    -------
    dict
        The data part of RESTful API response structure.
    '''

    r = requests.put("%s/%s" % (REST_ROOT, endpoint), data=data)
    return _parseResponse(r)

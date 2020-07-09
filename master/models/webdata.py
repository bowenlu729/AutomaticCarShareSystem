from datetime import datetime, timezone
from . import security


def castInput(dataType, data):
    '''Cast input data to a specified data type.

    Parameters
    ---------
    dataType : type
        Target data type.
    data : str
        The original data string.

    Returns
    -------
    type
        The value represents the input data in target data type.
    '''

    if dataType is None or data is None:
        return None

    try:
        if dataType == "password":
            value = security.hashPassword(data)
        elif dataType == "datetime":
            value = datetime.fromisoformat(data)
        elif dataType is bool:
            value = True if data == "True" else False
        elif dataType in [int, float]:
            value = dataType(data)
        elif dataType is str:
            value = data
        else:
            value = None
    except ValueError:
        value = None

    return value


def parseInput(rawParams, keyTypes):
    '''Parse raw paramters and cast all desired fields to proper data types.

    Parameters
    ----------
    rawParams : dict
        A parameter dict normally passed in from RESTful API callers.

    Returns
    -------
    dict
        A sanitised parameter dict.
    '''

    params = {}
    for k, t in keyTypes.items():
        if k in rawParams:
            params[k] = castInput(t, rawParams[k])

    return params


def statusToStr(status):
    '''Quick mapping between status numbers and human readable strings.

    Parameters
    ----------
    status : int
        Status number.

    Returns
    -------
    str
        A human readable string.
    '''

    if status == -1:
        return "Canceled"
    if status == 0:
        return "Reserved"
    elif status == 1:
        return "In-use"
    elif status == 2:
        return "Returned"
    else:
        return None


def datetimeToStr(dt):
    '''Convert a datetime object to a time string.

    Parameters
    ----------
    dt : datetime
        A datetime object.

    Returns
    -------
    str
        A time string.
    '''

    return dt.strftime("%Y-%m-%d %H:%M")


def strToDatetime(s):
    '''Convert a time string to a datetime object.

    Parameters
    ----------
    s : str
        A time string.

    Returns
    -------
    datetime
        A datetime object.
    '''

    try:
        return datetime.fromisoformat(s)
    except ValueError:
        return None


def convertUtcToLocal(dt):
    '''Convert datetime object from UTC to local time zone

    Parameters
    ----------
    dt : datetime
        A datetime object with UTC time zone

    Returns
    -------
    datetime
        A datetime object with local time zone
    '''

    if dt is None:
        return None

    return dt.replace(tzinfo=timezone.utc).astimezone(tz=None)


def convertLocalToUtc(dt):
    '''Convert datetime object from local to UTC time zone

    Parameters
    ----------
    dt : datetime
        A datetime object with local time zone

    Returns
    -------
    datetime
        A datetime object with UTC time zone
    '''

    if dt is None:
        return None

    return dt.replace(tzinfo=None).astimezone(tz=timezone.utc)

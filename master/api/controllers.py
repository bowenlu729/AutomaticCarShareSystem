from flask import Blueprint, jsonify, request
from flask_mail import Message
from werkzeug.exceptions import abort
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor
from models import security, webdata


api = Blueprint("api", __name__)

from app import app
from app import mail

mysql = MySQL(cursorclass=DictCursor)
mysql.init_app(app)


@api.route("/member", methods=["GET", "POST"])
def routeMember():
    '''RESTful endpoint to access member data.

    Parameters for GET method
    -------------------------
    id : int
        Member id.
    username : str
        Member's username.

    Returns
    -------
    dict {
        body : list
            A list of member dicts.
        error : str
            Error message if there's any.
    }
        Predefined API return data structure.

    Parameters for POST method
    --------------------------
    username : str
        Member's username.
    password : str
        Member's password.
    firstName : str
        Member's first name.
    lastName : str
        Member's last name.
    email : str
        Member's email.
    userType : str
        Member's type.

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

    # Allow only clients from specific origins
    if not security.legitimateClient(request.remote_addr):
        abort(401, "unauthorised request")

    if request.method == "GET":
        # Define parameter types
        keyTypes = {
            "id": int,
            "username": str
        }
        # Parse input parameters
        params = webdata.parseInput(request.args, keyTypes)
        resp = {
            "error": None,
            "body": getMembers(params)
        }
    else: # POST
        # Define parameter types
        keyTypes = {
            "username": str,
            "password": "password",
            "firstName": str,
            "lastName": str,
            "email": str,
            "userType": str,
        }
        # Parse input parameters
        params = webdata.parseInput(request.form, keyTypes)
        memberId = createMember(params)
        if memberId > 0:
            resp = {
                "error": None,
                "body": getMembers({"id": memberId})[0]
            }
        else:
            resp = {"error": "Error on creating member"}

    return jsonify(resp)


def getMembers(params):
    '''Fetch members by given criteria.

    Parameters
    ----------
    params : dict {
        id : int (optional)
            Member id.
        username : str (optional)
            Member's username.
    }

    Returns
    -------
    list of dict {
        id : int
            Member id.
        username : str
            Member's username.
        password : str
            Member's encrypted password.
        firstName : str
            Member's first name.
        lastName : str
            Member's last name.
        email : str
            Member's email address.
        userType : str
            Member's type.
    }
        All the members that match the criteria.
    '''

    try:
        conn = mysql.get_db()
        cur = conn.cursor()

        # Covert criteria to SQL condition syntax
        criteria = ["%s = %%(%s)s" % (k, k) for k in params]
        sql = "SELECT * FROM Members" + (" WHERE " + " AND ".join(criteria) if len(criteria) > 0 else "")
        # Perform SQL query
        cur.execute(sql, params)
        # There could be zero, one or multiple rows returned
        rows = cur.fetchall()

        cur.close()
    except Exception as e:
        abort(400, e)

    return rows


def createMember(params):
    '''Create a member account by given details

    Parameters
    ----------
    params : dict {
        username : str
            Member's username.
        password : str
            Member's password in plaintext.
        firstName : str
            Member's first name.
        lastName : str
            Member's last name.
        email : str
            Member's email address.
    }

    Returns
    -------
    int
        Id of the member just created.
    '''
    id = -1
    try:
        conn = mysql.get_db()
        cur = conn.cursor()

        # Covert criteria to SQL condition syntax
        criteria = ["%s = %%(%s)s" % (k, k) for k in params]
        sql = "INSERT INTO Members SET " + ", ".join(criteria)
        # Perform SQL query
        if cur.execute(sql, params) == 1:
            # Aquire id of the member just created
            sql = "SELECT LAST_INSERT_ID() AS id"
            if cur.execute(sql) == 1:
                row = cur.fetchone()
                id = int(row["id"])

        # Commit the transaction
        conn.commit()
        cur.close()
    except Exception as e:
        abort(400, e)

    return id


@api.route("/car", methods=["GET"])
def routeCar():
    '''RESTful endpoint to access car data.

    Parameters for GET method
    -------------------------
    id : int (optional)
        Car's id.
    make : str (optional)
        Car's brand.
    bodyType : str (optional)
        Car's body type.
    colour : str (optional)
        Car's colour.
    seats : int (optional)
        Number of seats.
    location : str (optional)
        Car's current location.
    costPerHour : float (optional)
        Cost per hour.
    available : bool (optional)
        Whether the car is available.

    Returns
    -------
    dict {
        body : list
            A list of car dicts.
        error : str
            Error message if there's any.
    }
        Predefined API return data structure.
    '''

    # Allow only clients from specific origins
    if not security.legitimateClient(request.remote_addr):
        abort(401, "unauthorised request")

    # Define parameter types
    keyTypes = {
        "id": int,
        "make": str,
        "bodyType": str,
        "colour": str,
        "seats": int,
        "location": str,
        "costPerHour": float,
        "available": bool,
        "reported": bool
    }
    # Parse input parameters
    params = webdata.parseInput(request.args, keyTypes)
    resp = {
        "error": None,
        "body": getCars(params)
    }

    return jsonify(resp)


def getCars(params):
    '''Fetch cars by given criteria.

    Parameters
    ----------
    params : dict {
        id : int (optional)
            Car's id.
        make : str (optional)
            Car's brand.
        bodyType : str (optional)
            Car's body type.
        colour : str (optional)
            Car's colour.
        seats : int (optional)
            Number of seats.
        location : str (optional)
            Car's current location.
        costPerHour : float (optional)
            Cost per hour.
        available : bool (optional)
            Whether the car is available.
    }

    Returns
    -------
    list of dict {
        id : int
            Car's id.
        make : str
            Car's brand.
        bodyType : str
            Car's body type.
        colour : str
            Car's colour.
        seats : int
            Number of seats.
        location : str
            Car's current location.
        latitude : float
            Car's geographic coordinate that specifies the north-south position
        longitude : float
            Car's geographic coordinate that specifies the east–west position
        costPerHour : float
            Cost per hour.
        available : bool
            Whether the car is available.
    }
        All the cars that mathc the criteria.
    '''

    try:
        conn = mysql.get_db()
        cur = conn.cursor()

        criteria = []
        # Covert criteria to SQL condition syntax
        for k in params:
            if type(params[k]) is str:
                criteria.append("%s LIKE %%(%s)s" % (k, k))
                params[k] = "%" + params[k] + "%"
            elif type(params[k]) is float:
                criteria.append("ABS(%s - %%(%s)s) < 1.0" % (k, k))
            else: # int or bool
                criteria.append("%s = %%(%s)s" % (k, k))
        sql = "SELECT * FROM Cars" + (" WHERE " + " AND ".join(criteria) if len(criteria) > 0 else "")
        # Perform SQL query
        cur.execute(sql, params)
        # There could be zero, one or multiple rows returned
        rows = cur.fetchall()

        cur.close()
    except Exception as e:
        abort(400, e)

    return rows


@api.route("/reservation", methods=["GET", "POST", "PUT"])
def routeReservation():
    '''RESTful endpoint to access reservation data.

    Parameters for GET method
    -------------------------
    id : int (optional)
        Reservation id.
    memberId : int (optional)
        Id of member who made the reservation.
    carId : int (optional)
        Id of car that is reserved.
    status : int (optional)
        Status of reservation (-1: canceled, 0: reserved, 1: in-use, 2: returned)

    Returns
    -------
    dict {
        body : list
            A list of reservation dicts.
        error : str
            Error message if there's any.
    }
        Predefined API return data structure.

    Parameters for POST method
    --------------------------
    memberId : int
        Id of member who is going to make the reservation.
    carId : int
        Id of car that is going to be reserved.
    reservedTime : str
        Time when the car can be unlocked.
    reservedHours : int
        Hours that the car is reserved for.

    Returns
    -------
    dict {
        body : dict
            A reservation dict.
        error : str
            Error message if there's any.
    }
        Predefined API return data structure.

    Parameters for PUT method
    -------------------------
    id : int
        Reservation id.
    location : str (optional)
        Car's current location.
    latitude : float (optional)
        Car's current geographic coordinate.
    longitude : float (optional)
        Car's current geographic coordinate.
    status : int
        Car's current status.

    Returns
    -------
    dict {
        body : dict
            A reservation dict.
        error : str
            Error message if there's any.
    }
        Predefined API return data structure.
    '''

    # Allow only clients from specific origins
    if not security.legitimateClient(request.remote_addr):
        abort(401, "unauthorised request")

    if request.method == "GET":
        # Define parameter types
        keyTypes = {
            "id": int,
            "memberId": int,
            "carId": int,
            "status": int
        }
        # Parse input parameters
        params = webdata.parseInput(request.args, keyTypes)
        resp = {
            "error": None,
            "body": getReservations(params)
        }
    elif request.method == "POST":
        # Define parameter types
        keyTypes = {
            "memberId": int,
            "carId": int,
            "reservedTime": "datetime",
            "reservedHours": int
        }
        # Parse input parameters
        params = webdata.parseInput(request.form, keyTypes)
        reservationId = createReservation(params)
        if reservationId > 0:
            resp = {
                "error": None,
                "body": getReservations({"id": reservationId})[0]
            }
        else:
            resp = {"error": "Error on creating reservation"}
    else: # PUT
        # Define parameter types
        keyTypes = {
            "id": int,
            "location": str,
            "latitude": float,
            "longitude": float,
            "status": int
        }
        # Parse input parameters
        params = webdata.parseInput(request.form, keyTypes)
        reservationId = updateReservation(params)
        if reservationId > 0:
            resp = {
                "error": None,
                "body": getReservations({"id": reservationId})[0]
            }
        else:
            resp = {"error": "Error on updating reservation"}

    return jsonify(resp)


def getReservations(params):
    '''Fetch reservations by given criteria.

    Parameters
    ----------
    params : dict {
        id : int (optional)
            Reservation id.
        memberId : int (optional)
            Id of member who made the reservation.
        carId : int (optional)
            Id of car that is reserved.
        status : int (optional)
            Status of reservation (-1: canceled, 0: reserved, 1: in-use, 2: returned)
    }

    Returns
    -------
    list of dict {
        id : int
            Reservation id.
        memberId : int
            Id of member who made the reservation.
        carId : int
            Id of car that is reserved.
        reservedTime : str
            Time when the car can be unlocked. (UTC time)
        reservedHours : int
            Hours that the car is reserved for.
        totalCost : float
            Total cost in the reservation.
        status : int
            Status of reservation.
    }
        All the members that match the criteria.
    '''

    try:
        conn = mysql.get_db()
        cur = conn.cursor()

        # Covert criteria to SQL condition syntax
        criteria = ["%s = %%(%s)s" % (k, k) for k in params]
        sql = "SELECT * FROM Reservations" + (" WHERE " + " AND ".join(criteria) if len(criteria) > 0 else "")
        # Perform SQL query
        cur.execute(sql, params)
        # There could be zero, one or multiple rows returned
        rows = cur.fetchall()

        # Convert datetime object to time string
        for row in rows:
            row["reservedTime"] = webdata.datetimeToStr(row["reservedTime"])

        cur.close()
    except Exception as e:
        abort(400, e)

    return rows


def createReservation(params):
    '''Create a reservation by given details.

    Parameters
    ----------
    params : dict {
        memberId : int
            Id of member who is going to make the reservation.
        carId : int
            Id of car that is going to be reserved.
        reservedTime : str
            Time when the car can be unlocked.
        reservedHours : int
            Hours that the car is reserved for.
    }

    Returns
    -------
    int
        Id of the reservation just created.
    '''

    id = -1
    # Fetch the car of interest
    cars = getCars({"id": params["carId"]})
    if len(cars) != 1:
        return id

    # Calculate total cost
    params["totalCost"] = float(cars[0]["costPerHour"]) * params["reservedHours"]

    try:
        conn = mysql.get_db()
        cur = conn.cursor()

        # Update car's availability in database
        sql = "UPDATE Cars SET available = FALSE WHERE id = %(carId)s AND available = TRUE"
        # Perform SQL query
        if cur.execute(sql, params) != 1:
            cur.close()
            return id

        # Create the reservation in database
        criteria = ["%s = %%(%s)s" % (k, k) for k in params]
        sql = "INSERT INTO Reservations SET " + ", ".join(criteria)
        # Perform SQL query
        if cur.execute(sql, params) == 1:
            # Aquire id of the reservation just created
            sql = "SELECT LAST_INSERT_ID() AS id"
            if cur.execute(sql) == 1:
                row = cur.fetchone()
                id = int(row["id"])

        # Commit the transaction
        conn.commit()
        cur.close()
    except Exception as e:
        abort(400, e)

    return id


def updateReservation(params):
    '''Update a reservation by given details

    Parameters
    ----------
    params : dict {
        id : int
            Reservation id.
        location : str (optional)
            Car's current location.
        latitude : float (optional)
            Car's current geographic coordinate.
        longitude : float (optional)
            Car's current geographic coordinate.
        status : int
            Car's current status.
    }

    Returns
    -------
    int
        Id of the reservation just updated.
    '''

    id = -1
    params["available"] = True if params["status"] in [-1, 2] else False

    try:
        conn = mysql.get_db()
        cur = conn.cursor()

        criteria = []
        for k in params:
            if k in ["available", "location", "latitude", "longitude"]:
                criteria.append("Cars.%s = %%(%s)s" % (k, k))
            elif k == "status":
                criteria.append("Reservations.%s = %%(%s)s" % (k, k))
        sql = "UPDATE Cars, Reservations SET " + ", ".join(criteria)
        sql += " WHERE Cars.id = Reservations.carId AND Reservations.id = %(id)s"
        if cur.execute(sql, params) in [1, 2]:
            id = params["id"]

        conn.commit()
        cur.close()
    except Exception as e:
        abort(400, e)

    return id


@api.route("/allMembers")
def routeAllMember():
    '''RESTful endpoint to access all members data.

    Returns
    -------
    dict {
        body : list
            A list of member dicts.
        error : str
            Error message if there's any.
    }
        Predefined API return data structure.

    '''
    resp = {"error": "Error on finding members"}

    # Allow only clients from specific origins
    resp = {
        "error": None,
        "body": getAllMembers()
    }

    return jsonify(resp)


def getAllMembers():
    '''Fetch all members.

    Parameters
    ----------
    
    Returns
    -------
    list of dict {
        id : int
            Member id.
        username : str
            Member's username.
        password : str
            Member's encrypted password.
        firstName : str
            Member's first name.
        lastName : str
            Member's last name.
        email : str
            Member's email address.
        userType : str
            Member's type.
    }
        All the members .
    '''

    try:
        conn = mysql.get_db()
        cur = conn.cursor()

        sql = "SELECT * FROM Members;"
        # Perform SQL query
        cur.execute(sql)
        # There could be zero, one or multiple rows returned
        rows = cur.fetchall()
        cur.close()
    except Exception as e:
        abort(400, e)

    return rows

@api.route("/searchMembers", methods=["GET", "POST"])
def routeSearchMembers():
    '''RESTful endpoint to members data.

    Parameters for GET method
    -------------------------
    username : str (optional)
        Member's username.
    email : str (optional)
        Member's email.

    Returns
    -------
    dict {
        body : list
            A list of member dicts.
        error : str
            Error message if there's any.
    }
        Predefined API return data structure.
    '''

    # Allow only clients from specific origins
    if not security.legitimateClient(request.remote_addr):
        abort(401, "unauthorised request")

    # Define parameter types
    keyTypes = {
        "username": str,
        "email": str
    }
    # Parse input parameters
    params = webdata.parseInput(request.args, keyTypes)
    resp = {
        "error": None,
        "body": searchMembers(params)
    }

    return jsonify(resp)


def searchMembers(params):
    '''Fetch members by given criteria.
    '''

    try:
        conn = mysql.get_db()
        cur = conn.cursor()

        criteria = []
        # Covert criteria to SQL condition syntax
        for k in params:
            criteria.append("%s LIKE %%(%s)s" % (k, k))
            params[k] = "%" + params[k] + "%"
        sql = "SELECT * FROM Members" + (" WHERE " + " AND ".join(criteria) if len(criteria) > 0 else "")
        # Perform SQL query
        cur.execute(sql, params)
        # There could be zero, one or multiple rows returned
        rows = cur.fetchall()
        cur.close()
    except Exception as e:
        abort(400, e)

    return rows

@api.route("/reportCar", methods=["GET", "POST"])
def reportCar():
    '''RESTful endpoint to members data.

    Parameters for GET method
    -------------------------
    id : str 
        Car's email.
    email : str 
        Member's email.
    content : str
        Report's content.

    Returns
    -------
    int
        Id of the car just updated.
    '''
    # Allow only clients from specific origins
    if not security.legitimateClient(request.remote_addr):
        abort(401, "unauthorised request")

    # Define parameter types
    keyTypes = {
        "id": int,
        "email": str,
        "content": str
    }   
    # Parse input parameters
    params = webdata.parseInput(request.args, keyTypes)

    resp = {
        "error": None,
        "body": createReport(params)
    }

    return jsonify(resp)
    
def createReport(params):

    try:
        conn = mysql.get_db()
        cur = conn.cursor()
        carId = params['id']
        email = params['email']
        content = params['content']

        msg = Message(content,
                  recipients=[email])
        msg.body = "Hi, Engineer! Car need to be repaired."
        # Send emails to engineer
        mail.send(msg)

        # Update car's report status in database
        sql = "UPDATE Cars SET reported = True,available = False WHERE id = " + str(carId)
        
        # Perform SQL query
        cur.execute(sql, params)
        # There could be zero, one or multiple rows returned
        rows = cur.fetchall()
        # Commit the transaction
        conn.commit()
        cur.close()

    except Exception as e:
        print(e)
        abort(400, e)

    return rows

@api.route("/modifyUser", methods=["GET", "POST"])
def modify():
    '''RESTful endpoint to member.

    Parameters for GET method
    -------------------------
    username : str
            Member's username.
    password : str
        Member's encrypted password.
    firstName : str
        Member's first name.
    lastName : str
        Member's last name.
    email : str
        Member's email address.
    userType : str
        Member's type.

    Returns
    -------
    int
        Id of the member just updated.
    '''
    # Allow only clients from specific origins
    if not security.legitimateClient(request.remote_addr):
        abort(401, "unauthorised request")

    # Define parameter types
    keyTypes = {
        "id":int,
        "username": str,
        "password": "password",
        "firstName": str,
        "lastName": str,
        "email": str,
        "userType": str,
    }
    # Parse input parameters
    params = webdata.parseInput(request.form, keyTypes)

    resp = {
        "error": None,
        "body": modifyUser(params),
    }

    return jsonify(resp)

def modifyUser(params):
    '''Update a member account by given details

    Parameters
    ----------
    params : dict {
        id : int
            Member's id.
        username : str
            Member's username.
        password : str
            Member's password in plaintext.
        firstName : str
            Member's first name.
        lastName : str
            Member's last name.
        email : str
            Member's email address.
    }

    Returns
    -------
    int
        Id of the member just created.
    '''
    id = params['id']
    try:
        conn = mysql.get_db()
        cur = conn.cursor()
        
        # Covert criteria to SQL condition syntax
        for k in params:
            if params[k]:
              criteria = ["%s = %%(%s)s" % (k, k)]
              
        sql = "UPDATE Members SET " + ", ".join(criteria) + " WHERE id = " + str(id)
        print(sql)
        # Perform SQL query
        cur.execute(sql, params)
        # Commit the transaction
        conn.commit()
        cur.close()
    except Exception as e:
        abort(400, e)

    return id
from flask import Blueprint, render_template, redirect, request, session, url_for, current_app
from models import rest, security, webdata, calendar


web = Blueprint("web", __name__)


@web.route("/", methods=["GET", "POST"])
@web.route("/welcome", methods=["GET", "POST"])
def welcome():
    '''Welcome URI.

    Parameters for GET method
    -------------------------
    None

    Parameters for POST method
    --------------------------
    username : str
        Member's username.
    password : str
        Member's password.
    '''

    member = security.verifySession(session)
    if member is not None:

        if member["userType"] == "admin":
            return redirect(url_for(".admin"))
            
        if member["userType"] == "manager":
            return redirect(url_for(".manager"))

        if member["userType"] == "engineer":
            return redirect(url_for(".engineer"))

        return redirect(url_for(".cars"))

    error = None
    if request.method == "POST":
        keyTypes = {
            "username": str,
            "password": str
        }
        params = webdata.parseInput(request.form, keyTypes)
        member = security.verifyPassword(params["username"], params["password"])
        if member is None:
            error = True
        else:
            session.clear()
            session["m"] = member["id"]
            error = False

            if member["userType"] == "admin":
                return redirect(url_for(".admin"))
            
            if member["userType"] == "manager":
                return redirect(url_for(".manager"))

            if member["userType"] == "engineer":
                return redirect(url_for(".engineer"))

            if not current_app.testing:
                return redirect(url_for("oauth.authorize"))

    return render_template("welcome.html", error=error, member=member)


@web.route("/register", methods=["GET", "POST"])
def register():
    '''Register URI.

    Parameters for GET method
    -------------------------
    None

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
        Member's email address.
    userType : str
        Member's type.
    '''

    error = None
    if request.method == "POST":
        keyTypes = {
            "username": str,
            "password": str,
            "firstName": str,
            "lastName": str,
            "email": str,
            "userType": str,
        }
        params = webdata.parseInput(request.form, keyTypes)
        resp = rest.post("member", data=params)
        if resp is None or resp["error"] is not None:
            error = True
        else:
            session.clear()
            error = False

    return render_template("register.html", error=error)


@web.route("/logout")
def logout():
    '''Logout URI.

    Parameters for GET method
    -------------------------
    None
    '''

    member = security.verifySession(session)
    session.clear()

    return render_template("logout.html", member=member)


@web.route("/cars", methods=["GET", "POST"])
def cars():
    '''Cars URI.

    Parameters for GET method
    -------------------------
    None

    Parameters for POST method
    --------------------------
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
    '''

    member = security.verifySession(session)
    if member is None:
        return redirect(url_for(".welcome"))

    params = {}
    if request.method == "POST":
        keyTypes = {
            "make": str,
            "bodyType": str,
            "colour": str,
            "seats": int,
            "location": str,
            "costPerHour": float
        }
        params = webdata.parseInput(request.form, keyTypes)

    params["available"] = True
    resp = rest.get("car", params=params)
    if resp is None or resp["error"] is not None:
        cars = None
    else:
        cars = resp["body"]

    return render_template("cars.html", member=member, params=params, cars=cars)


@web.route("/gmaps", methods=["GET", "POST"])
def gmaps():
    '''Maps URI.

    Parameters for GET method
    -------------------------
    None

    Parameters for POST method
    --------------------------
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
    '''

    member = security.verifySession(session)
    if member is None:
        return redirect(url_for(".welcome"))

    params = {}
    if request.method == "POST":
        keyTypes = {
            "make": str,
            "bodyType": str,
            "colour": str,
            "seats": int,
            "location": str,
            "costPerHour": float
        }
        params = webdata.parseInput(request.form, keyTypes)

    params["available"] = True
    resp = rest.get("car", params=params)
    if resp is None or resp["error"] is not None:
        cars = None
    else:
        cars = resp["body"]

    if cars is None:
        centre = {
            "latitude": -37.8744,
            "longitude": 145.1668
        }
    else:
        centre = {
            "latitude": 0.0,
            "longitude": 0.0
        }

        for car in cars:
            centre["latitude"] += car["latitude"]
            centre["longitude"] += car["longitude"]

        centre["latitude"] /= len(cars)
        centre["longitude"] /= len(cars)

    return render_template("gmaps.html", member=member, params=params, cars=cars, centre=centre)


def getCar(id):
    '''Get a car by given id.

    Parameters
    ----------
    id : int
        Car id.

    Returns
    -------
    dict
        Car dict collected via RESTful API.
    '''

    resp = rest.get("car", params={"id": id})
    if resp is None or resp["error"] is not None and len(resp["body"]) != 1:
        return None

    return resp["body"][0]


@web.route("/reserve", methods=["GET", "POST"])
def reserve():
    '''Reserve URI.

    Parameters for GET method
    -------------------------
    id : int
        Car id

    Parameters for POST method
    --------------------------
    carId : int
        Car id.
    reservedTime : str
        Time when the car can be unlocked.
    reservedHours : int
        Hours that the car is reserved for.
    '''

    member = security.verifySession(session)
    if member is None:
        return redirect(url_for(".welcome"))

    error = None
    if request.method == "GET":
        keyTypes = {
            "id": int
        }
        params = webdata.parseInput(request.args, keyTypes)
        car = getCar(params["id"])
        if car is None or not car["available"]:
            error = True
    else: # POST
        keyTypes = {
            "carId": int,
            "reservedTime": "datetime",
            "reservedHours": int
        }
        params = webdata.parseInput(request.form, keyTypes)
        params["memberId"] = member["id"]
        params["reservedTime"] = webdata.convertLocalToUtc(params["reservedTime"])
        car = getCar(params["carId"])
        if car is None or not car["available"]:
            error = True
        else:
            resp = rest.post("reservation", data=params)
            if resp is None or resp["error"] is not None:
                error = True
            else:
                reservation = resp["body"]
                reservation["reservedTime"] = webdata.strToDatetime(reservation["reservedTime"])
                #if not current_app.testing:
                #    calendar.insertEvent(session["credentials"], member, car, reservation)
                error = False

    return render_template("reserve.html", error=error, member=member, car=car)


@web.route("/history")
def history():
    '''Reserve URI.

    Parameters for GET method
    -------------------------
    None
    '''

    member = security.verifySession(session)
    if member is None:
        return redirect(url_for(".welcome"))
    else:
        staff = member
    
    if request.method == "GET":
        keyTypes = {
            "id": int
        }
        params = webdata.parseInput(request.args, keyTypes)
        resp = rest.get("member", params=params)
        for m in resp['body']:
            member = m

    params = {"memberId": member["id"]}
    resp = rest.get("reservation", params=params)
    if resp is None or resp["error"] is not None:
        reservations = None
    else:
        reservations = resp["body"]

    if reservations is not None:
        for reservation in reservations:
            params = {"id": reservation["carId"]}
            resp = rest.get("car", params=params)
            if resp is None or resp["error"] is not None:
                reservation["car"] = None
            else:
                reservation["car"] = resp["body"][0]

            reservation["reservedTime"] = webdata.strToDatetime(reservation["reservedTime"])
            reservation["reservedTime"] = webdata.convertUtcToLocal(reservation["reservedTime"])
            reservation["reservedTimeStr"] = webdata.datetimeToStr(reservation["reservedTime"])
            reservation["statusStr"] = webdata.statusToStr(reservation["status"])

    return render_template("history.html", staff=staff,member=member, reservations=reservations)


@web.route("/cancel")
def cancel():
    '''Reserve URI.

    Parameters for GET method
    -------------------------
    id : int
        Reservation id.
    '''

    member = security.verifySession(session)
    if member is None:
        return redirect(url_for(".welcome"))

    keyTypes = {
        "id": int
    }
    params = webdata.parseInput(request.args, keyTypes)
    params["status"] = -1
    resp = rest.put("reservation", data=params)
    if resp is None or resp["error"] is not None:
        error = True
    else:
        reservation = resp["body"]
        reservation["reservedTime"] = webdata.strToDatetime(reservation["reservedTime"])
        #if not current_app.testing:
        #    calendar.deleteEvent(session["credentials"], member, reservation)
        error = False

    return render_template("cancel.html", error=error, member=member)

@web.route("/admin", methods=["GET", "POST"])
def admin():

    member = security.verifySession(session)
    if member is None:
        return redirect(url_for(".welcome"))

    #View history
    resp = rest.get("allMembers") 
    if resp is None or resp["error"] is not None:
        members = None
    else:
        members = resp["body"]
    
    users = members
    
    #Report car 
    resp = rest.get("car")      
    if resp is None or resp["error"] is not None:
        cars = None
    else:
        cars = resp["body"]

    #User search 
    params = {}
    if request.method == "POST": 
        keyTypes = {
            "username": str,
            "email": str,
        }
        params = webdata.parseInput(request.form, keyTypes)

        resp = rest.get("searchMembers", params=params)
        if resp is None or resp["error"] is not None:
            users = None
        else:
            users = resp["body"]

    return(render_template("admin.html", staff=member,members=members,users=users,cars=cars))


@web.route("/modify",methods=["GET", "POST"])
def modify():
    '''Modify Member URI.

    Parameters for GET method
    -------------------------
    id : str
        Member's id.

    Parameters for POST method
    --------------------------
    id : str (optional)
        Member's id.
    username : str
        Member's username.
    password : str
        Member's password.
    firstName : str
        Member's first name.
    lastName : str
        Member's last name.
    email : str
        Member's email address.
    userType : str
        Member's type.
    '''
    error = None
    if request.method == "GET":
        keyTypes = {
            "id": int,
        }   
        params = webdata.parseInput(request.args, keyTypes)

        if not params: #add user
            user = None

        else: #modify user
            resp = rest.get("member", params=params)        
            user = resp['body']
            for i in user:
              user = i

    if request.method == "POST":

        keyTypes = {
            "id": int,
            "username": str,
            "password": str,
            "firstName": str,
            "lastName": str,
            "email": str,
            "userType": str,
        }
        params = webdata.parseInput(request.form, keyTypes)
        
        if(params['id'] != 0): #modify user

            resp = rest.post("modifyUser", data=params)
            if resp is None or resp["error"] is not None:
                error = True
            else:
                user = getUser(resp['body'])
                error = False         
            
        else: #add new user
            keyTypes = {
                "username": str,
                "password": str,
                "firstName": str,
                "lastName": str,
                "email": str,
                "userType": str,
            }
            params = webdata.parseInput(request.form, keyTypes)
            resp = rest.post("member", data=params)
            if resp is None or resp["error"] is not None:
                error = True
            else:
                error = False
            
            user = None

    return(render_template("modify.html",error=error,user=user))

def getUser(id):
    '''Get a user by given id.

    Parameters
    ----------
    id : int
        Member id.

    Returns
    -------
    dict
        Member dict collected via RESTful API.
    '''

    resp = rest.get("member", params={"id": id})
    if resp is None or resp["error"] is not None and len(resp["body"]) != 1:
        return None

    return resp["body"][0]

@web.route("/report",methods=["GET", "POST"])
def report():
    '''Report URL.

    Parameters
    ----------
    id : int
        Car id.

    Returns
    -------
    dict
        Car dict collected via RESTful API.
    '''
    error = None
    if request.method == "GET":
        keyTypes = {
            "id": int
        }
        params = webdata.parseInput(request.args, keyTypes)
        car = getCar(params["id"])
        if car is None:
            error = True

    if request.method == "POST":

        keyTypes = {
            "id" : int,
            "email": str,
            "content": str,
        }
        params = webdata.parseInput(request.form, keyTypes)
        car = getCar(params["id"])
        if car is None:
            error = True
        else:
            resp = rest.get("reportCar", params=params)
            if resp is None or resp["error"] is not None:
                error = True
            else:
                error = False
        
    return(render_template("report.html",car=car,error=error))

@web.route("/engineer", methods=["GET", "POST"])
def engineer():
    '''Engineer URI.

    Parameters for GET method
    -------------------------
    make : str 
        Car's brand.
    bodyType : str 
        Car's body type.
    colour : str 
        Car's colour.
    seats : int (optional)
        Number of seats.
    location : str 
        Car's current location.
    costPerHour : float 
        Cost per hour.
    reported : bool (True)
        Reported cars
    '''

    member = security.verifySession(session)
    if member is None:
        return redirect(url_for(".welcome"))

    keyTypes = {
        "make": str,
        "bodyType": str,
        "colour": str,
        "seats": int,
        "location": str,
        "costPerHour": float
    }
    params = webdata.parseInput(request.form, keyTypes)

    params["reported"] = True
    resp = rest.get("car", params=params)

    if resp is None or resp["error"] is not None:
        cars = None
    else:
        cars = resp["body"]

    return render_template("engineer.html", member=member, params=params, cars=cars)

@web.route("/emaps", methods=["GET", "POST"])
def emaps():
    '''Maps URI.
    '''

    member = security.verifySession(session)
    if member is None:
        return redirect(url_for(".welcome"))

    params = {}
    if request.method == "POST":
        keyTypes = {
            "make": str,
            "bodyType": str,
            "colour": str,
            "seats": int,
            "location": str,
            "costPerHour": float
        }
        params = webdata.parseInput(request.form, keyTypes)

    params["reported"] = True
    resp = rest.get("car", params=params)
    if resp is None or resp["error"] is not None:
        cars = None
    else:
        cars = resp["body"]

    if cars is None:
        centre = {
            "latitude": -37.8744,
            "longitude": 145.1668
        }
    else:
        centre = {
            "latitude": 0.0,
            "longitude": 0.0
        }

        for car in cars:
            centre["latitude"] += car["latitude"]
            centre["longitude"] += car["longitude"]

        centre["latitude"] /= len(cars)
        centre["longitude"] /= len(cars)

    return render_template("emaps.html", member=member, params=params, cars=cars, centre=centre)

@web.route("/manager", methods=["GET", "POST"])
def manager():

    member = security.verifySession(session)
    if member is None:
        return redirect(url_for(".welcome"))

    #All members
    resp = rest.get("allMembers") 
    if resp is None or resp["error"] is not None:
        members = None
    else:
        members = resp["body"]
    
    #All cars
    resp = rest.get("car")      
    if resp is None or resp["error"] is not None:
        cars = None
    else:
        cars = resp["body"]

    #All reservations
    resp = rest.get("reservation")
    if resp is None or resp["error"] is not None:
        reservations = None
    else:
        reservations = resp["body"]

    if reservations is not None:
        for reservation in reservations:
            params = {"id": reservation["carId"]}
            resp = rest.get("car", params=params)
            if resp is None or resp["error"] is not None:
                reservation["car"] = None
            else:
                reservation["car"] = resp["body"][0]

            reservation["reservedTime"] = webdata.strToDatetime(reservation["reservedTime"])
            reservation["reservedTime"] = webdata.convertUtcToLocal(reservation["reservedTime"])
            reservation["reservedTimeStr"] = webdata.datetimeToStr(reservation["reservedTime"])
            reservation["statusStr"] = webdata.statusToStr(reservation["status"])
    
    return(render_template("manager.html", staff=member,members=members,cars=cars,reservations=reservations))



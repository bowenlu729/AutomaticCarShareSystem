import os, sys, pickle, unittest
from datetime import datetime
from werkzeug.security import check_password_hash

sys.path.insert(0, os.path.abspath("../master"))
sys.path.insert(0, os.path.abspath("../agent"))

import master
import agent


class TestPIoTCSS(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        os.environ["FLASK_UNIT_TEST"] = "1"
        from app import app
        cls.app = app

        # Default member (id = 1)
        cls.defaultMember = {
            "username": "morrison",
            "password": "a",
            "firstName": "Scott",
            "lastName": "Morrison",
            "email": "scott.morrison@rmit.edu.au"
        }

        # Default car (id = 1)
        cls.defaultCar = {
            "make": "Holden",
            "bodyType": "Wagon",
            "colour": "Silver",
            "seats": 4,
            "costPerHour": 7.50,
        }

    def setUp(self):
        self.client = self.app.test_client()


    def assertRestResp(self, resp, expected_status_code=200):
        self.assertEqual(resp.status_code, expected_status_code)
        data = resp.get_json()
        self.assertTrue(data["error"] is None, data["error"])
        return data["body"]


    def assertMember(self, member, pattern=None):
        if pattern is None:
            pattern = self.defaultMember
        for k, v in pattern.items():
            if k == "password":
                self.assertTrue(check_password_hash(member[k], v))
            else:
                self.assertEqual(member[k], v)


    def assertCar(self, car, pattern=None):
        if pattern is None:
            pattern = self.defaultCar
        for k, v in pattern.items():
            self.assertEqual(car[k], v)


    def test_A_api_01_routeMember_POST(self):
        params = self.defaultMember
        resp = self.client.post("/api/member", data=params)
        body = self.assertRestResp(resp)
        self.assertEqual(body["id"], 1)
        self.assertMember(body)


    def test_A_api_02_routeMember_GET(self):
        params = {
            "id": 1
        }
        resp = self.client.get("/api/member", query_string=params)
        body = self.assertRestResp(resp)
        self.assertEqual(len(body), 1)
        self.assertMember(body[0])


    def test_A_api_03_routeCar_GET(self):
        params = {
            "id": 1
        }
        resp = self.client.get("/api/car", query_string=params)
        body = self.assertRestResp(resp)
        self.assertEqual(len(body), 1)
        self.assertCar(body[0])

        params = self.defaultCar
        params.update({
            "location": "Glen Waverley",
            "available": True
        })
        resp = self.client.get("/api/car", query_string=params)
        body = self.assertRestResp(resp)
        self.assertEqual(len(body), 1)
        self.assertCar(body[0])

        params = {
            "make": "Holden"
        }
        resp = self.client.get("/api/car", query_string=params)
        body = self.assertRestResp(resp)
        self.assertEqual(len(body), 3)
        self.assertCar(body[0])
        self.assertEqual(body[1]["id"], 5)
        self.assertEqual(body[2]["id"], 10)


    def test_A_api_04_routeReservation_POST(self):
        params = {
            "memberId": 1,
            "carId": 1,
            "reservedTime": datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
            "reservedHours": 24
        }
        resp = self.client.post("/api/reservation", data=params)
        body = self.assertRestResp(resp)
        self.assertEqual(body["id"], 1)
        self.assertEqual(body["memberId"], 1)
        self.assertEqual(body["carId"], 1)
        self.assertEqual(body["status"], 0)


    def test_A_api_05_routeReservation_PUT(self):
        params = {
            "id": 1,
            "status": -1
        }
        resp = self.client.put("/api/reservation", data=params)
        body = self.assertRestResp(resp)
        self.assertEqual(body["id"], 1)
        self.assertEqual(body["status"], -1)


    def test_A_api_06_routeReservation_GET(self):
        params = {
            "id": 1
        }
        resp = self.client.get("/api/reservation", query_string=params)
        body = self.assertRestResp(resp)
        self.assertEqual(len(body), 1)
        self.assertEqual(body[0]["id"], 1)
        self.assertEqual(body[0]["memberId"], 1)
        self.assertEqual(body[0]["carId"], 1)

        params = {
            "memberId": 1,
            "carId": 1,
            "status": -1
        }
        resp = self.client.get("/api/reservation", query_string=params)
        body = self.assertRestResp(resp)
        self.assertEqual(len(body), 1)
        self.assertEqual(body[0]["id"], 1)


    def assertWebResp(self, resp, expected_status_code=200):
        self.assertEqual(resp.status_code, expected_status_code)
        body = resp.data.decode("utf-8")
        return body


    def test_A_web_01_welcome_GET(self):
        resp = self.client.get("/welcome")
        body = self.assertWebResp(resp)
        self.assertTrue("<h1>[PIoT] Car Share System - Welcome</h1>" in body)


    def test_A_web_02_welcome_POST(self):
        params = {
            "username": self.defaultMember["username"],
            "password": self.defaultMember["password"]
        }
        resp = self.client.post("/welcome", data=params)
        body = self.assertWebResp(resp)
        self.assertTrue("<strong>Success!</strong>" in body)
        with self.client.session_transaction() as session:
            self.assertTrue("m" in session)


    def test_A_web_03_register_GET(self):
        resp = self.client.get("/register")
        body = self.assertWebResp(resp)
        self.assertTrue("<h1>[PIoT] Car Share System - Register</h1>" in body)


    def test_A_web_04_register_POST(self):
        params = {
            "username": "andrews",
            "password": "a",
            "firstName": "Daniel",
            "lastName": "Andrews",
            "email": "daniel.andrews@rmit.edu.au"
        }
        resp = self.client.post("/register", data=params)
        body = self.assertWebResp(resp)
        self.assertTrue("<strong>Success!</strong>" in body)


    def test_A_web_05_logout_GET(self):
        with self.client.session_transaction() as session:
            session["m"] = 1
        resp = self.client.get("/logout")
        body = self.assertWebResp(resp)
        self.assertTrue("<strong>Success!</strong>" in body)
        with self.client.session_transaction() as session:
            self.assertFalse("m" in session)


    def test_A_web_06_cars_GET(self):
        with self.client.session_transaction() as session:
            session["m"] = 1
        resp = self.client.get("/cars")
        body = self.assertWebResp(resp)
        self.assertTrue("<h1>[PIoT] Car Share System - Cars</h1>" in body)


    def test_A_web_07_cars_POST(self):
        with self.client.session_transaction() as session:
            session["m"] = 1
        params = self.defaultCar
        resp = self.client.post("/cars", data=params)
        body = self.assertWebResp(resp)
        self.assertTrue("<h1>[PIoT] Car Share System - Cars</h1>" in body)
        self.assertTrue("<td>C0001</td>" in body)


    def test_A_web_08_gmaps_GET(self):
        with self.client.session_transaction() as session:
            session["m"] = 1
        resp = self.client.get("/gmaps")
        body = self.assertWebResp(resp)
        self.assertTrue("<h1>[PIoT] Car Share System - Maps</h1>" in body)


    def test_A_web_09_gmaps_POST(self):
        with self.client.session_transaction() as session:
            session["m"] = 1
        params = self.defaultCar
        resp = self.client.post("/gmaps", data=params)
        body = self.assertWebResp(resp)
        self.assertTrue("<h1>[PIoT] Car Share System - Maps</h1>" in body)
        self.assertTrue('<li>Car No: <a href="/reserve?id=1">C0001</a></li>' in body)


    def test_A_web_10_reserve_GET(self):
        with self.client.session_transaction() as session:
            session["m"] = 1
        params = {
            "id": 1
        }
        resp = self.client.get("/reserve", query_string=params)
        body = self.assertWebResp(resp)
        self.assertTrue("<h1>[PIoT] Car Share System - Reserve</h1>" in body)


    def test_A_web_11_reserve_POST(self):
        with self.client.session_transaction() as session:
            session["m"] = 1
        params = {
            "carId": 1,
            "reservedTime": datetime.utcnow().isoformat(),
            "reservedHours": 24
        }
        resp = self.client.post("/reserve", data=params)
        body = self.assertWebResp(resp)
        self.assertTrue("<strong>Success!</strong>" in body)


    def test_A_web_12_history_GET(self):
        with self.client.session_transaction() as session:
            session["m"] = 1
        resp = self.client.get("/history")
        body = self.assertWebResp(resp)
        self.assertTrue("<h1>[PIoT] Car Share System - History</h1>" in body)
        self.assertTrue("<td>R000002</td>" in body)


    def test_A_web_13_cancel_GET(self):
        with self.client.session_transaction() as session:
            session["m"] = 1
        params = {
            "id": 2
        }
        resp = self.client.get("/cancel", query_string=params)
        body = self.assertWebResp(resp)
        self.assertTrue("<h1>[PIoT] Car Share System - Cancel</h1>" in body)
        self.assertTrue("<strong>Success!</strong>" in body)


    def test_B_agent_01_getGPSLocation(self):
        gps = agent.getGPSLocation()
        self.assertTrue("location" in gps)
        self.assertTrue("latitude" in gps)
        self.assertTrue("longitude" in gps)


    def test_B_agent_02_execCommand_unlockByPassword(self):
        params = {
            "memberId": 1,
            "carId": agent.config["agentId"],
            "reservedTime": datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
            "reservedHours": 24
        }
        resp = self.client.post("/api/reservation", data=params)
        reservation = self.assertRestResp(resp)

        auth = {
            "username": self.defaultMember["username"],
            "password": self.defaultMember["password"]
        }
        resp = agent.execCommand("U", auth, None)
        self.assertTrue(resp["error"] is None)
        self.assertMember(resp["body"])


    def test_B_agent_03_execCommand_returnByPassword(self):
        auth = {
            "username": self.defaultMember["username"],
            "password": self.defaultMember["password"]
        }
        gps = agent.getGPSLocation()
        resp = agent.execCommand("R", auth, gps)
        self.assertTrue(resp["error"] is None)
        self.assertMember(resp["body"])


    def test_C_agent_01_execCommand_unlockByFacreg(self):
        params = {
            "memberId": 1,
            "carId": agent.config["agentId"],
            "reservedTime": datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
            "reservedHours": 24
        }
        resp = self.client.post("/api/reservation", data=params)
        reservation = self.assertRestResp(resp)

        auth = {
            "encodings": agent.encodeImage(self.defaultMember["username"] + ".jpg")
        }
        resp = agent.execCommand("U", auth, None)
        self.assertTrue(resp["error"] is None)
        self.assertMember(resp["body"])


    def test_C_agent_02_execCommand_returnByFacreg(self):
        auth = {
            "encodings": agent.encodeImage(self.defaultMember["username"] + ".jpg")
        }
        gps = agent.getGPSLocation()
        resp = agent.execCommand("R", auth, gps)
        self.assertTrue(resp["error"] is None)
        self.assertMember(resp["body"])


if __name__ == '__main__':
    # Clear unit test database
    os.system("mysql --host=35.189.41.186 --user=root --password=dlp0IKqrLJxODvno < utests.sql")

    unittest.main()

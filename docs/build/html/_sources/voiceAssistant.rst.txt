voiceAssistant
================

Voice search methods that add the voice/search feature to search the cars in MP. 
This is for the admin who is looking to find a specific car.


Required components
---------------------
* google assistant: Convert speech into text(import speech_recognition as sr)                                                              
* client_secret.json: save the certification for API  

getCarMakeToSearch():                                                                                                                      
-----------------------

    Voice search by saying car make

    >>> Say the car make to search for.
    >>> Looking for car with make 'make'...
    >>> Results found / No results found

* To test searching without the microphone uncomment this line of code
* for i, microphone_name in enumerate(sr.Microphone.list_microphone_names()): 
* Set the device ID of the mic that we specifically want to use to avoid ambiguity
* r = sr.Recognizer(): obtain audio from the microphone
* subprocess.run("clear"): clear console of errors
* r.adjust_for_ambient_noise(source): energy threshold based on the surrounding noise level
* audio = r.listen(source, timeout = 1.5): listen voice
* carMake = r.recognize_google(audio): Replace recognition text

searchcarMake(carMake):
------------------------
Connect to Mysql DB to find car

    Parameters
    ----------
    carMake : str
        Make of the car

    Returns
    ----------
     dict {
        body : dict
            A car dict.
    }

* connection = pymysql.connect(HOST, USER, PASSWORD, DATABASE): Connect to database
* with connection.cursor() as cursor: 
* cursor.execute("select * from Cars where make = %s", (carMake,)):Execute query statement
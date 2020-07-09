import speech_recognition as sr
import pymysql, subprocess

HOST = "35.189.41.186"
USER = "mwneko"
PASSWORD = "aixin521"
DATABASE = "piot2db"

MIC_NAME = "HD Pro Webcam C920: USB Audio (hw:1,0)"

def main():
    #firstName = getFirstNameToSearch()
    carMake = getCarMakeToSearch()

    if(carMake is None):
        print("Failed to get car make.")
        return

    print()
    print("Looking for car with make '{}'...".format(carMake))
    print()

    rows = searchCar(carMake)
    if(rows):
        print("Found:", rows)
    else:
        print("No results found.")

#def getFirstNameToSearch():
def getCarMakeToSearch():
    # To test searching without the microphone uncomment this line of code
    # return input("Enter the first name to search for: ")

    # Set the device ID of the mic that we specifically want to use to avoid ambiguity
    for i, microphone_name in enumerate(sr.Microphone.list_microphone_names()):
        if(microphone_name == MIC_NAME):
            device_id = i
            break

    # obtain audio from the microphone
    r = sr.Recognizer()
    with sr.Microphone(device_index = device_id) as source:
        # clear console of errors
        subprocess.run("clear")

        # wait for a second to let the recognizer adjust the
        # energy threshold based on the surrounding noise level
        r.adjust_for_ambient_noise(source)

        print("Say the car make to search for.")
        try:
            audio = r.listen(source, timeout = 1.5)
        except sr.WaitTimeoutError:
            return None

    # recognize speech using Google Speech Recognition
    carMake = None
    try:
        # for testing purposes, we're just using the default API key
        # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
        # instead of `r.recognize_google(audio)`
        carMake = r.recognize_google(audio)
    except(sr.UnknownValueError, sr.RequestError):
        pass
    finally:
        return carMake

def searchCar(carMake):
    connection = pymysql.connect(HOST, USER, PASSWORD, DATABASE)

    with connection.cursor() as cursor:
        cursor.execute("select * from Cars where make = %s", (carMake,))
        rows = cursor.fetchall()

    connection.close()

    return rows

# Execute program.
if __name__ == "__main__":
    main()


import speech_recognition as sr
# Initialize recognizer class (for recognizing speech)
recognizer = sr.Recognizer()
def listen_for_command():


    # Use the microphone to capture the audio
    with sr.Microphone() as source:
        while True:
            print("Listening for the command 'test'...")
            # Adjust the recognizer sensitivity to ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=1)        
            # Capture the audio from the user
            audio = recognizer.listen(source)

            try:
                # Recognize speech using Google's speech recognition
                text = recognizer.recognize_google(audio).lower()
                if "test" in text:
                    listen_for_address()
                elif "exit" in text:
                    break
                
            except sr.UnknownValueError:
                print("Sorry, I could not understand the audio.")
            except sr.RequestError:
                print("Could not request results from Google Speech Recognition service; check your internet connection.")

def listen_for_address():
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Please say your address:")
        
        # Listen for the next statement
        audio = recognizer.listen(source)
        
        try:
            # Convert speech to text
            address = recognizer.recognize_google(audio)
            print(f"Address captured: {address}")
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand the address.")
        except sr.RequestError:
            print("Request failed; please check your connection.")

listen_for_command()
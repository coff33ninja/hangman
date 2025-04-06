# Ensure you install the library: pip install SpeechRecognition
import speech_recognition as sr  # Ensure this library is installed

class VoiceInput:
    def __init__(self, timeout=5):  # Make timeout configurable
        self.recognizer = sr.Recognizer()
        self.timeout = timeout  # Set the timeout

    def get_voice_input(self):
        """
        Capture voice input and return the recognized text.
        """
        with sr.Microphone() as source:
            print("Listening for your guess...")
            try:
                audio = self.recognizer.listen(source, timeout=self.timeout)
                return self.recognizer.recognize_google(audio).upper()
            except sr.UnknownValueError:
                print("Sorry, I didn't catch that.")
            except sr.RequestError as e:
                print(f"Voice recognition error: {e}")
        return None

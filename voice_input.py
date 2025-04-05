# Ensure you install the library: pip install SpeechRecognition
import speech_recognition as sr  # Ensure this library is installed

class VoiceInput:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def get_voice_input(self):
        """
        Capture voice input and return the recognized text.
        """
        with sr.Microphone() as source:
            print("Listening for your guess...")
            try:
                audio = self.recognizer.listen(source, timeout=5)
                return self.recognizer.recognize_google(audio).upper()
            except sr.UnknownValueError:
                print("Sorry, I didn't catch that.")
            except sr.RequestError as e:
                print(f"Voice recognition error: {e}")
        return None


import speech_recognition as sr
import pyaudiowpatch as pyaudio

print("IGRIS speech test started!")

recognizer = sr.Recognizer()
audio_system = pyaudio.PyAudio()

try:
    microphone = audio_system.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        input=True,
        input_device_index=2,
        frames_per_buffer=1024
    )

    print("Speak a short sentence now...")

    frames = []
    for _ in range(50):
        frames.append(microphone.read(
            1024, exception_on_overflow=False
        ))

    microphone.stop_stream()
    microphone.close()

    audio_data = b"".join(frames)

    audio = sr.AudioData(audio_data, 16000, 2)

    print("Converting speech to text...")

    text = recognizer.recognize_google(audio)
    print("IGRIS heard:", text)

except sr.UnknownValueError:
    print("IGRIS could not understand the speech. Try again.")

except sr.RequestError as error:
    print("Speech service error. Check your internet connection:", error)

except Exception as error:
    print("Error:", error)

finally:
    audio_system.terminate()

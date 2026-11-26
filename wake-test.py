
import speech_recognition as sr
import pyaudiowpatch as pyaudio

recognizer = sr.Recognizer()
audio_system = pyaudio.PyAudio()

try:
    print("===== MJ WAKE WORD TEST =====")
    print("Say MJ clearly when recording starts.")

    stream = audio_system.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        input=True,
        input_device_index=2,
        frames_per_buffer=1024
    )

    frames = []

    print("Recording for 4 seconds...")

    for _ in range(63):
        frames.append(
            stream.read(1024, exception_on_overflow=False)
        )

    stream.stop_stream()
    stream.close()

    audio = sr.AudioData(
        b"".join(frames),
        16000,
        2
    )

    print("Recognizing speech...")

    try:
        result = recognizer.recognize_google(
            audio,
            language="en-IN"
        )

        print("MJ heard:", result)

        words = result.lower().strip().split()

        if "mj" in words:
            print("SUCCESS! MJ wake word detected!")
        elif "emjay" in words or "em-jay" in words:
            print("SUCCESS! MJ wake word detected!")
        else:
            print("Wake word not detected. Try again.")

    except sr.UnknownValueError:
        print("Speech not understood. Please try again.")

    except sr.RequestError as error:
        print("Google recognition error:", error)

except Exception as error:
    print("Error type:", type(error).__name__)
    print("Error details:", repr(error))

finally:
    audio_system.terminate()

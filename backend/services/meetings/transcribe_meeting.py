from faster_whisper import WhisperModel
import os

AUDIO_FOLDER = "gtts_output"
OUTPUT_FILE = "transcripts.txt"

model = WhisperModel("base", device="cpu", compute_type="float16")

def transcribe(path):
    segments, info = model.transcribe(path)
    return " ".join(segment.text for segment in segments)

def main():
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for filename in os.listdir(AUDIO_FOLDER):
            if filename.endswith((".mp3", ".wav", ".m4a")):
                path = os.path.join(AUDIO_FOLDER, filename)
                print("Transcribing:", filename)
                text = transcribe(path)
                out.write(f"\n--- {filename} ---\n{text}\n")

    print("Done!")

if __name__ == "__main__":
    main()

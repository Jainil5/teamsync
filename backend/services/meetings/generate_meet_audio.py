from gtts import gTTS
import os

voice_map = {
    "Jay": "en",       
    "Riya": "en-in",   
    "Adit": "en-uk"    
}

script_data = [
    {"speaker": "Jay", "text": "Good morning, team. Let's do a quick check-in on the Q4 Ascent project."},
    {"speaker": "Riya", "text": "Morning. The pipeline is looking strong, Jay."},
    {"speaker": "Jay", "text": "Excellent. Five is strong. Adit, how do those five look to you?"},
    {"speaker": "Adit", "text": "One major deal is signed—85,000 dollars in recurring revenue secured."},
    {"speaker": "Riya", "text": "If it's the timeline, I can send over the revised implementation flowchart."},
    {"speaker": "Adit", "text": "That would be a huge help, Riya."},
    {"speaker": "Jay", "text": "Fantastic work, both of you."},
]
os.makedirs("gtts_output", exist_ok=True)

for i, entry in enumerate(script_data, start=1):
    speaker = entry["speaker"]
    text = entry["text"]
    lang = voice_map[speaker]

    filename = f"gtts_output/{i}_{speaker}.mp3"

    print(f"Generating: {filename}")

    tts = gTTS(text=text, lang=lang)
    tts.save(filename)

print("\nAll audio files generated in: gtts_output/")

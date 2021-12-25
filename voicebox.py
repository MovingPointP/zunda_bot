import json
import requests
import wave
from pydub import AudioSegment

def generate_wav(text, speaker=1, filepath='./audio.wav'):
    host = 'localhost'
    port = 50021
    params = (
        ('text', text),
        ('speaker', speaker),
    )
    response1 = requests.post(
        f'http://{host}:{port}/audio_query',
        params=params
    )

    headers = {'Content-Type': 'application/json', }
    response2 = requests.post(
        f'http://{host}:{port}/synthesis',
        headers=headers,
        params=params,
        data=json.dumps(response1.json())
    )
    
    with wave.open(filepath, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes(response2.content)
    
    sound = AudioSegment.from_wav(filepath)
    sound = sound[100:]
    sound.export(filepath, format='wav')

if __name__ == '__main__':
    text = 'おはようなのだ'
    generate_wav(text)

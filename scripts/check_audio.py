"""Independent local speech-recognition check; no audio is sent to a remote API."""
import json
from pathlib import Path
from faster_whisper import WhisperModel

ROOT=Path(__file__).resolve().parents[1]
demo=ROOT/'artifacts/demo'
model=WhisperModel('tiny.en',device='cpu',compute_type='int8')
segments,info=model.transcribe(str(demo/'demo.mp4'),beam_size=5,language='en')
rows=[{'start':s.start,'end':s.end,'text':s.text} for s in segments]
text=' '.join(s['text'].strip() for s in rows)
(demo/'asr-transcript.txt').write_text(text+'\n',encoding='utf-8')
(demo/'audio-check.json').write_text(json.dumps({'method':'Local faster-whisper tiny.en CPU int8','language':info.language,
    'segments':rows,'note':'ASR corroborates intelligibility, but is not a human assessment of voice naturalness.'},indent=2)+'\n',encoding='utf-8')
print(text)

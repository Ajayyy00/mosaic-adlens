"""Generate disclosed neural male narration and time-aligned captions."""
import asyncio
import json
import math
import subprocess
import textwrap
import wave
from pathlib import Path
import edge_tts
import imageio_ffmpeg

ROOT=Path(__file__).resolve().parents[1]
DEMO=ROOT/'artifacts/demo'
SCENES=[
 ('overview','A clear answer to wasted spend',
  'Eight hundred ads. Four platforms. Which campaigns had enough money and time, but still failed to earn back their spend? Adlens turns the official Mosaic dataset into a traceable answer.'),
 ('explorer','800 official records. No replacement data.',
  'The complete source is preserved with a download timestamp and checksum. Every ad retains its platform, audience, creative theme, spend, revenue, and running days. Nothing is sampled out.'),
 ('methodology','Three strict checks. One contribution.',
  'An ad qualifies only when return on ad spend is below one, spend exceeds five thousand rupees, and it has run for more than fourteen days. All three must pass. Its full spend counts once.'),
 ('overview','₹14,75,731.79 · 13 qualifying ads',
  'The result: fourteen lakh, seventy-five thousand, seven hundred thirty-one rupees and seventy-nine paise. Thirteen ads qualify. Instagram contributes the most, and the four platform totals reconcile exactly to the answer.'),
 ('filtered','Search. Filter. Inspect.',
  'The explorer makes that result practical. Filter by platform, audience, or creative theme. Search for an individual ad, sort its performance, and open the evidence behind its classification.'),
 ('detail','AD-0029 / Follow the evidence',
  'Take this Instagram ad. It spent roughly one lakh thirty-nine thousand rupees and earned about ninety-five thousand. Its reported return is zero point six eight, over sixty-five days. All three checks pass, so its full spend contributes once. The exact amounts and original source index remain visible.'),
 ('insights','Find patterns without overstating them',
  'Creative rankings use total revenue divided by total spend. Doctor Trust, Lifestyle, and Product Demo lead. These synthetic returns are unusually high, so relative underperformance does not automatically mean a whole audience is losing money.'),
 ('downloads','Reproduce the result',
  'Python Decimal and a separate JavaScript integer-cents calculation agree on every flagged ad and platform subtotal. Download the records and reconciliation to reproduce the result. Adlens makes every rupee explainable.'),
 ('overview','1475731.79 INR / Fully reconciled',
  'Thirteen ads. Fourteen lakh, seventy-five thousand, seven hundred thirty-one rupees and seventy-nine paise. Every rupee explained.'),
]

def stamp(seconds):
    ms=round(seconds*1000)
    return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'

async def main():
    DEMO.mkdir(parents=True,exist_ok=True)
    ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
    timeline=[]; cues=[]; cursor=0.0
    for index,(shot,title,script) in enumerate(SCENES):
        audio=DEMO/f'narration-{index}.mp3'
        boundaries=[]
        with audio.open('wb') as output:
            async for chunk in edge_tts.Communicate(script,'en-US-AndrewNeural',rate='+8%',boundary='WordBoundary').stream():
                if chunk['type']=='audio': output.write(chunk['data'])
                elif chunk['type']=='WordBoundary': boundaries.append(chunk)
        wav=DEMO/f'narration-{index}.wav'
        subprocess.run([ffmpeg,'-y','-loglevel','error','-i',str(audio),'-ar','48000','-ac','1',str(wav)],check=True)
        with wave.open(str(wav),'rb') as reader:
            duration=reader.getnframes()/reader.getframerate()
        # A small gap between chapters lets the viewer read the changing screen.
        scene_duration=math.ceil((duration+0.35)*30)/30
        timeline.append(dict(index=index,shot=shot,title=title,text=script,start=cursor,duration=scene_duration,
                             audio_duration=duration,audio=audio.name))
        group=[]
        for word in boundaries:
            group.append(word)
            if len(group)>=7 or word['text'].endswith(('.','?','!')):
                cues.append(dict(start=cursor+group[0]['offset']/1e7,
                                 end=cursor+(group[-1]['offset']+group[-1]['duration'])/1e7,
                                 text=' '.join(x['text'] for x in group)))
                group=[]
        if group:
            cues.append(dict(start=cursor+group[0]['offset']/1e7,
                             end=cursor+(group[-1]['offset']+group[-1]['duration'])/1e7,
                             text=' '.join(x['text'] for x in group)))
        cursor+=scene_duration
    transcript='\n\n'.join(s[2] for s in SCENES)+'\n'
    (DEMO/'transcript.txt').write_text(transcript,encoding='utf-8')
    (ROOT/'artifacts/submission/demo-script.md').write_text(transcript,encoding='utf-8')
    (DEMO/'timeline.json').write_text(json.dumps({'voice':'en-US-AndrewNeural','disclosure':'AI-generated neural male narration',
        'duration':cursor,'scenes':timeline,'cues':cues},indent=2),encoding='utf-8')
    (DEMO/'demo.srt').write_text('\n\n'.join(f"{i+1}\n{stamp(c['start'])} --> {stamp(c['end'])}\n"+'\n'.join(textwrap.wrap(c['text'],width=58)) for i,c in enumerate(cues))+'\n',encoding='utf-8')
    print(json.dumps({'seconds':cursor,'words':len(transcript.split()),'cues':len(cues),'voice':'en-US-AndrewNeural'}))
if __name__=='__main__':asyncio.run(main())

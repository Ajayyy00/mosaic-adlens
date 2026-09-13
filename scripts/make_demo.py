"""Compose an HD presentation using authentic browser captures, narration and burned captions.

Run scripts/narrate.py first. Capture public app views through the browser tools into
artifacts/demo/frames/{overview,explorer,methodology,filtered,detail,insights,downloads}.png.
Screenshots are real browser outputs; this script only frames/resizes them on video slides.
"""
import json
import re
import subprocess
import textwrap
import wave
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
import imageio_ffmpeg

ROOT=Path(__file__).resolve().parents[1]
DEMO=ROOT/'artifacts/demo'
FONT=Path('C:/Windows/Fonts')
W,H=1920,1080

def font(size,bold=False):
    names=['arialbd.ttf','DejaVuSans-Bold.ttf'] if bold else ['arial.ttf','DejaVuSans.ttf']
    for base in (FONT,Path('/usr/share/fonts/truetype/dejavu')):
        for name in names:
            if (base/name).exists():return ImageFont.truetype(str(base/name),size)
    raise RuntimeError('Install Arial or DejaVu Sans for rendering')

def draw_scene(scene):
    picture=Image.new('RGB',(W,H),'#101c2e'); draw=ImageDraw.Draw(picture)
    draw.rounded_rectangle((52,38,98,84),radius=10,fill='#c1f580')
    draw.text((64,36),'a',font=font(43,True),fill='#142238')
    draw.text((111,45),'adlens.',font=font(30,True),fill='white')
    draw.text((W-535,48),'MOSAIC / CONTENT & CREATIVE',font=font(19),fill='#a5b2c6')
    draw.text((54,121),scene['title'],font=font(42,True),fill='white')
    draw.text((56,181),f"0{scene['index']+1}  /  AD PERFORMANCE INTELLIGENCE",font=font(18),fill='#bfd89e')
    shot=Image.open(DEMO/'frames'/f"{scene['shot']}.png").convert('RGB')
    box=(54,232,1455,922)
    fitted=ImageOps.contain(shot,(box[2]-box[0]-8,box[3]-box[1]-8),Image.Resampling.LANCZOS)
    draw.rounded_rectangle(box,radius=10,fill='#f4f6f9',outline='#63758c',width=2)
    picture.paste(fitted,(box[0]+(box[2]-box[0]-fitted.width)//2,box[1]+(box[3]-box[1]-fitted.height)//2))
    draw=ImageDraw.Draw(picture)
    x=1490
    callouts={
      'overview':[('1475731.79','INR / EXACT ANSWER'),('13 / 800','ADS QUALIFY'),('0.00','RECONCILIATION GAP')],
      'explorer':[('800 records','COMPLETE SOURCE'),('23 fields','PER AD'),('4 platforms','OFFICIAL DATASET')],
      'methodology':[('ROAS < 1.0','BELOW BREAK-EVEN'),('Spend > 5000','RUPEES'),('Days > 14','ENOUGH TIME')],
      'filtered':[('Search by ID','FIND A RECORD'),('Combine filters','NARROW THE VIEW'),('Open evidence','UNDERSTAND THE WHY')],
      'detail':[('139192.58','INR / SPEND'),('95216.60','INR / REVENUE'),('139192.58','INR / CONTRIBUTION')],
      'insights':[('Doctor Trust','TOP CREATIVE THEME'),('Weighted ROAS','REVENUE / SPEND'),('Test, then scale','NO CAUSAL CLAIM')],
      'downloads':[('Decimal','PYTHON AUDIT'),('BigInt','INDEPENDENT CHECK'),('JSON + CSV','REPRODUCIBLE EVIDENCE')]}
    visible_callouts=callouts[scene['shot']]
    if scene['index']==3:
        visible_callouts=[('576898.53','INSTAGRAM / INR'),('429321.93','GOOGLE / INR'),('325750.71','YOUTUBE / INR'),('143760.62','META / INR')]
    for i,(value,label) in enumerate(visible_callouts):
        y=287+i*(145 if len(visible_callouts)==4 else 188)
        draw.text((x,y),label,font=font(16),fill='#99aabe')
        draw.text((x,y+39),value,font=font(30,True),fill='#c1f580' if i==0 else 'white')
        draw.line((x,y+112,W-54,y+112),fill='#344256',width=1)
    draw.text((54,944),'AUTHENTIC APPLICATION CAPTURE  •  OFFICIAL SYNTHETIC DATA',font=font(15),fill='#889bb3')
    draw.text((W-390,944),'Neural male narration',font=font(15),fill='#889bb3')
    return picture

def main():
    timeline=json.loads((DEMO/'timeline.json').read_text())
    assert 90<=timeline['duration']<=120, f"Narration duration outside requested range: {timeline['duration']}"
    ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
    scene_paths=[]
    for scene in timeline['scenes']:
        index=scene['index']; still=DEMO/'frames'/f'slide-{index}.png'
        draw_scene(scene).save(still)
        movie=DEMO/f'scene-{index}.mp4'; scene_paths.append(movie)
        duration=scene['duration']
        command=[ffmpeg,'-y','-loglevel','error','-loop','1','-framerate','30','-i',str(still),'-i',str(DEMO/scene['audio']),
                 '-vf',f'fade=t=in:st=0:d=0.22,fade=t=out:st={duration-.22}:d=0.22,format=yuv420p',
                 '-af','apad','-t',str(duration),'-c:v','libx264','-preset','fast','-crf','20','-c:a','aac','-b:a','192k','-ar','48000',str(movie)]
        subprocess.run(command,check=True)
    concat=DEMO/'concat.txt'
    concat.write_text(''.join("file '"+p.as_posix()+"'\n" for p in scene_paths),encoding='utf-8')
    # Use a relative subtitle filename so Windows drive colons do not enter filter syntax.
    subprocess.run([ffmpeg,'-y','-loglevel','error','-f','concat','-safe','0','-i',str(concat),
        '-vf',"subtitles=demo.srt:force_style='FontName=Arial,FontSize=12,PrimaryColour=&H00FFFFFF,OutlineColour=&H002E1C10,BorderStyle=3,Outline=1,Shadow=0,MarginV=9,Alignment=2'",
        '-c:v','libx264','-preset','fast','-crf','20','-c:a','aac','-b:a','192k','-movflags','+faststart',str(DEMO/'demo.mp4')],cwd=DEMO,check=True)
    probe=subprocess.run([ffmpeg,'-i',str(DEMO/'demo.mp4'),'-f','null','-'],capture_output=True,text=True)
    output=probe.stderr
    (DEMO/'ffmpeg-validation.txt').write_text(output,encoding='utf-8')
    match=re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)',output)
    duration=int(match[1])*3600+int(match[2])*60+float(match[3])
    for i,second in enumerate((5,30,55,80,100)):
        if second<duration:
            subprocess.run([ffmpeg,'-y','-loglevel','error','-ss',str(second),'-i',str(DEMO/'demo.mp4'),'-frames:v','1',str(DEMO/'frames'/f'check-{i}.png')],check=True)
    cues=timeline['cues']
    assert all(0<=c['start']<c['end']<=duration for c in cues)
    assert all(a['end']<=b['start']+.001 for a,b in zip(cues,cues[1:]))
    normalize=lambda t:re.sub(r'[^a-z0-9]','',t.lower())
    transcript=(DEMO/'transcript.txt').read_text(encoding='utf-8')
    captions_match=normalize(transcript)==normalize(' '.join(c['text'] for c in cues))
    report=dict(duration_seconds=duration,within_90_120_seconds=90<=duration<=120,
        resolution='1920x1080',fps=30,video_codec='H.264',audio_codec='AAC',decode_passed=probe.returncode==0,
        audio_present='Audio: aac' in output,video_present='Video: h264' in output,
        voice=timeline['voice'],narration_disclosure=timeline['disclosure'],srt_cues=len(cues),
        cue_timing_valid=True,caption_text_matches_transcript=captions_match,
        source_visuals='Real public application screenshots, framed and resized on presentation slides',
        human_like_quality='Neural voice selected; subjective listening review required',
        representative_frames='frames/check-0.png through frames/check-4.png')
    (DEMO/'validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))
    assert captions_match
if __name__=='__main__':main()

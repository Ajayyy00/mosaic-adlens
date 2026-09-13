"""Package the validated static build without destructive shell cleanup."""
import json
import subprocess
import tarfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def main():
    build=ROOT/'dist'
    manifest=json.loads((ROOT/'.openai/hosting.json').read_text())
    assert (build/'index.html').is_file()
    assert manifest['static']['directory']=='dist'
    target=ROOT/'artifacts/deploy'
    target.mkdir(parents=True,exist_ok=True)
    normalized=target/'hosting.json'
    normalized.write_text(json.dumps(manifest),encoding='utf-8')
    archive=target/'site.tar.gz'
    with tarfile.open(archive,'w:gz') as tar:
        for file in sorted(build.rglob('*')):
            if file.is_file():
                tar.add(file,arcname='dist/'+file.relative_to(build).as_posix())
        tar.add(normalized,arcname='dist/.openai/hosting.json')
    with tarfile.open(archive) as tar:
        names=tar.getnames()
        assert 'dist/index.html' in names and 'dist/.openai/hosting.json' in names
        assert not any('..' in Path(n).parts for n in names)
    print(json.dumps({'archive':str(archive),'files':len(names),'bytes':archive.stat().st_size}))
if __name__=='__main__':main()

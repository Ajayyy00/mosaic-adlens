"""Export committed, reviewed source as a read-only dumb-HTTP Git endpoint.

This is generated deployment output, never tracked inside its own repository.
Only Git objects, refs, HEAD and server-info are published; no local config or hooks.
"""
import json
import shutil
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def main():
    sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    staging=ROOT/'artifacts/deploy'/('source-'+sha[:12]+'.git')
    if not staging.exists():
        subprocess.run(['git','clone','--bare','--no-hardlinks',str(ROOT),str(staging)],check=True)
    subprocess.run(['git','--git-dir='+str(staging),'update-ref','refs/heads/main',sha],check=True)
    subprocess.run(['git','--git-dir='+str(staging),'symbolic-ref','HEAD','refs/heads/main'],check=True)
    subprocess.run(['git','--git-dir='+str(staging),'update-server-info'],check=True)
    target=ROOT/'public/source.git'
    target.mkdir(parents=True,exist_ok=True)
    for name in ('objects','refs','info'):
        shutil.copytree(staging/name,target/name,dirs_exist_ok=True)
    for name in ('HEAD','packed-refs'):
        if (staging/name).exists():shutil.copy2(staging/name,target/name)
    # A later export may preserve prior reviewed objects; no source or object is destructively removed.
    print(json.dumps({'commit':sha,'target':str(target),'file_count':sum(p.is_file() for p in target.rglob('*'))}))
if __name__=='__main__':main()

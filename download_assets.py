import concurrent.futures, subprocess, zipfile
from pathlib import Path
root=Path(__file__).resolve().parent
assets=[
 ('https://huggingface.co/unsloth/MOSS-Image-SFT-GGUF/resolve/main/MOSS-Image-SFT-UD-Q4_K_XL.gguf','models/MOSS-Image-SFT-UD-Q4_K_XL.gguf'),
 ('https://huggingface.co/unsloth/Qwen3.5-9B-GGUF/resolve/main/Qwen3.5-9B-Q4_K_M.gguf','models/Qwen3.5-9B-Q4_K_M.gguf'),
 ('https://github.com/leejet/stable-diffusion.cpp/releases/download/master-1106-532d2c1/cudart-sd-bin-win-cu12-x64.zip','vendor/cudart.zip'),
 ('https://github.com/leejet/stable-diffusion.cpp/releases/download/master-1106-532d2c1/sd-master-532d2c1-bin-win-cuda12-x64.zip','vendor/sd.zip')]
def fetch(item):
 url,relative=item; target=root/relative; target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists() and target.stat().st_size: return target
 tmp=target.with_suffix(target.suffix+'.part')
 print('Downloading',relative,flush=True)
 subprocess.run(['curl.exe','-L','--fail','--retry','20','--retry-delay','5','--connect-timeout','30','-C','-','-o',str(tmp),url],check=True)
 tmp.replace(target); print('Downloaded',relative,flush=True); return target
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex: paths=list(ex.map(fetch,assets))
 out=root/'vendor/sd'; out.mkdir(exist_ok=True)
 for path in paths[2:]:
  with zipfile.ZipFile(path) as z: z.extractall(out)
 print('Runtime installed; run moss-image doctor',flush=True)

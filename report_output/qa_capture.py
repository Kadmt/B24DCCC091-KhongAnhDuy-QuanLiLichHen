"""ADB helpers for the approved report scenario; does not modify project source."""
from pathlib import Path
import subprocess, time, json, re, sys
import xml.etree.ElementTree as ET
sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parent
ADB = r'D:\Android\Sdk\platform-tools\adb.exe'
SERIAL = 'emulator-5554'
PACKAGE = 'com.example.myapplication'

def adb(*args):
    result = subprocess.run([ADB, '-s', SERIAL, *map(str,args)], capture_output=True, text=True, encoding='utf-8', errors='replace')
    with (ROOT/'evidence/adb_commands.jsonl').open('a',encoding='utf-8') as stream:
        stream.write(json.dumps({'time':time.strftime('%Y-%m-%d %H:%M:%S'), 'args':list(args),'returncode':result.returncode,'output':result.stdout.strip(),'error':result.stderr.strip()},ensure_ascii=False)+'\n')
    if result.returncode: raise RuntimeError(result.stdout+result.stderr)
    return result.stdout.strip()

def settle(): time.sleep(1.3)

def dump(label='current'):
    adb('shell','uiautomator','dump','/sdcard/report_ui.xml')
    path=ROOT/'evidence'/f'ui_{label}.xml'
    adb('pull','/sdcard/report_ui.xml',str(path))
    return list(ET.parse(path).getroot().iter('node'))

def find(key,nodes=None):
    nodes=dump() if nodes is None else nodes
    matches=[n for n in nodes if n.get('resource-id','')==key or n.get('resource-id','').endswith(':id/'+key) or n.get('text')==key]
    matches=[n for n in matches if n.get('bounds')!='[0,0][0,0]']
    if len(matches)!=1: raise RuntimeError(f'Expected one node for {key}, found {len(matches)}')
    return matches[0]

def tap_node(node):
    x1,y1,x2,y2=map(int,re.findall(r'\d+',node.get('bounds')))
    adb('shell','input','tap',(x1+x2)//2,(y1+y2)//2)
    settle()

def tap(key): tap_node(find(key))

def fill(key,value):
    tap(key)
    adb('shell','input','keyevent','123',*(['67']*45))
    adb('shell','input','text',value.replace(' ','%s'))
    settle()

def swipe(up=True):
    adb('shell','input','swipe','90', '1900' if up else '700','90','650' if up else '1900','500')
    settle()

def snap(name):
    adb('shell','screencap','-p','/sdcard/report_screen.png')
    adb('pull','/sdcard/report_screen.png',str(ROOT/'screenshots'/name))
    print('CAPTURED',name,flush=True)

def scroll_to(key,up=True):
    for _ in range(6):
        try:
            node=find(key)
            numbers=list(map(int,re.findall(r'\d+',node.get('bounds'))))
            if numbers[3]-numbers[1] > 70:
                return node
        except RuntimeError:
            pass
        swipe(up)
    raise RuntimeError('Could not scroll to '+key)

def summary(label='current'):
    nodes=dump(label)
    for node in nodes:
        if node.get('resource-id') or node.get('text'):
            print(json.dumps({k:node.get(k) for k in ('resource-id','text','bounds','class','checked')},ensure_ascii=False))

if __name__=='__main__':
    exec(sys.argv[1])

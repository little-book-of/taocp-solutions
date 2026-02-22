#!/usr/bin/env python3
from pathlib import Path
import re
from deep_translator import GoogleTranslator

ROOT=Path(__file__).resolve().parents[1]
import os
files=os.environ.get('TRANSLATE_FILES','').strip()
if files:
    SRC=[ROOT/f.strip() for f in files.split(',') if f.strip()]
else:
    SRC=[ROOT/'index.qmd',*sorted((ROOT/'vol-1').glob('*.md'))]
DST=ROOT/'zh'
tr=GoogleTranslator(source='en',target='zh-CN')

def chunk_text(s,n=2500):
    out=[]; i=0
    while i<len(s):
        j=min(len(s),i+n)
        if j<len(s):
            k=s.rfind('\n',i,j)
            if k>i+200: j=k+1
        out.append(s[i:j]); i=j
    return out

def trans(s):
    if not s.strip(): return s
    try: return tr.translate(s) or s
    except Exception: return s

for f in SRC:
    lines=f.read_text(encoding='utf-8').splitlines(True)
    out=[]; state={'buf':''}; in_code=False; in_math=False
    def flush():
        if state['buf']:
            out.extend(trans(c) for c in chunk_text(state['buf']))
            state['buf']=''
    for line in lines:
        st=line.strip()
        if st.startswith('```'):
            flush(); in_code=not in_code; out.append(line); continue
        if st=='$$':
            flush(); in_math=not in_math; out.append(line); continue
        if in_code or in_math:
            flush(); out.append(line); continue
        state['buf'] += line
    flush()
    text=''.join(out)
    text=re.sub(r'\bAlgorithm(s)?\b','算法',text,flags=re.I)
    text=re.sub(r'\bPermutation(s)?\b','置换',text,flags=re.I)
    text=re.sub(r'\bBinomial coefficient(s)?\b','二项式系数',text,flags=re.I)
    text=re.sub(r'\bSubroutine(s)?\b','子程序',text,flags=re.I)
    text=re.sub(r'\bCoroutine(s)?\b','协程',text,flags=re.I)
    d=DST/f.relative_to(ROOT)
    d.parent.mkdir(parents=True,exist_ok=True)
    d.write_text(text,encoding='utf-8')
    print('translated',f.relative_to(ROOT),flush=True)

import json,sys
sys.path.insert(0,'.')
from tok import collect
R=sys.argv[1]; out=[]
for p in ['index','detail','review']:
    for x in collect(open(f'{R}/en/{p}.html').read()):
        if x not in out: out.append(x)
json.dump({str(i):x for i,x in enumerate(out)},open('en.json','w'),ensure_ascii=False,indent=0)
for i,x in enumerate(out): print(i,x)

import gzip, struct, sys, bz2, lzma
def opener(p):
    b=open(p,'rb').read()
    if b[:2]==b'\x1f\x8b': return gzip.decompress(b)
    if b[:3]==b'BZh': return bz2.decompress(b)
    if b[:5]==b'\xfd7zXZ': return lzma.decompress(b)
    return b
class R:
    def __init__(s,b): s.b=b; s.i=0; s.refs=[]
    def int(s): v=struct.unpack('>i',s.b[s.i:s.i+4])[0]; s.i+=4; return v
    def dbl(s,n): v=struct.unpack('>%dd'%n,s.b[s.i:s.i+8*n]); s.i+=8*n; return v
    def ints(s,n): v=struct.unpack('>%di'%n,s.b[s.i:s.i+4*n]); s.i+=4*n; return v
    def str_(s):
        n=s.int()
        if n==-1: return None
        v=s.b[s.i:s.i+n].decode('utf8','replace'); s.i+=n; return v
    def read(s):
        f=s.int(); t=f&0xff; has_attr=f&(1<<9); has_tag=f&(1<<10)
        if t==254: return None
        if t==242: return None
        if t==255: return s.refs[(f>>8)-1]
        if t==1:
            s.int(); v=s.str_(); s.refs.append(v); return v
        if t==9: return s.str_()
        if t in (2,):
            attr=s.read() if has_attr else None
            tag=s.read() if has_tag else None
            car=s.read(); cdr=s.read()
            out=[(tag,car)]
            if isinstance(cdr,list): out+=cdr
            return out
        if t in (10,13,14,16,19):
            n=s.int()
            if t==10 or t==13:
                import numpy as np
                v=np.frombuffer(s.b,dtype='>i4',count=n,offset=s.i).copy(); s.i+=4*n
            elif t==14:
                import numpy as np
                v=np.frombuffer(s.b,dtype='>f8',count=n,offset=s.i).copy(); s.i+=8*n
            elif t==16: v=[s.read() for _ in range(n)]
            else: v=[s.read() for _ in range(n)]
            attr=s.read() if has_attr else None
            return {'t':t,'v':v,'attr':dict(attr) if attr else {}}
        raise Exception('type %d at %d'%(t,s.i))
def load(p):
    b=opener(p); assert b[:2]==b'X\n'
    r=R(b); r.i=2; ver=r.int(); r.int(); r.int()
    if ver==3: n=r.int(); r.i+=n
    return r.read()
def to_df(o):
    names=o['attr']['names']['v']; cols={}
    for nm,c in zip(names,o['v']):
        v=c['v']
        if 'levels' in c['attr']: lv=c['attr']['levels']['v']; v=[lv[x-1] if x>0 else None for x in v]
        cols[nm]=(v,c['attr'].get('class',{}).get('v') if isinstance(c['attr'].get('class'),dict) else None)
    return cols

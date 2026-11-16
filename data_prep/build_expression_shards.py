"""Split the VST orthogroup x sample matrix into small binary shards.

The dashboard fetches only the shard holding the requested orthogroup instead of
downloading the whole 42 MB matrix at startup.

Format (expr_shards/):
  samples.txt    one sample_id per line, in column order
  index.csv      OG,shard,row  (row is 0-based within the shard)
  shard_NNN.bin  uint16 little-endian, row-major, round(VST * 1000)
VST values in the source are stored with 3 decimals, so the encoding is lossless.

Usage: python3 data_prep/build_expression_shards.py vst_full_xz.rds expr_shards
"""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rds_reader as rds

SCALE = 1000
OGS_PER_SHARD = 50

src, out = sys.argv[1], sys.argv[2]
o = rds.load(src)
n_og, n_s = o['attr']['dim']['v']
ogs = o['attr']['dimnames']['v'][0]['v']
samples = o['attr']['dimnames']['v'][1]['v']
m = np.asarray(o['v']).reshape((n_s, n_og)).T          # R is column-major
enc = np.rint(m * SCALE)
assert np.all(np.abs(enc / SCALE - m) < 1e-9), "values are not 3-decimal; encoding would be lossy"
assert enc.min() >= 0 and enc.max() < 65535
enc = enc.astype('<u2')

os.makedirs(out, exist_ok=True)
with open(os.path.join(out, 'samples.txt'), 'w') as f:
    f.write('\n'.join(samples) + '\n')
with open(os.path.join(out, 'index.csv'), 'w') as f:
    f.write('OG,shard,row\n')
    for i, og in enumerate(ogs):
        f.write(f'{og},{i // OGS_PER_SHARD},{i % OGS_PER_SHARD}\n')
for s in range(0, n_og, OGS_PER_SHARD):
    enc[s:s + OGS_PER_SHARD].tofile(os.path.join(out, f'shard_{s // OGS_PER_SHARD:03d}.bin'))
print(f'{n_og} OGs x {n_s} samples -> {(n_og - 1) // OGS_PER_SHARD + 1} shards in {out}/')

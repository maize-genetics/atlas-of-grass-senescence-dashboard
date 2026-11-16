"""Export the per-library photosynthetic index (ps_index, 1 = photosynthetic, 0 = senescent).

Usage: python3 data_prep/build_ps_index.py ../04_photosynthetic_index/data ps_index.csv
Reads {leaf,root,stem}_metadata_ps_index.rds produced by 04_photosynthetic_index/01_calculate_ps_index.R.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rds_reader as rds

src, out = sys.argv[1], sys.argv[2]
rows = {}
for t in ['leaf', 'root', 'stem']:
    df = rds.to_df(rds.load(os.path.join(src, f'{t}_metadata_ps_index.rds')))
    for s, p in zip(df['sample_id'][0], df['ps_index'][0]):
        rows[s] = p
with open(out, 'w') as f:
    f.write('sample_id,ps_index\n')
    for s in sorted(rows):
        f.write(f'{s},{rows[s]:.4f}\n')
print(len(rows), 'libraries ->', out)

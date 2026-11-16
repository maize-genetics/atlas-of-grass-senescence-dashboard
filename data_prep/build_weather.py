"""Convert the NEWA daily station files (deg F, inches) to a tidy metric CSV for the dashboard.

Usage: python3 data_prep/build_weather.py newa_data_23.txt newa_data_24.txt weather_daily.csv
GDD follows 02_consolidate_seasons.R: base 10 C, upper 30 C.
"""
import csv, sys, datetime

def num(x):
    try: return float(x)
    except ValueError: return None

def f2c(x):
    v = num(x)
    return None if v is None else round((v - 32) * 5 / 9, 2)

rows = []
for path in sys.argv[1:-1]:
    for r in csv.DictReader(open(path), delimiter='\t'):
        d = datetime.datetime.strptime(r['date'], '%m/%d/%y').date()
        tmin, tmax = f2c(r['min_air_temp']), f2c(r['max_air_temp'])
        gdd = None if None in (tmin, tmax) else max(0.0, (min(tmax, 30) + max(tmin, 10)) / 2 - 10)
        rows.append(dict(season=d.year, date=d.isoformat(), julian_day=d.timetuple().tm_yday,
                         min_air_C=tmin, mean_air_C=f2c(r['avg_air_temp']), max_air_C=tmax,
                         soil_C=f2c(r['avg_soil_temp']), precip_mm=None if num(r['total_precipitation']) is None else round(num(r['total_precipitation']) * 25.4, 1),
                         gdd_C=None if gdd is None else round(gdd, 2)))
with open(sys.argv[-1], 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(len(rows), 'days ->', sys.argv[-1])

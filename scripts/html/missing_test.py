import cdms2
from timeutils import TimeUtility

timobj = TimeUtility()

f = cdms2.open('/mnt/CMIP3.1/CMIP5/CMIP5/ACCESS1-0/historical/Monthly/Ocean/zos/r1i1p1/zos_Omon_ACCESS1-0_historical_r1i1p1.xml')
t = f['zos'].getTime()
print timobj.has_all(t, 1, missingYears=0)

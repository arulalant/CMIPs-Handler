"""
In the CMIPs dataset for few frequencies data filename doesnot contains the 
realm information. 
for eg : snc_day_MPI-ESM-LR_historical_r1i1p1_19500101-19591231.nc

So in this second information day doesnt contain the corresponding realm type.

This script will rename those kind of nc filename into correct realm and its
freq.

For eg, it will move the above nc file into the below one.

snc_LIday_MPI-ESM-LR_historical_r1i1p1_19500101-19591231.nc

Note : with out realm and freq information in the filename, we can not move
the nc file into the server with proper directory structure !

Written By : Arulalan.T

Date : 28.02.2013

"""


import os
from projectdatatypes import Realm

ipath = raw_input("Enter the data path which contains CMIPs day, 3hr, 6hrLev, 6hrPlev, fx, grids types of nc files : ")
freq = raw_input("Enter frequency : ")
realm = raw_input("Enter the missing realm short name in the filename : ")
if realm not in Realm:
    raise ValueError("The realm '%s' is not available in Realm dictionary" % realm)
    
rrealm = raw_input("Please retype the missing realm short name in the filename : ")

if realm != rrealm:
    raise ValueError("realm mis-match. Please type correct realm ")

os.chdir(ipath)
for fname in os.listdir(ipath):
    fsplit = fname.split('_')
    if fsplit[1] ==  freq:
        fsplit[1] = realm + freq 
        newfname = '_'.join(fsplit)
        os.system('mv %s %s' % (fname, newfname))
        print "data file renamed from '%s' into '%s'" % (fname, newfname)    
    # end of if fsplit[1] ==  freq:
# ennd of for fname in os.listdir(ipath):     

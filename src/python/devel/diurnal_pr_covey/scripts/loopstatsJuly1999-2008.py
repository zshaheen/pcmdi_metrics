# /g/g18/covey1/CMIP5/Tides/OtherFields/GridpointTimeseries/TRMM3B/loopstatsJuly11999-2008.py

# Get time series of 3-hourly precipitation from TRMM obs at ARM SGP and selected Dai et al. 2007
# gridpoints for July. Make a composite diurnal cycle (8 timepoints) for one or more contiguous
# years concatenated together (e.g. 10 Julys x 31 days/July = 310 days) including std devs. Then
# do curve fitting to obtain the first three Fourier harmonic amplitudes and phases.

#       Curt Covey, Peter Gleckler and Charles Doutriaux         	April 2016
#	(from ./getstatsJuly2008.py -- in this case we loop thru the years 1999-2008)

import cdms2 
import MV2
import os
from check_calendar     import *
from closest_point      import *
from diurnal_statistics import *

# This script gets numbers for just the top 3 of 10 gridpoint/seasons in Covey et al. 2016, Fig. S12: 
nGridPoints = 3
gridptlats = [ 31.125,  31,  36.4]
gridptlons = [-83.125, 111, -97.5]

print 'Assumed list of GMT timepoints ='
GMTs = range(0, 24, 3) # *NOTE* These values are corrected from erroneous time coordinates in the original
#                               obs4MIPs TRMM3B42 files (see CMIP5 documentation / errata). Until corrected
#                               files are obtained, calendar check will give time-of-day incorrectly!
print GMTs

# Choose your month and year(s):
firstyear = 1999
lastyear  = 2008
nYears = lastyear - firstyear + 1
print 'Making a list of files to read data from ...'
fnames = os.listdir('/p/lscratchd/covey1/')
fnamesJul = []
for year in range(firstyear, lastyear + 1): # (NOTE: range function goes up to but NOT including the final argument)
	for fname in fnames:
		# Files for extracting July data:
		if (('pr_TRMM-L3_v7_'  + str(year) + '07010130-' + str(year) + '07312230.nc' in fname)
		or  ('pr_TRMM-L3_v7A_' + str(year) + '07010130-' + str(year) + '07312230.nc' in fname)): fnamesJul.append(fname)
print 'July file names:\n', fnamesJul
print 'Getting spacetime coordinates from first file ...'
f = cdms2.open('/p/lscratchd/covey1/' + fnamesJul[0])
d = f('pr')
modellats = d.getLatitude()
modellons = d.getLongitude()
latbounds = d.getdimattribute(1, 'bounds')
lonbounds = d.getdimattribute(2, 'bounds')
days_per_month = calcheck(d)
print 'Number of days in this month is %d.' % days_per_month
f.close()

# Loop over years to create diurnal cycle averaged over all years:
count = 0
for year in range(nYears):
        count += 1
        fname = '/p/lscratchd/covey1/' + fnamesJul[year]
        f = cdms2.open(fname)
        # Foreach (lat, lon) gridpoint, 8 times-of-day foreach of the month's number of days (NOT concatenated over > 1 year
        cattseries = MV2.zeros((nGridPoints, 8, days_per_month)) #            ... so DO NOT multiply days_per_month * nYears)
        # Allow for (lat, lon) coordinates in source data that differ from (lat, lon) coordinates chosen above:
        closestlats = MV2.zeros(nGridPoints)
        closestlons = MV2.zeros(nGridPoints)
        print 'Reading data from %s ...' % fname      
        for i in range(nGridPoints): # ** Loop over gridpoints **
                print '   (lat, lon) = (%8.3f, %8.3f)' % (gridptlats[i], gridptlons[i])
                closestlats[i] = find_closest(modellats, latbounds, gridptlats[i])
                closestlons[i] = find_closest(modellons, lonbounds, gridptlons[i]%360)
                print '   Closest (lat, lon) for gridpoint = (%8.3f, %8.3f)' % (closestlats[i], closestlons[i])
                tvarb = f('pr', lat=(closestlats[i], closestlats[i]), lon=(closestlons[i], closestlons[i]), squeeze = 1)
                tvarb *= 86400 # Convert PRECIPITATION units from kg/m2/s to mm/day.
                for j in range(8):           # ** Loop over hours: 8 subsets of the month's timeseries ... **
                        subset = tvarb[j::8] #    ... with j=0 => 1st GMT timepoint, j=1 => 2nd GMT timepoint, etc.
                        cattseries[i, j, 0:days_per_month] = subset[:]
        #---------------------------------------------------------------------------------
        # Intermediate diurnal cycle, for current year:
        avgvalues, stdvalues, LSTs = composite(nGridPoints, closestlons, GMTs, cattseries)
        #---------------------------------------------------------------------------------
        # Print intermediate diurnal cycle:    
        for i in range(nGridPoints):
                print '\nFor gridpoint %d at %5.1f deg latitude, %6.1f deg longitude ...' % (i, gridptlats[i], gridptlons[i])
                print '   Local Solar Times are:'
                print 'LST%d = {' % i
                for j in range(8):
                        print '%5.3f,' % LSTs[i, j],
                print '\n   Mean values for each time-of-day are:'
                print 'mean%d = {' % i
                for j in range(8):
                        print '%5.3f,' % avgvalues[i, j],
                print '\n   Standard deviations for each time-of-day are:'
                print 'std%d = {' % i
                for j in range(8):
                        print '%6.4f,' % stdvalues[i, j],                        
        print ' '
        # Accumulate intermediate diurnal-mean cycle values over for overall multi-year composite mean:
        if count == 1:
                compmean = avgvalues
        else:
                compmean = avgvalues + compmean
# Normalize overall multi-year mean:
compmean /= nYears
print compmean

# Take a "slow Fourier transform" of the overall multi-year mean diurnal cycle:
print '**************   ', compmean[0][0]
cycmean, maxvalue, tmax = sft(compmean, LSTs)
print '**************   ', compmean[0][0]
# Print Fourier harmonics:
for i in range(nGridPoints):
        print 'For gridpoint %d:' % i
        print '  Mean value over cycle = %6.2f' % cycmean[i]
        print '  Diurnal     maximum   = %6.2f at %6.2f hr Local Solar Time.' % (maxvalue[i, 0], tmax[i, 0] % 24)
        print '  Semidiurnal maximum   = %6.2f at %6.2f hr Local Solar Time.' % (maxvalue[i, 1], tmax[i, 1] % 24)
        print '  Terdiurnal  maximum   = %6.2f at %6.2f hr Local Solar Time.' % (maxvalue[i, 2], tmax[i, 2] % 24)
        print ' '

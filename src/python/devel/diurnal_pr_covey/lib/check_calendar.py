# /export/covey1/CMIP5/Tides/OtherFields/TRMM3B/check_calendar.py

# Calendar-checking utility.

#                       Curt Covey                                   April 2016

import cdtime

def calcheck(s):
   print 'Calendar check for %s:' % s.id
   print '  Shape of field =', s.shape
   taxis = s.getTime()
   t = taxis[:]
   N = len(t)
   
   print '  Length of time series is %d.' % N
   if N % 8 == 0: # Assumes 8 time-points per day here and in following code
      ndays = N / 8
   else:
      print '** Stop: length of time series is not an integer number of days. **'
      raise RuntimeError
   calendar = taxis.getCalendar()
   relunits = taxis.units
   time1  = cdtime.reltime(taxis[0],   relunits)
   timeN  = cdtime.reltime(taxis[N-1], relunits)
   ctime1 = time1.tocomp(calendar)
   ctimeN = timeN.tocomp(calendar)
   print '  First time-point in series is %s.' % ctime1
   print '  Last  time-point in series is %s.' % ctimeN
   return ndays

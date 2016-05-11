# /g/g18/covey1/CMIP5/Tides/OtherFields/GridpointTimeseries/TRMM3B/diurnal_statistics.py

#         Curt Covey, PCMDI/LLNL                                      April 2016

# Functions for computing diurnal-cycle statistics:

def composite(nGridPoints, lons, GMTs, tseries):
        '''
Make diurnal-cycle composite means and standard deviations at a given set of gridpoints, from a given time series
of 3-hourly data. This time frequency, with 8 timepoints per day, is hardwired into the code. Associated times-of-day
are given as input; typically they are either (0:00, 3:00, 6:00, ... 21:00) GMT or (1:30, 4:30, 7:30, ... 22:30) GMT.

On input: nGridPoints = number of gridpoints
          lons[i] = longitudes of gridpoints; latitudes are not needed
          GMTs[j] = time coordinates input as described above
          tseries[i, j, k)] = time series to be averaged, etc., over the k-index
          ... with i identifying which gridpoint, j identifying which time-of-day, k identifying which day
          NOTE: For one month's data in one year, 0 < k < days_per_month - 1
                For the same month's data concatenated over several years, 0 < k < nYears * days_per_month - 1

On output: avgvalues[i, j] = mean diurnal cycle values at each gridpoint (i) for the 8 times-of-day (j)
           stdvalues[i, j] = associated standard deviations; can be plotted as "error bars"     in the diurnal cycle
           LSTs     [i, j] = associated Local Solar Times;   can be plotted as independent varb in the diurnal cycle
           
                            Curt Covey, PCMDI/LLNL                                      April 2016
        '''
        import genutil
        import MV2
        LSTs = MV2.zeros((nGridPoints, 8))      # This array will hold 8 Local Solar Times for each gridpoint
        avgvalues = MV2.zeros((nGridPoints, 8)) # This array will hold mean values    at 8 Local Solar Times for each gridpt
        stdvalues = MV2.zeros((nGridPoints, 8)) # This array will hold std deviations at 8 Local Solar Times for each gridpt
        for i in range(nGridPoints):
                for j in range(8):
                        LSTs[i, j] = (GMTs[j] + lons[i] / 15) % 24
                        avgvalues[i, j] = MV2.average(tseries[i, j, :])
                        stdvalues[i, j] =  genutil.statistics.std(tseries[i, j, :])
        return (avgvalues, stdvalues, LSTs)

def sft(x, t):
        '''
This is a simple SLOW Fourier integration via the trapezoidal rule -- an "SFT," not an FFT!

Return mean + amplitudes and times-of-maximum of the first three Fourier harmonic components of a time series x(t).
Do NOT detrend the time series first, in order to retain the "sawtooth" frequency implied by the input length of the
time series (e.g. the 24-hour period from a composite-diurnal cycle).

On input: x[i, j] = values      at each gridpoint (i) for N times (j), e.g. N = 8 for a 3-hr composite-diurnal cycle
          t[i, j] = timepoints  at each gridpoint (i) for N times (j), e.g. Local Standard Times
          
On output: c[i] = mean value at each gridpoint (i) in the time series (= constant term in Fourier series)  
           maxvalue[i, k] = amplitude       at each gridpoint (i) for each Fourier harmonic (k)
           tmax    [i, k] = time of maximum at each gridpoint (i) for each Fourier harmonic (k)

                Curt Covey, PCMDI/LLNL                                      April 2016
                (from /Users/covey1/EarthAtmosphericTides/WACCM1Output/sft_detrend_and_getfcomponents.py)
        '''
        import MV2
        nGridPoints = len(x)
        N = len(x[0]) # Length of time series for each gridpoint

        # Calculate sums for trapezoidal-rule integation:
        a = MV2.zeros((nGridPoints, 3))
        b = MV2.zeros((nGridPoints, 3))
        c = MV2.zeros( nGridPoints    )
        for n in range(3):          
            a[:, n] = x[:, 0]
            b[:, n] =  0.0
        c = x[:, 0]
        for j in range(1, N):
            for n in range(3):
               a[:, n] += x[:, j] * MV2.cos((n+1) * MV2.pi * j / 4.0)
               b[:, n] += x[:, j] * MV2.sin((n+1) * MV2.pi * j / 4.0)
            c[:]       += x[:, j]
               
       # Normalize per length of time series:
        for n in range(3):
            a[:, n] = 2.0 / N * a[:, n]
            b[:, n] = 2.0 / N * b[:, n]
        c[:]        = 1.0 / N * c[:]

        # Calculate amplitudes and phases:
        tmax      = MV2.zeros((nGridPoints, 3)) # time  of maximum for nth component
        maxvalue  = MV2.zeros((nGridPoints, 3)) # value of maximum for nth component (=1/2 peak-to-peak amplitude)
        for n in range(3):
            tmax[:, n] = MV2.arctan2(b[:, n], a[:, n])
            maxvalue[:, n] = a[:, n] * MV2.cos(tmax[:, n]) + b[:, n] * MV2.sin(tmax[:, n])
            for i in range(nGridPoints):
                    if maxvalue[i, n] < 0:              # Maximum value is by definition > 0, so ...
                       maxvalue[i, n] = -maxvalue[i, n] # ... extremum calculated above must have been minimum,
                       tmax[i, n] += MV2.pi             # ... and phase angle must have been 180 degrees off.
            tmax[:, n] = tmax[:, n] * 12.0 / (MV2.pi * (n+1)) # Converting from radians to hours
            tmax[:, n] = tmax[:, n] + t[:, 0]                 # Converting to local time
        return c, maxvalue, tmax
   

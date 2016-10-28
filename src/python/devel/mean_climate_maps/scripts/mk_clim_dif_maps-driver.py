import vcs
import cdms2
import MV2
import sys,os
import json
import string
import pcmdi_metrics
import time

era = 'cmip5'
exp = 'historical'

m = 'crunchy'
#m = 'oceanonly'

if m == 'oceanonly':
 basedir = '/work/gleckler1/'

if m == 'crunchy':
 basedir = '/export_backup/gleckler1/'
#basedir = '/work/lee1043/cdat/pmp/' ## FOR TEST -jwlee

plots_outdir = '/work/gleckler1/processed_data/clim_plots/'
#plots_outdir = '/work/lee1043/cdat/pmp/clim_plots/' ## FOR TEST -jwlee


vars = ['pr','rlut']   #,'tas','rt']
#vars = ['pr']

seasons = ['djf', 'mam', 'jja', 'son']

# Load the obs dictionary
fjson = open(
         os.path.join(
             sys.prefix,
             "share",
             "pmp",
             "obs_info_dictionary.json"))

#fjson = open('/export_backup/lee1043/git/pcmdi_metrics/doc/obs_info_dictionary.json') ## FOR TEST -jwlee
obs_dic = json.loads(fjson.read())
fjson.close()

#execfile('/export/gleckler1/git/pcmdi_metrics/src/python/pcmdi/seasonal_mean.py')
execfile('./plot_map_4panel.py')

# OBS path
opathin = basedir + 'processed_data/obs/atm/mo/VAR/OBS/ac/VAR_OBS_000001-000012_ac.nc'

# MOD path
mpathin = '/work/gleckler1/processed_data/metrics_package/interpolated_model_clims_historical/global/cmip5.MOD.historical.r1i1p1.mo.Amon.VAR.ver-1.1980-2005.interpolated.linear.2.5x2.5.global.AC.nc'

po = plots_outdir
subs = ['',era,exp]
for sub in subs: 
  po = po + '/' + sub
  try:
    os.mkdir(po)
  except:
    pass
import vcs
canvas=vcs.init(geometry=(1000,800),bg=True)
canvas.drawlogooff()

for var in vars:

   #==============================================================================
   # Observation
   #------------------------------------------------------------------------------
   obsd = obs_dic[var]['default']
   obst = string.replace(opathin,'VAR',var)
   obst = string.replace(obst,'OBS',obsd)
   fo = cdms2.open(obst)
   do = fo(var)
   ogrid = do.getGrid()
   fo.close()

   # Seasonal climatology of observation
   obs = {}
   for season in seasons:
     obs[season] = pcmdi_metrics.pcmdi.seasonal_mean.compute(do,season)

   #==============================================================================
   # Models
   #------------------------------------------------------------------------------
   # Get list of models
   mods = []
   mpatht = string.replace(mpathin,'MOD','*')
   mpatht = string.replace(mpatht,'VAR',var)
   lst = os.popen('ls ' + mpatht).readlines()
   for l in lst:
     mod = string.split(l,'.')[1] 
     if mod not in mods: mods.append(mod) 

   # For test...
#  mods = mods[0:3]
   #mods = mods[0:1]

   # Dictionary to save
   fld = {} # Model's climatology field
   dif = {} # Difference btw. model and obs
   mmm = {} # Multi model ensemble

   for season in seasons:
     mmm[season] = 0

   #------------------------------------------------------------------------------
   # Calculate seasonal mean and its difference against obs from MMM and individual models 
   #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
   for mod in mods:

     fld[mod] = {} # Model's climatology field
     dif[mod] = {} # Difference btw. model and obs

     mpatht = string.replace(mpathin,'MOD',mod)
     mpatht = string.replace(mpatht,'VAR',var)

     fm = cdms2.open(mpatht)
     dm = fm(var)
     fm.close()
#    print mod

     for season in seasons:

       # Seasonal climatology
       fld[mod][season] = pcmdi_metrics.pcmdi.seasonal_mean.compute(dm,season)

       # Regrid to observational grid
       fld_regrid = fld[mod][season].regrid(ogrid, regridTool='regrid2', mkCyclic=True)

       # Accumulate for MMM
       mmm[season] = MV2.add(mmm[season],fld_regrid)

       # Get difference field
       dif[mod][season] = MV2.subtract(fld_regrid,obs[season])
       dif[mod][season].id = 'Diff_'+season.upper()+'_'+var

   #------------------------------------------------------------------------------
   # Get multi-model mean (MMM)
   #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
   mmm_dif = {}
   for season in seasons:
     mmm[season] = mmm[season]/float(len(mods))

     mmm_dif[season] = mmm[season] - obs[season] 
     mmm_dif[season] = MV2.subtract(mmm[season],obs[season]) 
     mmm_dif[season].id = 'Diff_'+season.upper()+'_'+var

   #------------------------------------------------------------------------------
   # Create 4 panel plots: model, obs, model-obs, mmm-obs
   #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
   pout = plots_outdir + '/' + era + '/' + exp + '/' + var
   try:
     os.mkdir(pout) 
   except:
     pass

#  seasons = seasons[0:1] ## For test!!!

   for season in seasons:
     if var == 'pr' and do.units == 'kg m-2 s-1' and dm.units == 'kg m-2 s-1':
       obs[season] = obs[season] * 86400.  
       obs[season].units = 'mm d-1'
       mmm[season] = mmm[season] * 86400.
       mmm[season].units = 'mm d-1'
       mmm_dif[season] = mmm_dif[season] * 86400.
       mmm_dif[season].units = 'mm d-1'
     for mod in mods:
       go = pout + '/' + var +'.' + season + '.' + mod 
       debug = True
#      debug = None
       if var == 'pr' and do.units == 'kg m-2 s-1' and dm.units == 'kg m-2 s-1':
         fld[mod][season] = fld[mod][season] * 86400.  
         fld[mod][season].units = 'mm d-1'
         dif[mod][season] = dif[mod][season] * 86400.  
         dif[mod][season].units = 'mm d-1'

       a = time.time()
#      print var,' ', mod,' ', season,'  above plotting'
       plot_4panel(debug, var, season, mod, fld[mod][season], obs[season], dif[mod][season], mmm_dif[season], go, canvas=canvas)
       b = time.time()

       print var,' ', mod,' ', season,'  plotting time is ', b-a

 




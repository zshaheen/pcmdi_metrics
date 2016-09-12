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

if m == 'oceanonly':
 basedir = '/work/gleckler1/'

if m == 'crunchy':
 basedir = '/export_backup/gleckler1/'

plots_outdir = '/work/gleckler1/processed_data/clim_plots/'


vars = ['pr','rlut','tas','rt']
vars = ['pr']

# Load the obs dictionary
fjson = open(
        os.path.join(
            sys.prefix,
            "share",
            "pmp",
            "obs_info_dictionary.json"))
obs_dic = json.loads(fjson.read())
fjson.close()

#execfile('/export/gleckler1/git/pcmdi_metrics/src/python/pcmdi/seasonal_mean.py')



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


v = vcs.init()

for var in vars:

   obsd = obs_dic[var]['default']
   obst = string.replace(opathin,'VAR',var)
   obst = string.replace(obst,'OBS',obsd)
   fo = cdms2.open(obst)
   do = fo(var)

   mods = []
   mpatht = string.replace(mpathin,'MOD','*')
   mpatht = string.replace(mpatht,'VAR',var)
   lst = os.popen('ls ' + mpatht).readlines()
   for l in lst:
     mod = string.split(l,'.')[1] 
     if mod not in mods: mods.append(mod) 

   for mod in mods:
        mpatht = string.replace(mpathin,'MOD',mod)
        mpatht = string.replace(mpatht,'VAR',var)

        fm = cdms2.open(mpatht)
        dm = fm(var)
## RGRID OBS FOR FIRST MOD
        if mod == mods[0]:
          mgrid = dm.getGrid()
          dor = do.regrid(mgrid)
          print 'done regrindding obs'

        print mod,' ', dm.shape, dor.shape

        mod_djf = pcmdi_metrics.pcmdi.seasonal_mean.compute(dm,'djf')
        mod_mam = pcmdi_metrics.pcmdi.seasonal_mean.compute(dm,'mam')
        mod_jja = pcmdi_metrics.pcmdi.seasonal_mean.compute(dm,'jja')
        mod_son = pcmdi_metrics.pcmdi.seasonal_mean.compute(dm,'son')

        obs_djf = pcmdi_metrics.pcmdi.seasonal_mean.compute(dor,'djf')
        obs_mam = pcmdi_metrics.pcmdi.seasonal_mean.compute(dor,'mam')
        obs_jja = pcmdi_metrics.pcmdi.seasonal_mean.compute(dor,'jja')
        obs_son = pcmdi_metrics.pcmdi.seasonal_mean.compute(dor,'son')

        dif_djf = MV2.subtract(mod_djf,obs_djf)
        dif_mam = MV2.subtract(mod_djf,obs_mam)
        dif_jja = MV2.subtract(mod_djf,obs_jja)
        dif_son = MV2.subtract(mod_djf,obs_son)

        pout = plots_outdir + '/' + era + '/' + exp + '/' + var
        try:
          os.mkdir(pout) 
        except:
         pass

        go = pout + '/' + var + '.' + mod 
         
        v.plot(dif_djf, bg=1)
        v.png(go)

        time.sleep(.5)
        v.clear()
#       w = sys.stdin.readline()

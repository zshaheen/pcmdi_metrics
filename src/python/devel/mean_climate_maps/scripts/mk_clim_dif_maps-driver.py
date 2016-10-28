#!/usr/bin/env python
import vcs
import cdms2
import MV2
import sys,os
import json
import string
import pcmdi_metrics
import time
from pcmdi_metrics.mean_climate_maps import plot_4panel
from pcmdi_metrics.pcmdi import pmp_parser
import glob

parser = pmp_parser.PMPParser()

parser.add_argument("--era",help="era",default="cmip5")
parser.add_argument("--experiment",help="experiment",default="historical")
parser.add_argument("--base-directory",help="base directory",default="/export_backup/gleckler1")
parser.add_argument("--plots-output-directory",help="output directory for plots",default="/work/gleckler1/processed_data/clim_plots")
parser.add_argument("--models-directory",help="models directory",default="/work/gleckler1/processed_data/metrics_package/interpolated_model_clims_historical/global")

parser.add_argument("--seasons",type=str,
        nargs='+',
        dest='seasons',
        help='Seasons to use',
        default=["djf","mam","jja","son"],
        required=False)
parser.add_argument("--fg",help="plot in foreground",action="store_true",default=False)
args = parser.parse_args(sys.argv[1:])

variables = args.vars
if variables is None:
  variables = ['pr','rlut']   #,'tas','rt']


# Load the obs dictionary
fjson = open(
         os.path.join(
             sys.prefix,
             "share",
             "pmp",
             "obs_info_dictionary.json"))

obs_dic = json.loads(fjson.read())
fjson.close()

# OBS path
opathin = os.path.join(args.base_directory,'processed_data','obs','atm','mo','VAR','OBS','ac','VAR_OBS_000001-000012_ac.nc')

# MOD path
mpathin = os.path.join(args.models_directory,'cmip5.MOD.historical.r1i1p1.mo.Amon.VAR.ver-1.1980-2005.interpolated.linear.2.5x2.5.global.AC.nc')

try:
    os.makedirs(os.path.join(args.plots_directory,args.era,args.experiment))
except:
    pass

canvas=vcs.init(geometry=(1000,800),bg=not args.fg)
canvas.drawlogooff()

for var in variables:
   #==============================================================================
   # Observation
   #------------------------------------------------------------------------------
   obsd = obs_dic[var]['default']
   obst = opathin.replace('VAR',var)
   obst = obst.replace('OBS',obsd)
   fo = cdms2.open(obst)
   do = fo(var)
   ogrid = do.getGrid()
   fo.close()

   # Seasonal climatology of observation
   obs = {}
   for season in args.seasons:
     obs[season] = pcmdi_metrics.pcmdi.seasonal_mean.compute(do,season)

   #==============================================================================
   # Models
   #------------------------------------------------------------------------------
   # Get list of models
   mods = set()
   mpatht = mpathin.replace('MOD','*').replace('VAR',var)
   lst = glob.glob(mpatht)
   for l in lst:
     mod = l.split('.')[1] 
     mods.add(mod) 

   # Dictionary to save
   fld = {} # Model's climatology field
   dif = {} # Difference btw. model and obs
   mmm = {} # Multi model ensemble

   for season in args.seasons:
     mmm[season] = 0

   #------------------------------------------------------------------------------
   # Calculate seasonal mean and its difference against obs from MMM and individual models 
   #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
   for mod in mods:

     fld[mod] = {} # Model's climatology field
     dif[mod] = {} # Difference btw. model and obs

     mpatht = mpathin.replace('MOD',mod).replace('VAR',var)

     fm = cdms2.open(mpatht)
     dm = fm(var)
     fm.close()

     for season in args.seasons:

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
   for season in args.seasons:
     mmm[season] = mmm[season]/float(len(mods))

     mmm_dif[season] = mmm[season] - obs[season] 
     mmm_dif[season] = MV2.subtract(mmm[season],obs[season]) 
     mmm_dif[season].id = 'Diff_'+season.upper()+'_'+var

   #------------------------------------------------------------------------------
   # Create 4 panel plots: model, obs, model-obs, mmm-obs
   #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
   pout = os.path.join(args.plots_output_directory,args.era,args.experiment,var)
   try:
     os.makedirs(pout) 
   except Exception,err:
       pass


   for season in args.seasons:
     if var == 'pr' and do.units == 'kg m-2 s-1' and dm.units == 'kg m-2 s-1':
       obs[season] = obs[season] * 86400.  
       obs[season].units = 'mm d-1'
       mmm[season] = mmm[season] * 86400.
       mmm[season].units = 'mm d-1'
       mmm_dif[season] = mmm_dif[season] * 86400.
       mmm_dif[season].units = 'mm d-1'
     for mod in mods:
       go = os.path.join(pout,var+'.'+season+'.'+mod)
       if var == 'pr' and do.units == 'kg m-2 s-1' and dm.units == 'kg m-2 s-1':
         fld[mod][season] = fld[mod][season] * 86400.  
         fld[mod][season].units = 'mm d-1'
         dif[mod][season] = dif[mod][season] * 86400.  
         dif[mod][season].units = 'mm d-1'

       a = time.time()
       plot_4panel(not args.fg, var, season, mod, fld[mod][season], obs[season], dif[mod][season], mmm_dif[season], go, canvas=canvas)
       b = time.time()
       print var,' ', mod,' ', season,'  plotting time is ', b-a

 




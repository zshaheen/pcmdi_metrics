#!/usr/bin/env python

import numpy as NP
import matplotlib.pyplot as PLT
import json
import sys, os
import getopt
import pcmdi_metrics
from pcmdi_metrics.taylor_diagram_mpl import TaylorDiagram

test = True

fjson = open(
    os.path.join(
        pcmdi_metrics.__path__[0],
        "..",
        "..",
        "..",
        "..",
        "share",
        "CMIP_metrics_results",
        "CMIP5",
        "amip",
        "rlut_2.5x2.5_esmf_linear_metrics.json"))
        #../../../../share/CMIP_metrics_results//CMIP5/amip
obs_dic = json.loads(fjson.read())
fjson.close()

print 'fjson is ', fjson

# Below if for dia.ax.plot -- turn off now
#x95 = [0.05, 13.9] # For Prcp, this is for 95th level (r = 0.195)
#y95 = [0.0, 71.0]
#x99 = [0.05, 19.0] # For Prcp, this is for 99th level (r = 0.254)
#y99 = [0.0, 70.0]

args=sys.argv[1:]
letters='j:v:s:e:d:o:'
keywords=['json=','var=','season=','exp=','domain=','plotpath=']
json_path = 'default'
season ='default'
domain ='NHEX'
var = 'default'
pathout = './'
opts,pargs=getopt.getopt(args,letters,keywords)
for o,p in opts:
    if o in ['-j','--json']:
        json_path=p
    if o in ['-v','--var']:
        var = p
    if o in ['-s','--season']: # djf / mam / jja / son / ann
        season=p
    if o in ['-o','--plotpath']:
        pathout=p
    if o in ['-e','--exp']:
        exp=p
    if o in ['-d','--domain']:
        dom=p

print json_path,' ',season,' ', pathout,' ', exp,' ', var , ' ', dom
print 'after args'

fjson = open(
    os.path.join(
        pcmdi_metrics.__path__[0],
        "..",
        "..",
        "..",
        "..",
        "share",
        "CMIP_metrics_results",
        "CMIP5",
        "amip",
        var+"_2.5x2.5_esmf_linear_metrics.json"))

dd = json.loads(fjson.read())
fjson.close()

if test:
    ### TEMPORARY UNTIL JSON FILES ARE UPDATED TO INCLUDED STD
    #pi = '/work/gleckler1/processed_data/metrics_package/metrics_results/cmip5clims_metrics_package-amip/v1.1/pr_2.5x2.5_esmf_linear_metrics.json'
    pi = '/Users/lee1043/Documents/Research/PMP/pcmdi_metrics/data/CMIP_metrics_results/CMIP5/amip/pr_2.5x2.5_esmf_linear_metrics.json'
    dd = json.load(open(pi,'rb'))
    var = 'pr'

if var == 'pr':
    unit_adj = 28.
else:
    unit_adj = 1.

mods = dd.keys()

for mod in mods:
   if mod in ['METRICS','GridInfo','RegionalMasking','References','DISCLAIMER', 'metrics_git_sha1','uvcdat_version']:
    try:
     mods.remove(mod)
    except:
     pass

seasons = [season]
if season == 'all':
  seasons = ['djf', 'mam', 'jja', 'son']
  rects = {'djf':221, 'mam':222, 'jja':223, 'son':224} # subplot location
  fig = PLT.figure(figsize=(14,11)) # optimized figure size for four subplots
  fig_filename = var + '_' + exp + '_taylor_4panel_' + season + '_' + dom
else:
  rects = {}
  rects[season] = 111 # subplot location
  fig = PLT.figure(figsize=(11,8)) # optimized figure size for one subplot
  fig_filename = var + '_' + exp + '_taylor_1panel_' + season + '_' + dom

fig.suptitle(var.title()+', '+(exp+', '+dom).upper(), size='x-large') # Giving title for the entire canvas

stdrefs = {}
source_ref = dd[mods[0]]["defaultReference"]['source']

for season in seasons:
    # Reference std from obs
    stdrefs[season] = float(dd[mods[0]]["defaultReference"]['r1i1p1']['global']['std-obs_xy_'+season+'_'+dom])*unit_adj

    samples = {}
    all_mods = []
    for mod in mods:
        cor = float(dd[mod]["defaultReference"]['r1i1p1']['global']['cor_xy_'+season+'_'+dom])
        std = float(dd[mod]["defaultReference"]['r1i1p1']['global']['std_xy_'+season+'_'+dom])*unit_adj
        all_mods.append([std,cor,str(mod)])
    samples[season] = all_mods

    colors = PLT.matplotlib.cm.Set1(NP.linspace(0,1,len(samples[season])))

    dia = TaylorDiagram(stdrefs[season], fig=fig, rect=rects[season],
                        #label='Reference')
                        label=source_ref)

    # Diagonal lines, turned off now ---
    #dia.ax.plot(x95,y95,color='k')
    #dia.ax.plot(x99,y99,color='k')

    # Add samples to Taylor diagram
    for i,(stddev,corrcoef,name) in enumerate(samples[season]):
        dia.add_sample(stddev, corrcoef,
                       marker='$%d$' % (i+1), ms=10, ls='',
                       #mfc='k', mec='k', # B&W
                       mfc=colors[i], mec=colors[i], # Colors
                       label=name)

    # Add RMS contours, and label them
    contours = dia.add_contours(levels=5, colors='0.5') # 5 levels
    dia.ax.clabel(contours, inline=1, fontsize=10, fmt='%.1f')
    # Tricky: ax is the polar ax (used for plots), _ax is the
    # container (used for layout)
    dia._ax.set_title(season.upper()) # Title for the subplot

# Add a figure legend and title. For loc option, place x,y tuple inside [ ].
# Can also use special options here:
# http://matplotlib.sourceforge.net/users/legend_guide.html

fig.legend(dia.samplePoints,
           [ p.get_label() for p in dia.samplePoints ],
           numpoints=1, prop=dict(size='small'), loc='right')

PLT.savefig(pathout + '/' + fig_filename + '.png')

if test:
    PLT.ion()
    PLT.show()

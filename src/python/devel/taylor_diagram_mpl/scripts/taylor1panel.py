#!/usr/bin/env python

import numpy as NP
import matplotlib.pyplot as PLT
import json
import sys, os
import getopt
import pcmdi_metrics
from pcmdi_metrics.taylor_diagram_mpl import TaylorDiagram

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

obs_dic = json.loads(fjson.read())
fjson.close()

#../../../../share/CMIP_metrics_results//CMIP5/amip

print 'fjson is ', fjson

#w = sys.stdin.readline()

# Reference std
stdrefs = dict(winter=48.491)

x95 = [0.05, 13.9] # For Prcp, this is for 95th level (r = 0.195)
y95 = [0.0, 71.0]
x99 = [0.05, 19.0] # For Prcp, this is for 99th level (r = 0.254)
y99 = [0.0, 70.0]

rects = dict(winter=221)

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
    if o in ['-s','--season']:
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
        "rlut_2.5x2.5_esmf_linear_metrics.json"))

dd = json.loads(fjson.read())
fjson.close()

### TEMPORARY UNTIL JSON FILES ARE UPDATED TO INCLUDED STD
pi = '/work/gleckler1/processed_data/metrics_package/metrics_results/cmip5clims_metrics_package-amip/v1.1/pr_2.5x2.5_esmf_linear_metrics.json'
dd = json.load(open(pi,'rb'))
####

#print dd['CCSM4'].keys()
mods = dd.keys()



for mod in mods:
   print 'here is mod ', mod
   if mod in ['METRICS','GridInfo','RegionalMasking','References','DISCLAIMER', 'metrics_git_sha1','uvcdat_version']:
    try:
     mods.remove(mod)
    except:
     pass

print 'mods are ', mods

#w = sys.stdin.readline()

samples = {}
winter = []
for mod in mods:
  cor = float(dd[mod]["defaultReference"]['r1i1p1']['global']['cor_xy_djf_NHEX'])
  std = float(dd[mod]["defaultReference"]['r1i1p1']['global']['std_xy_djf_NHEX'])*28.
  winter.append([std,cor,str(mod)])

samples['winter'] = winter

colors = PLT.matplotlib.cm.Set1(NP.linspace(0,1,len(samples['winter'])))


#w = sys.stdin.readline()

fig = PLT.figure(figsize=(11,8))  # 11,8
fig.suptitle("", size='x-large')

for season in ['winter']:

    dia = TaylorDiagram(stdrefs[season], fig=fig, rect=rects[season],
                        label='Reference')

    dia.ax.plot(x95,y95,color='k')
    dia.ax.plot(x99,y99,color='k')

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
    dia._ax.set_title(season.capitalize())

# Add a figure legend and title. For loc option, place x,y tuple inside [ ].
# Can also use special options here:
# http://matplotlib.sourceforge.net/users/legend_guide.html

fig.legend(dia.samplePoints,
           [ p.get_label() for p in dia.samplePoints ],
           numpoints=1, prop=dict(size='small'), loc='right')

print 'above fig.legend'

#fig.tight_layout()

print 'below fig.legend'

PLT.savefig(pathout + '/' + var + '_' + exp + '_taylor_1panel.png')
print 'below save plot'


#PLT.show()

#!/usr/bin/env python

import numpy as NP
import matplotlib.pyplot as PLT
import json
import sys, os
import pcmdi_metrics
from pcmdi_metrics.taylor_diagram_mpl import TaylorDiagram
import argparse
from argparse import RawTextHelpFormatter
import sys
import string


P = argparse.ArgumentParser(
    description='Runs PCMDI Metrics Computations',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

P.add_argument("-j", "--json",
                      type = str,
                      dest = 'json',
                      help = "Path to json file")
P.add_argument("-v", "--variable",
                      type = str,
                      dest = 'var',
                      help = "(Case Insensitive)")
P.add_argument("-s", "--season",
                      type = str,
                      default = 'DJF',
                      help = "Season for mode of variability\n"
                             "- Available options: DJF (default), MAM, JJA, SON or all")
P.add_argument("-e", "--experiment",
                      type = str,
                      dest = 'exp',
                      default = 'historical',
                      help = "AMIP, historical or picontrol")
P.add_argument("-d", "--domain",
                      type = str,
                      dest = 'dom',
                      default = 'global',
                      help = "put options here")
P.add_argument("-o", "--plotpath",
                      type = str,
                      dest = 'outpath',
                      default = '',
                      help = "")

args = P.parse_args(sys.argv[1:])

json_path = args.param
var = args.var
domain = 
w = sys.stdin.readline()

test = False  #True

#args=sys.argv[1:]
#letters='j:v:s:e:d:o:'
#keywords=['json=','var=','season=','exp=','domain=','plotpath=']
#json_path = 'default'
#season ='default'
#domain ='NHEX'
#var = 'default'
#pathout = './'
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

fj = open(json_path)
dd = json.loads(fj.read())
fj.close()

if var == 'pr':
    unit_adj = 28.
else:
    unit_adj = 1.

mods = dd['RESULTS'].keys()

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
source_ref = dd['RESULTS'][mods[0]]["defaultReference"]['source']

for season in seasons:
    # Reference std from obs
#   stdrefs[season] = float(dd['RESULTS'][mods[0]]["defaultReference"]['r1i1p1']['global']['std-obs_xy_'+season+'_'+dom])*unit_adj
    stdrefs[season] = float(dd['RESULTS'][mods[0]]["defaultReference"]['r1i1p1']['global']['std-obs_xy_'+season])*unit_adj

    samples = {}
    all_mods = []
    for mod in mods:
        cor = float(dd['RESULTS'][mod]["defaultReference"]['r1i1p1']['global']['cor_xy_'+season])
        std = float(dd['RESULTS'][mod]["defaultReference"]['r1i1p1']['global']['std_xy_'+season])*unit_adj
        all_mods.append([std,cor,str(mod)])
    samples[season] = all_mods

    colors = PLT.matplotlib.cm.Set1(NP.linspace(0,1,len(samples[season])))

    dia = TaylorDiagram(stdrefs[season], fig=fig, rect=rects[season],
                        #label='Reference')
                        label=source_ref)

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

#!/usr/bin/env python

import numpy as NP
import matplotlib.pyplot as PLT
import json
import sys, os
import string
import getopt
import pcmdi_metrics
#from pcmdi_metrics.bias_bar_chart import BarChart
from SeabarChart_mpl import BarChart
import argparse
from argparse import RawTextHelpFormatter

test = False
test = True

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
P.add_argument("-s", "--stat",
                      type = str,
                      default = 'rms',
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

args = P.parse_args(sys.argv[1:])

json_path = args.json
var = args.var
dom = args.dom
exp = args.exp
stat = args.stat
pathout = args.outpath


print json_path,' ',stat,' ', pathout,' ', exp,' ', var , ' ', dom
print 'after args'

try:
 fj = open(json_path)
 dd = json.loads(fj.read())
 fj.close()
except:
 json_path = string.replace(json_path,'VAR',var)
 fj = open(json_path)
 dd = json.loads(fj.read())
 fj.close()


unit_adj = 1
if var == 'pr':
    unit_adj = 28.
if var == 'tauu':
    unit_adj = 1000.


mods = dd['RESULTS'].keys()
#mods.sort()
mods = sorted(mods, key=lambda s:s.lower())

#seasons = [season]
season = 'all'
if season == 'all':
  seasons = ['ann', 'djf', 'mam', 'jja', 'son']
  rects = {'ann':511, 'djf':512, 'mam':513, 'jja':514, 'son':515} # subplot location
  fig = PLT.figure(figsize=(10,16)) # optimized figure size for five subplots
  fig_filename = var + '_' + exp + '_bias_5panel_' + season + '_' + dom
else:
  rects = {}
  rects[season] = 111 # subplot location
  fig = PLT.figure(figsize=(10,6)) # optimized figure size for one subplot
  fig_filename = var + '_' + exp + '_bias_1panel_' + stat + '_' + dom

#fig.suptitle(var.title()+', ' + stat + ', ' +(exp+', '+dom).upper(), size='x-large') # Giving title for the entire canvas

fig.suptitle((dom).upper() + ' ' + var.upper()+' ' + stat.upper() + ' (' + exp.upper() +' CMIP5 R1)', size='x-large') # Giving title for the entire canvas

for season in seasons:
    all_mods = []
    for mod in mods:
        bias = float(dd['RESULTS'][mod]["defaultReference"]['r1i1p1']['global'][stat +'_xy_'+season])*unit_adj
        all_mods.append(bias)
    dia = BarChart(mods,all_mods,fig=fig, rect=rects[season])
    dia._ax.set_title(season.upper()) # Give title for individual subplot
    if season != seasons[-1]: # Hide x-axis labels for upper panels if plotting multiple panels
      dia._ax.axes.xaxis.set_ticklabels([])
      dia._ax.set_xlabel('')

if len(seasons) == 1:
  fig.subplots_adjust(bottom=0.3) # Give more bottom margins to model name show up

PLT.savefig(pathout + '/' + fig_filename + '.png')

if test:
    PLT.ion()
    PLT.show()

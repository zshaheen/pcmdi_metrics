
# coding: utf-8

# In[6]:

import vcs # For plots
import cdms2 # for data
import glob
import pcmdi_metrics
import os, glob
from parallel_coordinates_functions import *


# Read in data
json_pth = "/Users/jerome/Work/Evaluation/PCMDI-MP/CMIP5_results/v1.1/*.json"
json_files = glob.glob( json_pth )

# Read them in
J = pcmdi_metrics.pcmdi.io.JSONs(json_files)
## Add an IPSL file
ipsl_json_path = '/Users/jerome/Work/Evaluation/PCMDI-MP/Metrics/IGCM_OUT_model_not_defined_CM605-LR-pdCtrl-01_2060_2069/metrics_results/*.json'
ipsl_json_files = glob.glob( ipsl_json_path )
J2 = pcmdi_metrics.pcmdi.io.JSONs(ipsl_json_files)

# -- Rename with a user defined name
J3 = rename_top_key(J2, J2.data['pr'].keys()[0], 'CM605-LR-pdCtrl-01')

# -- Merge the JSONs objects
J_final = merge_JSONs_on_topkey(J,J3)

# -- Specify the metric to display (statistic, season, region)
metric = dict(statistic="bias_xy", season="ann", region='global')


#x.clear()
#show = VCSAddonsNotebook(x)
fig = plot_parallel_coordinates(J_final, metric, highlights=['IPSL-CM5A-LR','CM605-LR-pdCtrl-01','CNRM-CM5'], sort=True,
                          colors=['red', 'blue','green'], figwidth=1200, figheight=600,
                          plot_y1=.15, plot_y2=.85,
                          plot_x2=.6, legend_x1=.62, legend_x2=.97,
                          line_widths=[4.,4.,4.])

from IPython.display import Image
Image(fig)


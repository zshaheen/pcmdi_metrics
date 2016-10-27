#!/bin/python
import cdms2
import vcs
import pcmdi_metrics
import os, glob

import base64
import tempfile
from time import gmtime, strftime
class VCSAddonsNotebook(object):
    def __init__(self, x):
        self.x = x
    def _repr_png_(self):
        fnm = tempfile.mktemp()+".png"
        x.png(fnm)
        print 'Saved figure as '+fnm
        encoded = base64.b64encode(open(fnm, "rb").read())
        return encoded
    def __call__(self):
        return self


    
    
#for elt in J.getAxisList():
#    print elt.id
def rename_top_key(J,oldname,newname):
    from copy import deepcopy
    new_J = deepcopy(J)
    # Loop on the variables
    for variable in J.data.keys():
        # Loop on the models/simulations
        for model in J.data[variable]:
            # Find the model targeted by 'oldname'
            if model in oldname:
                tmp = new_J.data[variable][model].copy()
                # We now have to change the realization name so that
                # we only have one realization accross all the simulations
                # (the top key is the identifier)
                # Loop on the references
                for reference in tmp.keys():
                    if reference in ['defaultReference','alternate1','alternate2','alternate3']:
                        for realization in tmp[reference].keys():
                            if realization not in 'source' and len(tmp[reference].keys())<=2:
                                tmp2 = tmp[reference][realization].copy()
                                tmp[reference].update({'r1i1p1':tmp2})
                                tmp[reference].pop(realization)
                new_J.data[variable].update({newname:tmp})
                new_J.data[variable].pop(model)
    print 'Renamed '+oldname+' with '+newname
    return new_J
#

# Merge two Js
def merge_JSONs_on_topkey(J, J2):
    # Verifier la json_struct
    if J.json_struct == J2.json_struct:
        from copy import deepcopy
        J_final = deepcopy(J)
        variables = []
        for variable in J_final.data.keys():
            if variable in J2.data.keys():
                J_final.data[variable].update(J2.data[variable])
                variables.append(variable)
            else:
                J_final.data.pop(variable)
        J_final.getAxisList()
        for ind in xrange(len(J_final.axes)):
            if J_final.axes[ind].id in 'variable':
                J_final.axes[ind] = cdms2.createAxis(variables,id='variable')
            if J_final.axes[ind].id in 'model':
                J_final.axes[ind] = cdms2.createAxis(J_final.data[variables[0]].keys(),id='model')
        return J_final
    else:
        print "The JSONs objects have different structures - can not merge them"

#
import numpy
def sort_vert_axes(dat,variables,test_index,method='value_on_y_axis'):
    if method in 'value_on_y_axis':
        y_positions = []
        for var in xrange(len(variables)):
            var_values = dat.data[var,:]
            var_test = var_values[test_index]
            var_values = numpy.extract(var_values!=1e+20, var_values)
            var_min = var_values.min()
            var_max = var_values.max()
            y_position = (var_test - var_min) / (var_max - var_min)
            y_positions.append(y_position)
        y_positions = numpy.array(y_positions)
        sorted_index = numpy.argsort(y_positions)

        sorted_variables = []
        for ind in sorted_index:
            sorted_variables.append(variables[ind])
    return sorted_variables
#


def plot_parallel_coordinates(J, metric={}, variables = None, models=None, sort=False, highlights=None,
                              colors=None, title=None, line_widths=None,
                              figwidth = 1800, figheight=800, plot_x1=0.05, plot_x2=0.7, plot_y1=.15, plot_y2=.85,
                              titleFontSizeAdj=0,xlabelFontSizeAdj=0,ylabelFontSizeAdj=0,legendFontSizeAdj=0,
                              legend_x1=0.71, legend_x2=0.9, Notebook=True, **kwargs):

    if 'statistic' not in metric:
        metric.update(dict(statistic='rms_xyt'))
    if 'season' not in metric:
        metric.update(dict(season='ann'))
    if 'region' not in metric:
        metric.update(dict(statistic='global'))

    if not title:
        title = 'Parallel Coordinates '+metric['statistic']+' '+metric['season']+' '+metric['region']
    if not line_widths: line_widths = 2.
    if not isinstance(line_widths,list): line_widths=list(line_widths)
    #
    # Start with getting the metrics data (cdms2 object)
    input_dic_J = metric.copy()
    if variables: input_dic_J.update(dict(variable=variables))
    if models: input_dic_J.update(dict(model=models))
    # -- First, we get the list of simulation to sort them in alphabetical order
    tmp_metrics_dat = J(**input_dic_J)(squeeze=1)
    tmp_models = list(tmp_metrics_dat.getAxis(1).getValue())
    tmp_models.sort()
    # -- Then, we build a new metrics_dat cdms2 object from the JSONs object J
    input_dic_J.update(dict(model=tmp_models))
    metrics_dat = J(**input_dic_J)(squeeze=1)
    variables = list(metrics_dat.getAxis(0).getValue())
    all_models = list(metrics_dat.getAxis(1).getValue())
    #
    # If we want to highlight results
    if highlights:
        if not isinstance(highlights,list): highlights=list(highlights)
        ref_model=highlights[0]
        print ref_model+' is used as the reference model'
        if len(highlights)>1:
            test_model=highlights[1:len(highlights)-1]
        if colors:
            if not isinstance(colors,list): colors = list(colors)
            lines_colors = ['grey']*(len(all_models)-len(highlights)) + colors 
        #
        models = list(metrics_dat.getAxis(1).getValue())
        for highlight_model in highlights:
            models.pop(models.index(highlight_model))
        models = models + highlights
        # -- We do a new metrics_dat
        metrics_dat = J(model=models, **metric)(squeeze=1)
        if len(highlights)==len(line_widths): line_widths = [2.]*(len(models)-len(highlights)) + line_widths
    #
    # -- Sort the results by columns for the reference model
    if sort:
        #print 'len(list(metrics_dat.getAxis(1).getValue())) ',len(list(metrics_dat.getAxis(1).getValue()))
        sorted_variables = sort_vert_axes(metrics_dat, variables, list(metrics_dat.getAxis(1).getValue()).index(ref_model))
        metrics_dat = J(variable=sorted_variables, model=models, **metric)(squeeze=1)
    #
    # initialize a canvas
    x=vcs.init(geometry=(figwidth,figheight), bg=True)
    import vcsaddons
    gm = vcsaddons.createparallelcoordinates(x=x)

    # Prepare the graphics
    # Set variable name
    metrics_dat.id = title
    # Set units of each variables on axis
    #rms_xyt.getAxis(-2).units = ["mm/day","mm/day","hPa","W/m2","W/m2","W/m2", "K","K","K","m/s","m/s","m/s","m/s","m","m/s","m/s","m/s","m/s","m"]# Sets title on the variable
    metrics_dat.title = ""

    # Prepare the canvas areas
    t = vcs.createtemplate()
    # Create a text orientation object for xlabels
    tx=x.createtextorientation()
    tx.angle=-45
    tx.height+=8+xlabelFontSizeAdj
    tx.halign="right"
    # Tell template to use this orientation for x labels
    t.xlabel1.textorientation = tx
    # Y labels
    ty = x.createtextorientation()
    ty.height+=3+ylabelFontSizeAdj
    ty.halign="right"
    t.ylabel1.textorientation = ty
    # Title
    tti=x.createtextorientation()
    tti.height+=20+titleFontSizeAdj
    t.dataname.textorientation=tti


    # Define area where plot will be drawn in x direction
    t.reset('x',plot_x1,plot_x2,t.data.x1,t.data.x2)
    t.reset('y',plot_y1,plot_y2,t.data.y1,t.data.y2)
    #if plot_y1: t.data.y1 = plot_y1
    #if plot_y2: t.data.y2 = plot_y2
    ln = vcs.createline()
    
    # Turn off box around legend
    ln.color = [[0,0,0,0]]
    t.legend.line = ln
    # turn off box around data area
    t.box1.priority=0

    # Define box where legend will be drawn
    t.legend.x1 = legend_x1
    t.legend.x2 = legend_x2
    # use x/y of data drawn for legend height
    t.legend.y1 = t.data.y1
    t.legend.y2 = t.data.y2
    tl = x.createtextorientation()
    tl.height+=10+legendFontSizeAdj
    t.legend.textorientation = tl

    gm.linecolors = lines_colors
    gm.linestyles=["dot"]*len(models)
    gm.linewidths=line_widths
    gm.markercolors = lines_colors
    gm.markertypes=["dot"]*len(models)
    gm.markersizes=[2.]*len(models)
    
    
    x.clear()
    gm.plot(metrics_dat,template=t)
    fnm = tempfile.mktemp()+".png"
    x.png(fnm)
    print 'Saved figure as '+fnm
    
    if Notebook:
        return fnm
        
        
    


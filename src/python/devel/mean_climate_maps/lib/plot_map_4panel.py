import EzTemplate, vcs  


def plot_4panel(bg, mode, season, model, s1, s2, s3, s4, output_file_name, canvas=None):
#-------------------------------------------------------------------------------------------

  ## Input fields ---
  s = []
  s.append(s1)
  s.append(s2)
  s.append(s3)
  s.append(s4)

  ## Initialize VCS ---
  if canvas is None:
	    canvas = vcs.init(geometry=(1000,800),bg=bg) # Plotting in background mode

  #canvas.setcolormap('bl_to_darkred')




  plot_title.string = mode + ': ' + season
  canvas.plot(plot_title)

  # Plot subplots ---
  left_pos = 0
  for i in range(4):  
    t = M.get(legend='local',row=i/2,column=i%2,font=0) # Use local colorbar
    if i%2 !=1:  
      t.legend.priority=0 # Turn off legend  
      left_pos = t.data.x1
    else:
      # Set legend (colorbar) position
      t.legend.x1 = left_pos
      t.legend.x2 = t.data.x2
      t.legend.y1 = t.legend.y1 - 0.03
      t.legend.y2 = t.legend.y2 - 0.03
    #t.legend.y1 = t.legend.y1 - 0.03
    #t.legend.y2 = t.legend.y2 - 0.03

    #setup_template(t)

    if i < 2: 
      canvas.plot(s[i], t, iso)
    else:
      canvas.plot(s[i], t, iso_diff)

    # Titles of subplots ---
    plot_sub.height = 20
    if i == 0: 
      plot_sub.string = model # multi-realization mean...
      plot_sub.x = .27
      plot_sub.y = .91
    elif i == 1: 
      plot_sub.string = 'OBS'
      plot_sub.x = .73
      plot_sub.y = .91
    elif i == 2: 
      plot_sub.string = 'Diff: '+model+' - OBS'
      plot_sub.x = .27
      plot_sub.y = .48
    elif i == 3: 
      plot_sub.string = 'Diff: MMM - OBS'
      plot_sub.x = .73
      plot_sub.y = .48
    canvas.plot(plot_sub)
   
  #-------------------------------------------------
  # Drop output as image file (--- vector image?)
  #- - - - - - - - - - - - - - - - - - - - - - - - - 
  canvas.png(output_file_name+'.png')
  canvas.clear()


#===========================================================================================
def setup_template(t):
#-------------------------------------------------------------------------------------------
  # Turn off no-needed information -- prevent overlap
  t.blank(['title','mean','min','max','dataname','crdate','crtime',
           'units','zvalue','tvalue','xunits','yunits','xname','yname'])
  t.scalefont(.75)
  return

#===========================================================================================
def setup_iso(iso, diff):
#-------------------------------------------------------------------------------------------
  import vcs

  ## Setup color ---
  if not diff: 
    iso.colormap = 'bl_to_darkred'
    iso.colormap = 'default'
    iso.levels = [   1,  2,    3,    4,    5, 6,   7,   8,   9,  10,  11, 12, 14, 16, 18, 20, 22 ]
  else:
    iso.colormap = 'bl_to_drkorang'
    iso.levels = [-10, -9, -8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

  iso.ext_1 = 'y' # control colorbar edge (arrow extention on/off)
  iso.ext_2 = 'y' # control colorbar edge (arrow extention on/off)
  iso.missing = 'white'

  ## Map projection setup ---
  p = vcs.createprojection()
  p.type = 'mollweide'

  iso.projection = p
  return

#===========================================================================================
def label_setup(my_template):
#-------------------------------------------------------------------------------------------
  tick_text = vcs.createtext()
  tick_text.height = 22
  tick_text.valign = "half"
  tick_text.halign = "center"
  my_template.xlabel1.textorientation = tick_text.To_name
  my_template.xlabel1.texttable = tick_text.Tt_name

  tick_text2 = vcs.createtext()
  tick_text2.height = 22
  tick_text2.valign = "half"
  tick_text2.halign = "right"
  my_template.ylabel1.textorientation = tick_text2.To_name
  my_template.ylabel1.texttable = tick_text2.Tt_name

  tick_text3 = vcs.createtext()
  tick_text3.height = 25
  tick_text3.valign = "half"
  tick_text3.halign = "center"
  my_template.legend.textorientation = tick_text3.To_name
  my_template.legend.texttable = tick_text3.Tt_name
  return


iso = vcs.createisofill()
iso_diff = vcs.createisofill()
## iso setup ---
setup_iso(iso, diff=False)
setup_iso(iso_diff, diff=True)
my_template = vcs.createtemplate()
## Increase label text size ---
label_setup(my_template)
setup_template(my_template)
## EzTemplate ---
M = EzTemplate.Multi(template=my_template, rows=2,columns=2)  

# Legend colorbar ---
#M.legend.stretch = 1.5 # 150% of width (for middle one) --- in case use local legend
#M.legend.stretch = 0.8 # 150% of width (for middle one) --- in case use global legend
M.legend.thickness = 0.4 # Thickness of legend color bar
M.legend.direction = 'horizontal' 
#M.legend.direction = 'vertical' 

# Border margin for entire canvas ---
M.margins.top = .15
M.margins.bottom = .10
M.margins.left = .05  
M.margins.right = .05  

# Interval spacing between subplots ---
M.spacing.horizontal = .05
M.spacing.vertical = .10
#===========================================================================================
# Title on top ---
plot_title = vcs.createtext()
plot_title.x = .5
plot_title.y = .97
plot_title.height = 30
plot_title.halign = 'center'
plot_title.valign = 'top'
plot_title.color = 'black'

plot_sub = vcs.createtext(Tt_source=plot_title.Tt_name,To_source=plot_title.To_name)

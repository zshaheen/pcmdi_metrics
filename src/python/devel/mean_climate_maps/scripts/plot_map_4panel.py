#===========================================================================================
def plot_4panel(debug, mode, season, model, s1, s2, s3, s4, output_file_name, canvas=None):
#-------------------------------------------------------------------------------------------
  import EzTemplate, vcs  
  import string

  if debug is None:
    debug = True

  debug = False
  ## Input fields ---
  s = []
  s.append(s1)
  s.append(s2)
  s.append(s3)
  s.append(s4)

  ## Initialize VCS ---
  if canvas is None:
	  if debug:
	    canvas = vcs.init(geometry=(1000,800)) # Show canvas
	  else:
	    canvas = vcs.init(geometry=(1000,800),bg=1) # Plotting in background mode

  #canvas.setcolormap('bl_to_darkred')

  ## iso setup ---
  iso = canvas.createisofill()
  iso, xtra = setup_iso(mode, iso, diff=False)

  iso_diff = canvas.createisofill()
  iso_diff, xtra = setup_iso(mode, iso_diff, diff=True)

  ## Increase label text size ---
  my_template = vcs.createtemplate()
  my_template = label_setup(my_template)

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

  # Title on top ---
  plot_title = vcs.createtext()
  plot_title.x = .5
  plot_title.y = .97
  plot_title.height = 30
  plot_title.halign = 'center'
  plot_title.valign = 'top'
  plot_title.color = 'black'
  plot_title.string = mode + ': ' + season
  canvas.plot(plot_title)

  # Plot subplots ---
  left_pos = 0
  for i in range(4):  
    #t = M.get() # Use global colorbar
    t = M.get(legend='local') # Use local colorbar
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

    t = setup_template(t)

    if i < 2: 
      canvas.plot(s[i], t, iso)
    else:
      canvas.plot(s[i], t, iso_diff)

    # Titles of subplots ---
    plot_title.height = 20
    if i == 0: 
      plot_title.string = model # multi-realization mean...
      plot_title.x = .27
      plot_title.y = .91
    elif i == 1: 
      plot_title.string = 'OBS'
      plot_title.x = .73
      plot_title.y = .91
    elif i == 2: 
      plot_title.string = 'Diff: '+model+' - OBS'
      plot_title.x = .27
      plot_title.y = .48
    elif i == 3: 
      plot_title.string = 'Diff: MMM - OBS'
      plot_title.x = .73
      plot_title.y = .48
    canvas.plot(plot_title)
   
  #-------------------------------------------------
  # Drop output as image file (--- vector image?)
  #- - - - - - - - - - - - - - - - - - - - - - - - - 
  canvas.png(output_file_name+'.png')

# if not debug:
# canvas.close()
  canvas.clear()


#===========================================================================================
def setup_template(t):
#-------------------------------------------------------------------------------------------
  # Turn off no-needed information -- prevent overlap
  t.blank(['title','mean','min','max','dataname','crdate','crtime',
           'units','zvalue','tvalue','xunits','yunits','xname','yname'])
  return(t)

#===========================================================================================
def setup_iso(mode, iso, diff):
#-------------------------------------------------------------------------------------------
  import string
  import vcs

  ## Setup color ---
  if not diff: 
    iso.colormap = 'bl_to_darkred'
    iso.colormap = 'default'
    #iso.levels = [-0.5, -0.4, -0.3, -0.2, -0.1, 0, 0.1, 0.2, 0.3, 0.4, 0.5]
    iso.levels = [   1,  2,    3,    4,    5, 6,   7,   8,   9,  10,  11, 12, 14, 16, 18, 20, 22 ]
  else:
    iso.colormap = 'bl_to_drkorang'
    #iso.levels = [-10, -8, -6, -4, -2, 0, 2, 4, 6, 8, 10]
    iso.levels = [-10, -9, -8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    #iso.colormap = 'grn_to_magenta'
    #iso.colormap = 'bl_to_darkred'

  #if string.split(mode,'_')[0] == 'PDO':
  #  iso.levels = [-0.5, -0.4, -0.3, -0.2, -0.1, 0, 0.1, 0.2, 0.3, 0.4, 0.5]
  #else:
  #  iso.levels = [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]
  iso.ext_1 = 'y' # control colorbar edge (arrow extention on/off)
  iso.ext_2 = 'y' # control colorbar edge (arrow extention on/off)
  #cols = vcs.getcolors(iso.levels)
  #cols[6] = 139 # Adjsut to light red
  #iso.fillareacolors = cols
  #iso.missing = 0
  iso.missing = 'white'

  ## Map projection setup ---
  p = vcs.createprojection()
  #if mode == 'NAM' or mode == 'SAM':
  #  p.type = int('-3')
  #elif mode == 'NAO' or mode == 'PNA' or mode == 'PDO' or mode == 'AMO':
  #  p.type = 'lambert'
  #elif mode == 'PDO_teleconnection' or mode == 'PDO_pseudo_teleconnection':
  #  p.type = 'robinson'
  #else:
  #  p.type = int('-3')
  p.type = 'robinson'
  p.type = 'mollweide'

  iso.projection = p
 

  xtra = {}
  #if mode == 'PDO_teleconnection' or mode == 'PDO_pseudo_teleconnection':
  #  xtra = {}
  #elif mode == 'SAM' or mode == 'SAM_teleconnection' or mode == 'SAM_pseudo_teleconnection':
  #  xtra['latitude'] = (-90.0,0.0) # For Southern Hemisphere
  #else:
  #  xtra['latitude'] = (90.0,0.0) # For Northern Hemisphere

  return(iso, xtra)

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

  return(my_template)

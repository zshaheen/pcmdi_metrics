def write_nc_output(output_file_name,eof1,pc1,frac1):
  import cdms2 as cdms
  fout = cdms.open(output_file_name+'.nc','w')
  fout.write(eof1,id='eof1')
  fout.write(pc1,id='pc1')
  fout.write(frac1,id='frac1')
  fout.close()

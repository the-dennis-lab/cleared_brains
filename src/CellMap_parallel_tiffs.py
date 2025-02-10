#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CellMap
=======

This script is the main pipeline to analyze immediate early gene expression 
data from iDISCO+ cleared tissue [Renier2016]_.

See the :ref:`CellMap tutorial </CellMap.ipynb>` for a tutorial and usage.


.. image:: ../Static/cell_abstract_2016.jpg
   :target: https://doi.org/10.1016/j.cell.2020.01.028
   :width: 300

.. figure:: ../Static/CellMap_pipeline.png

  iDISCO+ and ClearMap: A Pipeline for Cell Detection, Registration, and 
  Mapping in Intact Samples Using Light Sheet Microscopy.


References
----------
.. [Renier2016] `Mapping of brain activity by automated volume analysis of immediate early genes. Renier* N, Adams* EL, Kirst* C, Wu* Z, et al. Cell. 2016 165(7):1789-802 <https://doi.org/10.1016/j.cell.2016.05.007>`_
"""
__author__    = 'Christoph Kirst <christoph.kirst.ck@gmail.com>'
__license__   = 'GPLv3 - GNU General Pulic License v3 (see LICENSE)'
__copyright__ = 'Copyright © 2020 by Christoph Kirst'
__webpage__   = 'http://idisco.info'
__download__  = 'http://www.github.com/ChristophKirst/ClearMap2'

if __name__ == "__main__":
     
  #%%############################################################################
  ### Initialization 
  ###############################################################################
  
  #%% Initialize workspace
  import sys, os, h5py
  import tifffile as tif
  import numpy as np

  if len(sys.argv) <3:
      print('ERROR: you entered {} and we require three strings: a directory, expression_raw string, and key name'.format(len(sys.argv)))
  else:
      directory = str(sys.argv[1]); print('using directory: ',directory)
      expression_raw = str(sys.argv[2]); print('using expression str',expression_raw)
      keyval = str(sys.argv[3]);print('using key ',keyval)
      keyintval = int(keyval.split('s')[1])

  #directories and files
  subdirectory = os.path.join(directory,'tiffs')
  print(os.path.isdir(subdirectory))

  if not os.path.isdir(subdirectory):
      os.mkdir(subdirectory)
  from numpy.lib.format import open_memmap

  # get the number of tiffs (z planes) for each key
  if str.split(expression_raw,'.')[1] == 'h5':
      print('converting h5 to tiffs for processing')
      with h5py.File(os.path.join(directory,expression_raw),'r') as infile:
          shapeval=0
          shapelist=[0]
          keylist=[key for key in infile.keys() if 's' in key]
          for key in keylist:
              dset=infile['t00000'][key]['0']['cells']
              dtype=dset.dtype
              shapeval+=int(dset.shape[0])
              shapelist.append(shapeval)

          # we want to start the tiff number
          start=shapelist[keyintval]
          dset = infile['t00000'][keyval]['0']['cells']
          print('on key ',keyval)
          for dsetstart in range(0,dset.shape[0]):
                  if start%20==0:
                      print('on tiff',start)
                  if not os.path.isfile(os.path.join(subdirectory,f"tiffs{start:04d}.tif")):
                      tif.imsave(os.path.join(subdirectory,f"tiffs{start:04d}.tif"),np.squeeze(dset[dsetstart:dsetstart+1]))
                  start+=1
	  np.save(os.path.join(directory,'tiff_stack_sizes.npy'),np.array(np.shape(np.squeeze(dset[dsetstart:dsetstart+1])),start))

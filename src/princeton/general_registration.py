#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 20240502
@author: emilyjanedennis
PURPOSE: to align a moving volume (or volumes) to a fixed volume
INPUTS:
	1. mvtiff: a string containing a full path
	2. fxtiff: a string containing a full path to a tiff file that you'd like to align the [mvtiffs] to
	3. output_dir: a string pointing to a full path where you'd like the outputs saved
OPTIONAL INPUTS:
	4. parameter_folder, this will default to ../parameter_folder (1 affine, 3 bsplines)
OUTPUTS:
	1. tiffile of transformed image
	2. transform file
	both are saved in argument 3, output_dir
"""

import os,sys,cv2, itk
from datetime import datetime
import numpy as np
from scipy.ndimage import zoom
import tifffile as tif

if __name__ == "__main__":

	if len(sys.argv) >= 4:
		if os.path.exists(sys.argv[1]):
			try:
				print('opening first tif, zooming 1.4x')
				# we found that a 140% sized image empirically produces better alignments
				mvtiff = zoom(itk.imread(sys.argv[1]),1.4)
				mv_basename = sys.argv[1].split('/')[-1].split('.')[0]
			except:
				print('ERROR: you entered {} for the first argument, which is not an image file'.format(sys.argv[1]))
		else:
			print('ERROR, you entered {} for the first argument, and the path does not exist'.format(sys.argv[1]))
		if os.path.exists(sys.argv[2]):
			try:
				print('opening fixed image tif')
				fxtiff = itk.imread(sys.argv[2])
				fx_basename = sys.argv[2].split('/')[-1].split('.')[0]
			except:
				print('ERROR: you entered {} for the second argument, which is not an image file'.format(sys.argv[2]))
		else:
			print('ERROR, you entered {} for the second argument, and the path does not exist'.format(sys.argv[2]))
		if os.path.isdir(sys.argv[3]):
			output_dir = sys.argv[3]
			subdir = os.path.join(output_dir,'{}_to_{}'.format(mv_basename,fx_basename))
			os.mkdir(subdir)
		else:
			print('ERROR, you entered {} for the third argument, and the path does not exist'.format(sys.argv[2]))
	else:
		print('ERROR: this script requires three input arguments: \n 1. a path to the moving image \n 2. a path to the fixed image and \n 3. a path to a directory where you would like to save the results')
	if len(sys.argv) > 4:
		if os.path.exists(sys.argv[4]):
			param_file_fld = sys.argv[4]
		else:
			print(' you entered {} for the optional fourth argument, but the path does not exist. \n USING DEFAULT PARAM FILES'.format(param_file_fld))
			param_file_fld='../parameter_folder'
	else:
		param_file_fld = '../parameter_folder'
	param_files = [os.path.join(param_file_fld,file) for file in os.listdir(param_file_fld) if ".txt" in file]
	param_files.sort()
	print('param files are:',param_files)
	parameter_object = itk.ParameterObject.New()
	for file in param_files:
		parameter_object.AddParameterFile(file)

	# run elastix, this can take some time
	print('running elastix, starting at {}, this can take some time!'.format(datetime.now()))
	result_img_elx, result_transform_params = itk.elastix_registration_method(fxtiff,mvtiff,parameter_object,log_to_file=True,output_directory=subdir)
	print('finished running elastix at {}, now saving out files'.format(datetime.now()))
	tif.imsave(os.path.join(subdir,'{}_to_{}.tif'.format(mv_basename,fx_basename)),result_img_elx)

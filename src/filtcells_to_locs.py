#!/usr/bin/env python3
"""
created 20250204
@author emilyjanedennis
PURPOSE
INPUTS
OPTIONAL INPUTS
OUTPUTS
"""

import os,sys,h5py
import numpy as np
import pandas as pd

if __name__ == "__main__":


	#first, deal with inputs
	if len(sys.argv) < 2:
		print('this requires at minimum one input: a full path to a folder with a tiffs/cells_filtered.py file')
	else:
		filepath=os.path.join(sys.argv[1],"tiffs/cells_filtered.npy")
		print('working on {}'.format(filepath))

	try:
		cells = np.load(filepath)
	except:
		if os.path.isfile(sys.argv[1]):
			print('cannot open file, check filepath: {}'.format(filepath))
		else:
			print('full path does not lead to a file, check filepath: {}'.format(filepath))

	print('max dims are: {}x {}y {}z'.format(np.max(cells['x']),np.max(cells['y']),np.max(cells['z'])))
	df_cells = pd.DataFrame(cells[['x','y','z']])

	directory=os.path.dirname(os.path.dirname(filepath))
	outputdir = os.path.join(directory,'outputs')
	if not os.path.isdir(outputdir):
		outputdir = os.mkdir(outputdir)

	# following section fails DRY, TODO: to fix DRY fail, save out these shapes when creating tiffs
	# look at the .h5 file, get the data for each key (s00,s01,s02...) and 
	# use that to subset the cells info into csvs split by key for bigstitcher spark transform
	with h5py.File(os.path.join(directory,"dataset.h5"),'r') as infile:
		shapeval=0
		shapelist=[0]
		keylist=[key for key in infile.keys() if 's' in key]
		for key in keylist:
			dset = infile['t00000'][key]['0']['cells']
			dtype=dset.dtype
			shapeval+=int(dset.shape[2])
			shapelist.append(shapeval)
			subdf = df_cells[(df_cells.z>=shapelist[-2])&(df_cells.z<shapelist[-1])]
			subdf.z=subdf.z-shapelist[-2]
			subdf.to_csv(os.path.join(outputdir,"{}_filtered_cells.csv".format(key)),header=False,index=False)

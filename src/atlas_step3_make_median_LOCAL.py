#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 16 13:49:34 2019

@author: wanglab
"""

import os, tifffile, cv2, numpy as np, multiprocessing as mp, sys, shutil, subprocess as sp
from scipy.ndimage import zoom
sys.path.append("..")
from tools.imageprocessing.orientation import fix_orientation

def listdirfull(x, keyword=False):
    """
    lists all contents of a directory by joining all paths
    """
    if not keyword:
        lst = [os.path.join(x, xx) for xx in os.listdir(x) if xx[0] != "." and "~" not in xx and "Thumbs.db" not in xx]
    else:
        lst = [os.path.join(x, xx) for xx in os.listdir(x) if xx[0] != "." and "~" not in xx and "Thumbs.db" not in xx and keyword in xx]

    lst.sort()
    return lst


def load_memmap_arr(pth, mode="r", dtype = "uint16", shape = False):
    """
    Function to load memmaped array.

    Inputs
    -----------
    pth: path to array
    mode: (defaults to r)
    +------+-------------------------------------------------------------+
    | "r"  | Open existing file for reading only.                        |
    +------+-------------------------------------------------------------+
    | "r+" | Open existing file for reading and writing.                 |
    +------+-------------------------------------------------------------+
    | "w+" | Create or overwrite existing file for reading and writing.  |
    +------+-------------------------------------------------------------+
    | "c"  | Copy-on-write: assignments affect data in memory, but       |
    |      | changes are not saved to disk.  The file on disk is         |
    |      | read-only.                                                  |
    dtype: digit type
    shape: (tuple) shape when initializing the memory map array

    Returns
    -----------
    arr
    """
    if shape:
        assert mode =="w+", "Do not pass a shape input into this function unless initializing a new array"
        arr = np.lib.format.open_memmap(pth, dtype = dtype, mode = mode, shape = shape)
    else:
        arr = np.lib.format.open_memmap(pth, dtype = dtype, mode = mode)
    return arr

def elastix_command_line_call(fx, mv, out, parameters, fx_mask=False, verbose=False):
    """
    Wrapper Function to call elastix using the commandline, this can be time consuming

    Inputs
    -------------------
    fx = fixed path (usually Atlas for "normal" noninverse transforms)
    mv = moving path (usually volume to register for "normal" noninverse transforms)
    out = folder to save file
    parameters = list of paths to parameter files IN ORDER THEY SHOULD BE APPLIED
    fx_mask= (optional) mask path if desired

    Outputs
    --------------
    ElastixResultFile = ".tif" or ".mhd" result file
    TransformParameterFile = file storing transform parameters

    """
    e_params=["elastix", "-f", fx, "-m", mv, "-out", out]
    if fx_mask: e_params=["elastix", "-f", fx, "-m", mv, "-fMask", fx_mask, "-out", out]

    ###adding elastix parameter files to command line call
    for x in range(len(parameters)):
        e_params.append("-p")
        e_params.append(parameters[x])

    #set paths
    TransformParameterFile = os.path.join(out, "TransformParameters.{}.txt".format((len(parameters)-1)))
    ElastixResultFile = os.path.join(out, "result.{}.tif".format((len(parameters)-1)))

    #run elastix:
    try:
        if verbose: print ("Running Elastix, this can take some time....\n")
        sp.call(e_params)
        if verbose: print("Past Elastix Commandline Call")
    except RuntimeError as e:
        print("\n***RUNTIME ERROR***: {} Elastix has failed. Most likely the two images are too dissimiliar.\n".format(e.message))
        pass
    if os.path.exists(ElastixResultFile) == True:
        if verbose: print("Elastix Registration Successfully Completed\n")
    #check to see if it was MHD instead
    elif os.path.exists(os.path.join(out, "result.{}.mhd".format((len(parameters)-1)))) == True:
        ElastixResultFile = os.path.join(out, "result.{}.mhd".format((len(parameters)-1)))
        if verbose: print("Elastix Registration Successfully Completed\n")
    else:
        print ("\n***ERROR***Cannot find elastix result file, try changing parameter files\n: {}".format(ElastixResultFile))
        return


    return ElastixResultFile, TransformParameterFile

def generate_median_image(output_folder, parameters, memmappth, dst, brains, verbose = True):
    """
    Function to collect post-registered volumes, generate a memory mapped array and then save out median volume
    """

    if verbose: sys.stdout.write("Collecting data and generating memory mapped array"); sys.stdout.flush()
    nm = "result.{}.tif".format(len(parameters)-1)
    vol = tifffile.imread(brains[0])
    z,y,x = vol.shape
    dtype = vol.dtype

    #init array
    arr = load_memmap_arr(memmappth, mode="w+", shape = (len(brains),z,y,x), dtype = dtype)

    #load
    for i, brain in enumerate(brains):
        arr[i] = tifffile.imread(brain)
        arr.flush()
    if dst[-4:] != ".tif": dst = dst+".tif"
    if verbose: sys.stdout.write("...completed\nTaking median and saving as {}".format(dst)); sys.stdout.flush()

    #median volume
    vol = np.median(arr, axis=0)
    tifffile.imsave(dst, vol.astype(dtype))
    if verbose: sys.stdout.write("...completed"); sys.stdout.flush()
    return


if __name__ == "__main__":

    #print(os.environ["SLURM_ARRAY_TASK_ID"])
    #jobid = int(os.environ["SLURM_ARRAY_TASK_ID"])
    output_fld = "/home/emilyjanedennis/Desktop/PRA_f_out"

    seed = "/home/emilyjanedennis/Desktop/for_registration_to_lightsheet/tiffs/PRAf_seed2.tif"
    #Location to make a memory mapped array
    memmappth = os.path.join(output_fld, "PRAfseed3_memmap.npy")
    #Location to save out our atlas (median image)
    final_output_path = "/home/emilyjanedennis/Desktop/for_registration_to_lightsheet/tiffs/PRAf_seed4.tif"

    #run registration
    #make output folder:
    #find all brains
    brain_list = ["f002","f003","f110","k320","k321","k323","k327","t107"]
    data_fld = "/home/emilyjanedennis/Desktop/PRA_f_out"
    brains = []
    for i in np.arange(0,len(brain_list)):
        brains.append(os.path.join(data_fld,brain_list[i],"result.3.tif"))
    parameters = "/home/emilyjanedennis/Desktop/GitHub/parameterfolder"
    #RUN AFTER ALL REGISTERATIONS ARE COMPLETE (locally or on head node, do not need a job for this)
    generate_median_image(output_fld, parameters, memmappth, final_output_path, brains, verbose = True)

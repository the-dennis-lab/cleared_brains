import sys, os, glob
import tifffile as tif
import numpy as np
from scipy.ndimage import zoom

if __name__ == "__main__":

        if len(sys.argv) < 3:
                print('this script requires at minimum two inputs: a full path to a folder containing tiffs and a full path to an existing location where you want the resulting stack saved')
                sys.exit(1)
        else:
                fld_of_tiffs = sys.argv[1]
                file_to_save = sys.argv[2]
                if not os.path.isdir(fld_of_tiffs):
                        print('the first argument should be a full path to a folder with tiffs, not {}'.format(fld_of_tiffs))
                        sys.exit(1)
                elif os.path.isfile(file_to_save):
                        print('file already exists! delete or input a different name than {}'.format(file_to_save))
                        sys.exit(1)
                elif not os.path.isdir(os.path.dirname(file_to_save)):
                        print('directory does not exist for stack path, please ensure the path exists: {}'.format(os.path.dirname(file_to_save)))
                        sys.exit(1)
        tiff_paths = sorted(glob.glob(os.path.join(fld_of_tiffs, "*.ti*")))
        print(len(tiff_paths))
        if len(tiff_paths) < 1:
                print("no tiffs found! check folder {}".format(fld_of_tiffs))
                sys.exit(1)
        else:
                print("found {len(tiff_paths)} files")
        images = [tif.imread(p) for p in tiff_paths]
        dtype = images[0].dtype

        max_h = max(img.shape[0] for img in images)
        max_w = max(img.shape[1] for img in images)
        n_slices = len(images)

        padded = np.zeros((2400,1600,1600),dtype=dtype)
        for i, img in enumerate(images):
                padded[i,0:max_h,0:max_w] = img

        downsized = zoom(padded, zoom=(0.2, 0.2, 0.2), order=1)

        print("final stack shape: {}".format(np.shape(downsized)))
        tif.imwrite(file_to_save,downsized)
        print("saved {file_to_save}")



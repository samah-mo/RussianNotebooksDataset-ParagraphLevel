import glob
import shutil
import os.path as path
import os

source_folder = "output_val/"
distanation_folder = "train_and_validatio_Russian_notebooks/validation/"
images_folder = "images/"
# os.mkdir(path.join(distanation_folder, "page/"))
# os.mkdir(path.join(distanation_folder, "images/"))
files = sorted(glob.glob(source_folder + "*.xml"))
for file in files:
  image_file = glob.glob(images_folder + path.basename(file)[:-3] + "*")[0]
  shutil.copy(file, path.join(distanation_folder, "page/"))
  shutil.copy(image_file, path.join(distanation_folder, "page/"))
  shutil.copy(image_file, path.join(distanation_folder, "images/"))
print(files)
print(len(files))
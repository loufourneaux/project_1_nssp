import os
from tqdm import tqdm
import subprocess
from fsl.wrappers import mcflirt, fslmaths, fslmerge

# Set directories
data_dir = 'gdrive_ds000171/sub-control01'  #change to you data folder
output_dir_anat = 'sub_control01_preprocessed/anat'
output_dir_func = 'sub_control01_preprocessed/func'
subject_id = 'sub-control01'


# List of runs
runs = [
    'sub-control01_task-music_run-1_bold',
    'sub-control01_task-music_run-2_bold',
    'sub-control01_task-music_run-3_bold'
]

# Create output directories if they don't exist
os.makedirs(output_dir_anat, exist_ok=True)
os.makedirs(output_dir_func, exist_ok=True)

# Step 1: Standardization of Each Run
standardized_output_dir = os.path.join(output_dir_func, 'standardized')
os.makedirs(standardized_output_dir, exist_ok=True)
for run in tqdm(runs, desc="Standardization"):
    func_file = os.path.join(data_dir, 'func', f'{run}.nii.gz')
    standardized_output_path = os.path.join(standardized_output_dir, f'{run}_standardized.nii.gz')
    
    if os.path.exists(standardized_output_path):
        print(f"Standardized file already exists for {run}")
        continue

    fslmaths(func_file).inm(1).run(standardized_output_path)

# Step 2: Concatenate Standardized Runs
concat_output_path = os.path.join(output_dir_func, 'concatenated_standardized.nii.gz')
if not os.path.exists(concat_output_path):
    standardized_files = [os.path.join(standardized_output_dir, f'{run}_standardized.nii.gz') for run in runs]
    fslmerge('t', concat_output_path, *standardized_files)
else:
    print("Concatenated file already exists")

# Preprocessing on the Concatenated File
# Step 3: Motion Correction with Reference to First Volume of First Run
mc_output_path = os.path.join(output_dir_func, 'concatenated_standardized_mc.nii.gz')
if not os.path.exists(mc_output_path):
    first_volume_reference = os.path.join(data_dir, 'func', f'{runs[0]}.nii.gz')
    print("Running motion correction on concatenated file with reference to the first volume...")
    mcflirt(infile=concat_output_path, refvol=0, o=mc_output_path, plots=True, mats=True, dof=6)

# Step 4: Spatial Smoothing on mc file
smoothed_output_path = os.path.join(output_dir_func, 'concatenated_standardized_mc_smoothed.nii.gz')
if not os.path.exists(smoothed_output_path):
    print("Running spatial smoothing with 4mm Gaussian kernel...")
    fslmaths(mc_output_path).s(4/2.3458).run(smoothed_output_path)


# Step 5: Identify Signal Artifacts
outliers_output_path = os.path.join(output_dir_func, 'motion_outliers.txt')
outlier_metric_output_path = os.path.join(output_dir_func, 'motion_metric.txt')
outlier_pic_output_path = os.path.join(output_dir_func, 'motion_metric.png')
if not os.path.exists(outliers_output_path):
    print("Identifying volumes with excessive motion or signal artifacts...")
    subprocess.run(f"fsl_motion_outliers  -i {concat_output_path} -o {outliers_output_path} -s {outlier_metric_output_path} -p {outlier_pic_output_path} --dvars ", shell=True)


print("Preprocessing completed!")
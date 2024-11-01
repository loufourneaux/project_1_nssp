import os
import subprocess
from tqdm import tqdm
from fsl.wrappers import mcflirt, flirt, fslmaths, fslmerge, epi_reg

# Set directories
data_dir = 'gdrive_ds000171/sub-control01'  
output_dir_anat = 'sub_control01_preprocessed/anat'
output_dir_func = 'sub_control01_preprocessed/func'
subject_id = 'sub-control01'
mni_template= '/Users/loufourneaux/fsl/data/standard/MNI152_T1_1mm_brain.nii.gz' #change to your fsl path

# List of runs
runs = [
    'sub-control01_task-music_run-1_bold',
    'sub-control01_task-music_run-2_bold',
    'sub-control01_task-music_run-3_bold'
]

# Create output directories if they don't exist
os.makedirs(output_dir_anat, exist_ok=True)
os.makedirs(output_dir_func, exist_ok=True)

# Step 1: Skull Stripping for epi_reg
anat_file = os.path.join(data_dir, 'anat', f'{subject_id}_T1w.nii.gz')
bet_output_path = os.path.join(output_dir_anat, f'{subject_id}_T1w_bet.nii.gz')
#bet_mask_path = os.path.join(output_dir_anat, f'{subject_id}_T1w_bet_mask.nii.gz')

if not os.path.exists(bet_output_path):# or not os.path.exists(bet_mask_path):
    print("Running skull stripping...")
    subprocess.run(f"bet {anat_file} {bet_output_path}", shell=True)
else:
    print("Skull stripped files already exist.")

# Step1.1: Registration to MNI space
anat_to_mni_output = os.path.join(output_dir_anat, 'T1_to_MNI.nii.gz')
anat_to_mni_matrix = os.path.join(output_dir_anat, 'T1_to_MNI.mat')
if not os.path.exists(anat_to_mni_output):
    print("Normalizing anatomical to MNI space...")
    flirt(src=bet_output_path, ref=mni_template, omat=anat_to_mni_matrix, out=anat_to_mni_output)
else:
    print("Anatomical normalization to MNI space already exists.")

# Step 2: Standardization of Each Run
standardized_output_dir = os.path.join(output_dir_func, 'standardized')
os.makedirs(standardized_output_dir, exist_ok=True)
for run in tqdm(runs, desc="Standardization"):
    func_file = os.path.join(data_dir, 'func', f'{run}.nii.gz')
    standardized_output_path = os.path.join(standardized_output_dir, f'{run}_standardized.nii.gz')
    
    if os.path.exists(standardized_output_path):
        print(f"Standardized file already exists for {run}")
        continue

    fslmaths(func_file).inm(1).run(standardized_output_path)

# Step 3: Concatenate Standardized Runs
concat_output_path = os.path.join(output_dir_func, 'concatenated_standardized.nii.gz')
if not os.path.exists(concat_output_path):
    standardized_files = [os.path.join(standardized_output_dir, f'{run}_standardized.nii.gz') for run in runs]
    fslmerge('t', concat_output_path, *standardized_files)
else:
    print("Concatenated file already exists")

# Preprocessing on the Concatenated File
# Step 4: Motion Correction with Reference to First Volume of First Run
mc_output_path = os.path.join(output_dir_func, 'concatenated_standardized_mc.nii.gz')
if not os.path.exists(mc_output_path):
    first_volume_reference = os.path.join(data_dir, 'func', f'{runs[0]}.nii.gz')
    print("Running motion correction on concatenated file with reference to the first volume...")
    mcflirt(infile=concat_output_path, refvol=0, o=mc_output_path, plots=True, mats=True, dof=6)

# Step 4.1: Atlas coregistration with epi_reg
normalized_output_path = os.path.join(output_dir_func, 'concatenated_standardized_mc_coreg.nii.gz')
if not os.path.exists(normalized_output_path):
    print("Running atlas coregistration with epi_reg...")
    epi_reg(
        epi=mc_output_path,
        t1=anat_file,
        t1brain=bet_output_path,
        out=normalized_output_path
    )
'''
# Step 5: Identify and Censor Motion and Signal Artifacts
outliers_output_path = os.path.join(output_dir_func, 'motion_outliers.txt')
outlier_metric_output_path = os.path.join(output_dir_func, 'motion_metric.txt')
outlier_pic_output_path = os.path.join(output_dir_func, 'motion_metric.png')
if not os.path.exists(outliers_output_path):
    print("Identifying volumes with excessive motion or signal artifacts...")
    subprocess.run(f"fsl_motion_outliers -s {outlier_metric_output_path} -p {outlier_pic_output_path} --thresh=0.5 --nomoco", shell=True)
'''

# Step 6: High-Pass Temporal Filtering
highpass_output_path = os.path.join(output_dir_func, 'concatenated_standardized_mc_coreg_highpassed.nii.gz')
if not os.path.exists(highpass_output_path):
    print("Running high-pass temporal filtering...")
    fslmaths(normalized_output_path).bptf(50, -1).run(highpass_output_path)

# Step 7: Spatial Smoothing
smoothed_output_path = os.path.join(output_dir_func, 'concatenated_standardized_mc_coreg_highpassed_smoothed.nii.gz')
if not os.path.exists(smoothed_output_path):
    print("Running spatial smoothing with 4mm Gaussian kernel...")
    fslmaths(highpass_output_path).s(4).run(smoothed_output_path)



print("Preprocessing completed!")

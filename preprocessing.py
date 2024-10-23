import os
from tqdm import tqdm  # For progress bar
from fsl.wrappers import mcflirt, bet, fslmaths, fslmerge

# Set directories
data_dir = 'gdrive_ds000171/sub-control01'  
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

# Skull stripping using BET
run_file_path = os.path.join(data_dir, 'anat', f'{subject_id}_T1w.nii.gz')
bet_output_path = os.path.join(output_dir_anat, f'{subject_id}_T1w_bet.nii.gz')
bet_mask_path = os.path.join(output_dir_anat, f'{subject_id}_T1w_bet_mask.nii.gz')

# Check if the output files already exist
if os.path.exists(bet_output_path) and os.path.exists(bet_mask_path):
    print(f"Skull stripped files already exist: {bet_output_path}, {bet_mask_path}")
#else:
    # Skull stripping using BET
    #bet(infile=run_file_path, out=bet_output_path, mask=bet_mask_path)

# Motion correction using MCFLIRT
for run in tqdm(runs, desc="Motion correction: "):
    run_file_path = os.path.join(data_dir, 'func', f'{run}.nii.gz')
    mcflirt_output_path = os.path.join(output_dir_func, f'{run}_mc')
    
    # Check if the output file already exists
    if os.path.exists(f'{run}_mc.nii.gz') and os.path.exists(f'{run}_mc.par') and os.path.isdir(f'{run}_mc.mat'):
        print(f"Motion corrected file already exists for {run}")
        continue

    # Motion correction command
    mcflirt(infile=run_file_path, o=mcflirt_output_path, plots=True, mats=True, dof=6)

# Standardization using fslmaths
for run in tqdm(runs, desc="Standardization: "):
    run_file_path = os.path.join(output_dir_func, f'{run}_mc.nii.gz')
    standardized_output_path = os.path.join(output_dir_func, f'{run}_standardized.nii.gz')
    
    # Check if the output file already exists
    if os.path.exists(standardized_output_path):
        print(f"Standardized file already exists for {run}")
        continue

    # Standardization command
    fslmaths(run_file_path).inm(1).run(standardized_output_path)

# Smoothing using FSL's fslmaths
for run in tqdm(runs, desc="Smoothing"):
    standardized_file_path = os.path.join(output_dir_func, f'{run}_standardized.nii.gz')
    smoothed_output_path = os.path.join(output_dir_func, f'{run}_smoothed.nii.gz')
    
    # Check if the output file already exists
    if os.path.exists(smoothed_output_path):
        print(f"Smoothed file already exists for {run}")
        continue

    # Smoothing command (with a kernel size of 5mm as an example)
    fslmaths(standardized_file_path).s(5).run(smoothed_output_path)

# Concatenation of smoothed runs
concat_output_path = os.path.join(output_dir_func, 'concatenated_smoothed.nii.gz')
if os.path.exists(concat_output_path):
    print(f"Concatenated file already exists")
else:
    # Command to concatenate all smoothed files
    smoothed_files = [os.path.join(output_dir_func, f'{run}_smoothed.nii.gz') for run in runs]
    fslmerge('t', concat_output_path, *smoothed_files)

print("Preprocessing completed!")

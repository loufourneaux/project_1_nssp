import pandas as pd

def load_mot_params_fsl_6_dof(path):
    return pd.read_csv(path, sep='  ', header=None, engine='python',
    names=['Rotation X', 'Rotation Y', 'Rotation Z', 'Translation X', 'Translation Y', 'Translation Z'] )



def compute_FD_power(mot_params):
    framewise_diff= mot_params.diff().iloc[1:]
    rot_params=framewise_diff[['Rotation X', 'Rotation Y', 'Rotation Z']]
    converted_rots= rot_params*50
    trans_params=framewise_diff[['Translation X', 'Translation Y', 'Translation Z']]
    fd=converted_rots.abs().sum(axis=1)+trans_params.abs().sum(axis=1)
    return fd 
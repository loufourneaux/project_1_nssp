# project_1_nssp
Study of the neural processing of emotionally provocative auditory stimuli. Specifically you want to figure out what regions of the brain are activated when subjects are listening to positive compared to negative emotional musical and nonemotional - nonmusical stimuli (pure neutral tones) during fMRI scanning.

## Dataset
In this dataset, participants listened in blocks of 33 seconds to positive or negative music. Music blocks were interleaved with 33 seconds of pure tone listening, following the paradigm described in Lepping, et al., 2015 (see Fig.1 of bibliographical reference [1]). The last 3 seconds of each musical block was used to make sure participants were paying attention, where they had to press a button to indicate if they found the samples to be positive or negative.

## Dependencies 
nipype
nilearn



# Preprocessing
BET: skull stripping?? -> bc no registration to MNI space needed i don't think necessary 
FAST: tissue segmentation -> useful bc want to look at specific areas for our study
MCFLIRT: motion correction
standardize: for camparision and concatenation
SUSAN: spatial smoothing 
slice timing correction? If the acquisition was done with a multi-slice technique, this step corrects for the timing differences in slice acquisition, ensuring accurate alignment of temporal data.


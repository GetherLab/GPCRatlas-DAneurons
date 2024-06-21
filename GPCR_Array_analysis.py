# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 15:16:23 2024

@author: Jan Hendrik Schmidt
"""

# importing packages
import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import gmean

# setting directory
base_dir = 'E:/tmpDATA/GPCR_array/'  # Work

# Cp data normalization
# loading data
df = pd.read_excel(base_dir + "Raw_Array_Cp.xlsx")

# collecting column names
columns_names = df.columns

# define cp columns
cp_columns = columns_names[3:15]

# Dictionary to store treatment outputs
norm_dict = {}

# initial loop for normalization values
for sample in cp_columns:

    # find geomean of transcripts that have a Cp value higher than 36
    geo_mean = gmean(df[sample][df[sample] > 36])

    # calculate normalized noise level for sample
    noise_value = 35
    normalized_noise = pow(2, -(noise_value-geo_mean))
    inverse_noise_value = 1/normalized_noise
    
    # normalize cp by geomean and noise
    treatment_output = [pow(2, -(row-geo_mean))*gmean(inverse_noise_value) for row in df[sample]]

    norm_dict["RE_"+sample] = treatment_output

# Append the key-value pair to the DataFrame
for key, values in norm_dict.items():
    df[key] = values
    
# log2 transformation and defining EGFP+/- group columns
# updating column names
columns_names2 = df.columns

# defining normalized data columns
all_RE_columns = columns_names2[21:33]

# log2 transformation
for column in all_RE_columns:
    df["log2_"+column] = np.log2(df[column])

# updating column names
columns_names3 = df.columns

# defining EGFP positive and negative group columns
all_columns = columns_names3[33:45]
positive_columns = columns_names3[33:39]
negative_columns = columns_names3[39:45]

# Calculate mean and standard deviation for each row and group
# total
mean_all = df[all_columns].mean(axis=1)
mean_all_std = df[all_columns].std(axis=1)

# EGFP positives
mean_positive = df[positive_columns].mean(axis=1)
mean_positive_std = df[positive_columns].std(axis=1)

# EGFP negatives
mean_negative = df[negative_columns].mean(axis=1)
mean_negative_std = df[negative_columns].std(axis=1)

# Mean difference between groups
mean_differences = mean_positive-mean_negative

# Perform t-test for every transcript and collect p_values
# Setting up list
p_values = []

# looping over dataframe and running ttests
for index, row in df.iterrows():
    
    # grabbing values for EGFP+/- groups
    positive_group = list(row[positive_columns].values)
    negative_group = list(row[negative_columns].values)

    _, p_value = stats.ttest_ind(positive_group, negative_group)
    p_values.append(p_value)

# Convert p-values to ease interpretation
log_p_values = -np.log10(p_values)

# collect data in dataframe
df["Mean RE ALL"] = mean_all
df["Mean RE StD. ALL"] = mean_all_std
df["Mean RE EGFP+"] = mean_positive
df["Mean RE StD. EGFP+"] = mean_positive_std
df["Mean RE EGFP-"] = mean_negative
df["Mean RE StD. EGFP-"] = mean_negative_std
df["-log10(pvalue)"] = log_p_values
df["log2_FC"] = mean_differences

# export dataframe
df.to_excel(base_dir + "Data.xlsx", header=True, index=False)
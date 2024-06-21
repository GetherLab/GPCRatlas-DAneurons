from process_data import process_data
from calculate_response import calculate_response
import os
import pandas as pd
import numpy as np

def process_file(file):
	path = os.path.join(root, file)
	data = (process_data(pd.read_csv(path), baseline))
	data.data = data.data.iloc[:-2]
	data.baseline_drop_below()
	return data

def calculate_delta_increase(condition):
	baseline = (conditions_corrected[condition][0]-7, conditions_corrected[condition][0]-1)
	delta = responses.calculate_delta(baseline=baseline, response=conditions_corrected[condition])
	std = responses.std(baseline)
	std = std*sd_cut_off
	true_false_std = pd.Series(np.where(delta > std, True, False))
	print(f"Total number of cells: {len(true_false_std)}")
	print(f"Number of responders for {condition}: {true_false_std.values.sum()}")
	data_responders = responses.data.loc[:, true_false_std.values == True]
	data_non_responders = responses.data.loc[:, true_false_std.values == False]
	return data_responders, data_non_responders

# Variables
# Update before running
root = 'data' # Data root folder
output = 'analyzed' # Output folder
sd_cut_off = 3

# File to load in CSV format
file_name = 'data.csv'
# {name: [start time, end time, type (baseline/min/max)]}
conditions = {
	'condition1': [..., ..., ...],
	'condition2': [..., ..., ...],
}
# Time points to use for slope correction
frames_slope_correction = [..., ...]
# Time points to use for baseline
baseline = [..., ...]

###################################

conditions_corrected = {}
for condition in conditions:
	conditions_corrected[condition] = [i-baseline[0] for i in conditions[condition] if type(i) is int]

all_data = process_file(file_name)

# Initialize variables
y_selected = pd.DataFrame()
parameters = pd.DataFrame()
time_series = pd.DataFrame()
time_series_non_resp = pd.DataFrame()

# Initialize the class for calculation	
responses = calculate_response(all_data(), conditions)

# We want to keep original conditions beacuse we don't cut out the frames before basline
conditions_corrected = conditions

# Remove cells not responding to KCl
baseline_KCl = (conditions_corrected['KCl'][0]-7, conditions_corrected['KCl'][0]-1)
delta_KCl = responses.calculate_delta(baseline=baseline_KCl, response=conditions_corrected['KCl'])
# Calculate the cut off
std = responses.std(baseline_KCl)
std = std*sd_cut_off
# Sort the cells based on their response compared to SD
true_false_kcl_std = pd.Series(np.where(delta_KCl > std, True, False))
print(f"Total number of cells: {len(true_false_kcl_std)}")
print(f"Number of responders for KCl: {true_false_kcl_std.values.sum()}")
# Copy over data with KCl non responders removed
responses.data = responses.data.loc[:, true_false_kcl_std.values == True]

# Correct slope
# Calculate fit
y = responses.data.loc[frames_slope_correction[0]:frames_slope_correction[1]]
y = y.reset_index(drop=True)
y_fit_line, parameters_line, perr = responses.nonlinfit_line(y.index.values, y)

# Add correction to all columns
data_corrected_slope = responses.data.copy()
data_corrected_slope = data_corrected_slope.reset_index(drop=True)
for col, series in data_corrected_slope.items():
	k = parameters_line.loc[col].iloc[1]
	x = series.index
	y_correction = x*k
	data_corrected_slope.loc[:, col] = data_corrected_slope.loc[:, col]-y_correction

# Copy over data with slope corrected data
responses.data = data_corrected_slope

# Normalize data
min = responses.data.loc[baseline[0]:baseline[1]].mean()
max = responses.data.loc[conditions_corrected['KCl'][0]:conditions_corrected['KCl'][1]].max()
data_normalized = (responses.data - min) / (max - min)
responses.data = data_normalized

# Save the response data in temp var
data_responders = responses.data

# Calculate the delta increase for cmpdA compared to average 6 (1 min) frames before stimulation
data_responders_cmpdA, data_non_responders_cmpdA = calculate_delta_increase('cmpdA')

# Calculate delta increase for antagonist
data_responders_antagonist, data_non_responders_antagonist = calculate_delta_increase('antagonist')

# Calculate delta increase for antagonist+cmpdA
data_responders_antagonist_cmpdA, data_non_responders_antagonist_cmpdA = calculate_delta_increase('antagonist+cmpdA')

data_responders_cmpdA.to_csv(os.path.join(output, 'data_cmpdA_'+file_name+'.csv'))
data_non_responders_cmpdA.to_csv(os.path.join(output, 'data_cmpdA_'+file_name+'_neg.csv'))

data_responders_antagonist.to_csv(os.path.join(output, 'data_antagonist_'+file_name+'.csv'))
data_non_responders_antagonist.to_csv(os.path.join(output, 'data_antagonist_'+file_name+'_neg.csv'))

data_responders_antagonist_cmpdA.to_csv(os.path.join(output, 'data_antagonist_cmpdA_'+file_name+'.csv'))
data_non_responders_antagonist_cmpdA.to_csv(os.path.join(output, 'data_antagonist_cmpdA_'+file_name+'_neg.csv'))

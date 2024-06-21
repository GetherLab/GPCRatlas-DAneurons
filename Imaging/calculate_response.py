import pandas as pd
from scipy.optimize import curve_fit as scipy_curve_fit

class calculate_response:
	def __init__(self, data: pd.DataFrame, conditions: dict):
		self.data = data
		self.data_org = self.data.copy()
		self.conditions = { k:v for k,v in conditions.items() if 'baseline' not in k}
		if 'baseline' in conditions:
			self.baseline = conditions['baseline']
	
	def line(self, x, intercept, slope):
		""" Straight line fit for using with non-linear fit data. """
		return(intercept + x*slope)
	
	def nonlinfit_line(self, x: list, y: pd.DataFrame):
		"""
		Straight line fit for nonlinear fit comparison. Returns the y-fit and parameters.
		
		Arguments:
		:x: x-values (non-log)
		:y: y-values
		"""
		if isinstance(y, pd.DataFrame):
			parameters = pd.DataFrame(columns=['intercept', 'slope'])
			y_fit = pd.DataFrame(index=y.index, columns=y.columns)
			perr = pd.DataFrame(columns=['intercept', 'slope'])
			for col, row in y.items():
				parameters.loc[col], c = scipy_curve_fit(self.line, x, row, maxfev=10240)
				y_fit.loc[:, col] = self.line(x, parameters.loc[col].iloc[0], parameters.loc[col].iloc[1])
		else:
			parameters, c = scipy_curve_fit(self.line, x, y, maxfev=10240)
			y_fit = self.line(x, parameters[0], parameters[1])	
		return y_fit, parameters, perr
	
	def calculate_delta(self, baseline, response, type=None):
		""" Calculates the delta response between baseline and response frames.
		Assumes one baseline with ladder type sitmulation.
		Takes the maximum value of the baseline.

		Arguments:
		:type: max or min
		"""
		if type is None:
			type = response[2]
		if type == 'max':
			min = self.data.loc[baseline[0]:baseline[1]].max()
			max = self.data.loc[response[0]:response[1]].max()
		if type == 'min':
			min = self.data.loc[baseline[0]:baseline[1]].min()
			max = self.data.loc[response[0]:response[1]].min()
		if type == 'baseline':
			min = self.data.loc[response[0]:response[1]].min()
			max = self.data.loc[response[0]:response[1]].max()
		return max-min
	
	def std(self, frames):
		""" Returns the standard deviation of the defined frames """
		return self.data.loc[frames[0]:frames[1]].std()
	
	def drop_true_false(self, data: pd.DataFrame, tf: pd.Series):
		"""
		Drops all rows in data where tf is false. Returns updated data.
		
		Arguments:
		:data: Data to be processed.
		:tf: List of True/False with same index as data.
		"""
		return data.loc[tf.values == True].copy()
	
	def drop_non_responders_sd(self, condition, cut_off=5, abs=False, neg=False, baseline=False, update=True):
		"""
		Remove all non-responders based on the response compared to the baseline SD. Returns the true_false table.
		
		Arguments:
		:condition: The response condition to compare with.
		:cut_off: The cut-off required to count as a response.
		"""
		if baseline is False:
			std = self.std([self.baseline[0],self.baseline[1]])
		else:
			std = self.std(self.conditions[baseline])
		data = self.data_delta
		if abs is False:
			data_true_false = (data[condition] > cut_off*std[std.index.isin(data.index)])
		elif abs is True:
			data_true_false = (data[condition].abs() > cut_off*std[std.index.isin(data.index)])
		if neg is True:
			data_true_false = (data[condition].abs() > cut_off*std[std.index.isin(data.index)]) & (data[condition] < 0)
		if update is True:
			self.data = self.data.loc[:, data_true_false.values == True]
			self.data_delta = self.data_delta.loc[data_true_false.values == True]
		return data_true_false
	
	def drop_non_responders_delta(self, condition, baseline, neg=False):
		"""
		Remove all non-responders based on the response compared to defined baseline delta.
		"""
		data = self.data_delta
		if neg is False:
			data_true_false = (data[condition] > data[baseline])
		if neg is True:
			data_true_false = (data[condition] < data[baseline])
		return data_true_false
from __future__ import annotations
import pandas as pd
import numpy as np

class process_data:
	def __init__(self, data, baseline: list, fps: float=None, bg=True):
		self.data = pd.DataFrame(data)
		self.data_raw = self.data.copy()
		self.baseline = baseline
		self.fps = fps

		self.__rename()
		self.__move_frame()
		if bg is True:
			self.__rm_bg()
		self.__unique_names()
		
		self.data_org = self.data

	def __call__(self):
		return self.data

	def __rename(self):
		""" Renames first column to frame. """
		if 'frame' not in self.data.columns:
			self.data.rename(columns = {self.data.columns[0]: 'frame'}, inplace = True)

	def __move_frame(self):
		""" Copy the frame column to its own pandas Series and converts the index of data to frames """
		self.frames = self.data['frame']
		self.data.set_index('frame', inplace = True)

	def __rm_bg(self):
		""" Removes the background from all data """
		self.data.update(self.data.sub(self.data.iloc[:, -1], axis = 0))
		self.data.drop(self.data.columns[-1], axis = 1, inplace = True)

	def __baseline(self):
		""" Returns the mean value of the baseline frames for each column. """
		baseline = self.data_org.loc[self.baseline[0]:self.baseline[1]]
		return baseline.mean()
	
	def return_baseline(self):
		""" Returns the mean value of the baseline frames for each column. """
		baseline = self.data_org.loc[self.baseline[0]:self.baseline[1]]
		return baseline.mean()
	
	def __unique_names(self):
		""" Update all column names with unique numbers. """
		columns = [i for i in range(len(self.data.columns))]
		self.data.columns = columns

	def make_ratio(self):
		""" Updates data to have the ratio of channels. """	
		ratio = self.data_channel[1].div(self.data_channel[0])
		self.data = ratio

	def cut_frames(self, data: pd.DataFrame):
		""" Returns the data with the frames before baseline cut out """
		return data.loc[self.baseline[0]:]

	def rolling(self, window=3, inplace=True):
		"""
		Transforms the data with rolling average.

		Arguments:
		window: the window size for the rolling average.
		inplace: Should data be replaced?
		"""
		rolling = self.data.rolling(window, center=False).mean()
		rolling.dropna(inplace = True)
		if inplace is True:
			self.data = rolling
		return rolling

	def normalize_baseline(self, cut = True, inplace = True):
		""" Returns data normalized to the baseline. """
		baseline_mean = self.__baseline()
		normalized = self.data.div(baseline_mean)
		if cut is True:
			normalized = self.cut_frames(normalized)
		if inplace is True:
			self.data = normalized
		return normalized

	def baseline_drop_below(self, value=0, inplace=True):
		""" Drops a column if baseline value is below value. """
		baseline_mean = self.__baseline()
		below_baseline = pd.Series(np.where(baseline_mean < value, True, False))
		cleaned_data = self.data.loc[:, below_baseline.values == False]
		if inplace is True:
			self.data = cleaned_data
		return cleaned_data
	
	def frame2time(self, data: pd.DataFrame = None, type = 'min'):
		""" Converts frames to time """
		if data is None: data = self.data
		match type:
			case 'min':
				x = 60
				name = 'Time (min)'
			case 's':
				x = 1
				name = 'Time (s)'
		time = pd.Series(index = data.index, data = data.index/x/self.fps, name = name)
		data.insert(0, time.name, time)
		return data
	
	def merge(self, instance: process_data):
		""" Inserts the data from instance to the current instance. """
		self.data = pd.concat([self.data, instance.data], axis=1)
		self.__unique_names()
	
	def export(self, file, data: pd.DataFrame = None, time = True, frame = False):
		"""
		Exports the data to a csv file.

		Parameters:
		data: is a pandas DataFrame to be exported. Defaults to self.data.
		time: include time column if present.
		frame: include frame column.
		"""
		file = file+'.csv'
		data = data or self.data.copy()
		if time is False:
			data.drop(str.startswith('Time'), inplace = True)
		data.to_csv(file, index = frame), print('Exported ' +file+ '.')
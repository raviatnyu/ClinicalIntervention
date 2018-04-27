import os
import json
import copy

class Dataiter():

	#Create a seperate file for each ICU_STAYID? Memory issues?
	def __init__(self, labeljsonfile, staticjsonfile, timeseriesjsonfile, featuresfile, outliersfile, trainfile, valfile, testfile, fwindow=6, lwindow=4, gwindow=4, fillprevvalue=True):
		self.labels = json.load(open(labeljsonfile, 'r'))
		self.static = json.load(open(staticjsonfile, 'r'))
		self.timeseries = json.load(open(timeseriesjsonfile, 'r'))
		self.features = json.load(open(featuresfile, 'r'))
		self.outliers = json.load(open(outliersfile, 'r'))

		self.trainids = json.load(open(trainfile, 'r'))["IcuIds"]
		self.valids = json.load(open(valfile, 'r'))["IcuIds"]
		self.testids = json.load(open(testfile, 'r'))["IcuIds"]

		self.staticfeatures = {} #fname:ftype
		self.timeseriesfeatures = {} #fname:ftype	 
		self.numericfeatureindex = {}
		self.categoricfeatureindex = {}
		
		self.featurewindow = fwindow
		self.labelwindow = lwindow
		self.gapwindow = gwindow
		
		self.fillprevvalue = fillprevvalue
	
	def populatefeatures(self):
		features = self.features["Features"]
		for feature in features:
			featurename = feature["Feature"]
			featurepattern = feature["FeaturePattern"]
			featuretype = feature["FeatureType"]
			if featurepattern == "Static":
				if featurename not in self.staticfeatures.keys():
					self.staticfeatures[featurename] = feature["FeatureType"]
			elif featurepattern == "TimeSeries":
				if featurename not in self.timeseriesfeatures.keys():
					self.timeseriesfeatures[featurename] = feature["FeatureType"]
			if featuretype == 'Numeric':
				self.numericfeatureindex[featurename] = len(self.numericfeatureindex)
			elif featuretype == 'Categoric':
				self.categoricfeatureindex[featurename] = len(self.categoricfeatureindex)
	
		print(self.staticfeatures)
		print(self.timeseriesfeatures)
		print(self.numericfeatureindex)
		print(self.categoricfeatureindex)

	def processoutlier(self, fname, fvalue):
		if fname in self.outliers:
			outliersdict = self.outliers[fname]
			if fvalue in outliersdict:
				print(fvalue)
				return outliersdict[fvalue]
		return fvalue

	def iterstaticdeep(self, data='train'):
		if data == 'train': validicuids = self.trainids
		elif data == 'val': validicuids = self.valids
		elif data == 'test': validicuids = self.testids
		static_data = self.static["icustay_static"]
		#change it to items for python3
		for icu_stay, attributes in static_data.items():
			if icu_stay in validicuids:
				for feature in self.staticfeatures.keys():
					if feature in attributes.keys():
						yield icu_stay, feature, self.staticfeatures[feature], attributes[feature]
 
	def itertimeseriesdeep(self, data='train'):
		if data == 'train': validicuids = self.trainids
		elif data == 'val': validicuids = self.valids
		elif data == 'test': validicuids = self.testids
		timeseries_data = self.timeseries["icustay_timeseries"]
		for icu_stay, attributes in timeseries_data.items():
			if icu_stay in validicuids:
				for feature in self.timeseriesfeatures.keys():
					if feature in attributes.keys():
						for value, timeindex in attributes[feature]:
							yield icu_stay, feature, self.timeseriesfeatures[feature], self.processoutlier(feature, value)

	def iterdata(self, data='train'):
		def getinterval(series):
			start, end = -1, -1
			for value, tindex in series:
				if value!=-2 or value!= -1:
					start = tindex
					break
			if series != []: end = series[-1][1] 
			return start, end

		def filloutlier(feature, series):
			newseries = []
			for value, tindex in series:
				newvalue = self.processoutlier(feature, value)
				newseries.append([newvalue, tindex])
			return newseries

		def fillmissing(series):
			newseries = []
			if series != []: prev = series[0][0]
			for value, tindex in series:
				if value==-1 or value=='':
					value = prev
				prev = value
				newseries.append([value, tindex])
			return newseries

		def getfeaturecategory(feature):
			for featuredict in self.features["Features"]:
				if featuredict["Feature"] == feature:
					return featuredict["FeatureCategory"]
			return None

		def classifylabel(labelswindow):
			#0: 0000, #1: 1111, #2: 0011, #3: 1100
			if labelswindow[0][0] == 0:
				for i in range(len(labelswindow)-1):
					if labelswindow[i+1][0] == 1:
						return 2
				return 0
			elif labelswindow[0][0] == 1:
				for i in range(len(labelswindow)-1):
					if labelswindow[i+1][0] == 0:
						return 3
				return 1
							
		if data == 'train': validicuids = self.trainids
		elif data == 'val': validicuids = self.valids
		elif data == 'test': validicuids = self.testids
		static_data = self.static["icustay_static"]
		timeseries_data = self.timeseries["icustay_timeseries"]
		label_data = self.labels["icustay_label"]

		for icu_stay in validicuids:
			if icu_stay in static_data and icu_stay in timeseries_data:
				static_features = copy.deepcopy(static_data[icu_stay])
				timeseries_features = copy.deepcopy(timeseries_data[icu_stay])
				labelseries = copy.deepcopy(label_data[icu_stay])
				
				minstart, maxend = 241, -1
				for feature, series in timeseries_features.items():
					if getfeaturecategory(feature) != "Vital": continue
					fstart, fend = getinterval(series)
					if fstart < minstart and fstart >= 0: minstart = fstart
					if fend > maxend: maxend = fend
				for feature, series in timeseries_features.items():
					timeseries_features[feature] = filloutlier(feature, series)
					series = timeseries_features[feature]
					if self.fillprevvalue:
						timeseries_features[feature] = fillmissing(series)
					fstart, fend = getinterval(series)
					fill = -1
					if self.fillprevvalue and series!=[]: fill = series[fend][0]
					pad = [[fill, fend+i+1] for i in range(maxend-fend)]
					timeseries_features[feature].extend(pad)

				lstart, lend = getinterval(labelseries)
				discharge = self.labelwindow -1 + self.gapwindow
				lpad = [[0, lend+i+1] for i in range(maxend-lend+discharge)] 
				labelseries.extend(lpad) 

				labeloffset = self.featurewindow #+ self.gapwindow
				labeldistance = self.featurewindow -1 + self.gapwindow
				labelrange = self.labelwindow

				for sslice in range(maxend-labeloffset+1+1): #1 for range 1 for offset
					instance = {}
					for feature in self.staticfeatures.keys():
						if feature in static_features:
							instance[feature] = [static_features[feature]]
						else: instance[feature] = ['']
					for feature in self.timeseriesfeatures.keys():
						if feature in timeseries_features:
							instance[feature] = [value for value, tindex in timeseries_features[feature][sslice:sslice+self.featurewindow]]
						#else: instance[feature] = [[-2, sslice+i] for i in range(self.featurewindow)]
						else: instance[feature] = [-2 for i in range(self.featurewindow)]

					label = labelseries[sslice+labeldistance:sslice+labeldistance+labelrange]
					label = classifylabel(label)
					yield instance, label	

if __name__=='__main__':

	labeljsonfile = 'icu_label.json'
	staticjsonfile = 'icu_static.json'
	timeseriesjsonfile = 'icu_timeseries.json'
	featuresfile = 'icu_features.json'
	outliersfile = 'icu_outliers.json'
	
	trainfile = 'trainicuidsample.json'
	valfile = 'valicuid.json'
	testfile = 'testicuid.json'

	dataiter = Dataiter(labeljsonfile, staticjsonfile, timeseriesjsonfile, featuresfile, outliersfile, trainfile, valfile, testfile, fwindow=6, lwindow=4, gwindow=4, fillprevvalue=True)
	dataiter.populatefeatures()
	i=0
	for icuid, fname, ftype, fvalue in dataiter.iterstaticdeep():
		i = i+1
		print(icuid, fname, ftype, fvalue) 
		if i==10:
			break
	i=0
	for icuid, fname, ftype, fvalue in dataiter.itertimeseriesdeep():
		i = i+1
		print(icuid, fname, ftype, fvalue)
		if i==10:
			break

	for instance, label in dataiter.iterdata():
		print(instance)	
		print(label)

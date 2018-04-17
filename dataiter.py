import os
import json

class Dataiter():

	#Create a seperate file for each ICU_STAYID? Memory issues?
	def __init__(self, staticjsonfile, timeseriesjsonfile, featuresfile, fwindow, lwindow):
		self.static = json.load(open(staticjsonfile, 'r'))
		self.timeseries = json.load(open(timeseriesjsonfile, 'r'))
		self.features = json.load(open(featuresfile, 'r'))
		self.staticfeatures = {} #fname:ftype
		self.timeseriesfeatures = {} #fname:ftype	 
		self.featureindex = {}
		
		self.featurewindow = fwindow
		self.labelwindow = lwindow

	
	def populatefeatures(self):
		features = self.features["Features"]
		for feature in features:
			featurename = feature["Feature"]
			featurepattern = feature["FeaturePattern"]
			if featurepattern == "Static":
				if featurename not in self.staticfeatures.keys():
					self.staticfeatures[featurename] = feature["FeatureType"]
			elif featurepattern == "TimeSeries":
				if featurename not in self.timeseriesfeatures.keys():
					self.timeseriesfeatures[featurename] = feature["FeatureType"]
			self.featureindex[feature] = len(self.featureindex)
	
		print(self.staticfeatures)
		print(self.timeseriesfeatures)
		print(self.featureindex)

	def iterstaticdeep(self):
		static_data = self.static["icustay_static"]
		#change it to items for python3
		for icu_stay, attributes in static_data.iteritems():
			for feature in self.staticfeatures.keys():
				if feature in attributes.keys():
					yield icu_stay, feature, self.staticfeatures[feature], attributes[feature]
 
	def itertimeseriesdeep(self):
		timeseries_data = self.timeseries["icustay_timeseries"]
		for icu_stay, attributes in timeseries_data.iteritems():
			for feature in self.timeseriesfeatures.keys():
				if feature in attributes.keys():
					for value, timeindex in attributes[feature]:
						yield icu_stay, feature, self.timeseriesfeatures[feature], value

	def iterdata(self):
		
		return {'fname' : [], 'fname':[]}


if __name__=='__main__':

	staticjsonfile = 'icu_static.json'
	timeseriesjsonfile = 'icu_timeseries.json'
	featuresfile = 'icu_features.json'

	dataiter = Dataiter(staticjsonfile, timeseriesjsonfile, featuresfile)
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

	

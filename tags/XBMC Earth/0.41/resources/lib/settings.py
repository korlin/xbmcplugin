import xbmc, datetime, tarfile, os, glob, urllib, httplib, sys, os.path, time, datetime, urllib2
import simplejson

TEMPFOLDER = os.path.join( os.getcwd().replace( ";", "" ), "temp\\" )	

class Settings:
	settings = dict()
	
	def write_settings(self):
		fName = file
		f = open(TEMPFOLDER + "settings.xml", 'wb')
		data = simplejson.dumps(self.settings, sort_keys=True, indent=4)
		f.write(data)
		f.close()
		pass
	
	def read_settings(self):
		try:
			fName = file
			f = open(TEMPFOLDER + "settings.xml", 'r')
			self.settings = simplejson.loads(f.read())
			f.close()
		except:
			self.load_defaults()
			
	def load_defaults(self):

		self.settings["geo"] = dict()
		self.settings["fav"] = dict()
		self.settings["analytics"]=dict()
		fav_seq = []
		self.settings["fav"] = fav_seq
		self.settings["options"] = dict()
		
		self.settings["geo"]["lon"] = 13.411494
		self.settings["geo"]["lat"] = 52.523480
		self.settings["geo"]["zoom"] = 8
		self.settings["geo"]["hybrid"] = 1
		
		self.settings["fav"].append(dict())
		self.settings["fav"][0]["name"] = "Berlin"
		self.settings["fav"][0]["lon"] = 13.411494
		self.settings["fav"][0]["lat"] = 52.523480
		self.settings["fav"][0]["zoom"] = 8
		
		self.settings["fav"].append(dict())
		self.settings["fav"][1]["name"] = "New York"
		self.settings["fav"][1]["lon"] = -73.986951000000005
		self.settings["fav"][1]["lat"] = 40.756053999999999
		self.settings["fav"][1]["zoom"] = 6
		
		self.settings["fav"].append(dict())
		self.settings["fav"][2]["name"] = "Syndey"
		self.settings["fav"][2]["lon"] = 151.20711399999999
		self.settings["fav"][2]["lat"] = -33.867139000000002
		self.settings["fav"][2]["zoom"] = 4
		
		self.settings["analytics"]["utmac"] = "UA-2760691-3"
		self.settings["analytics"]["url"] = "www.xbmcmaps.de"
		self.settings["analytics"]["cookie_number"] = ""
		self.settings["analytics"]["random"] = ""
		self.settings["analytics"]["first_use"] = ""
		self.settings["analytics"]["last_use"] = ""
		self.settings["analytics"]["now"] = ""
		self.settings["analytics"]["count"] = 0
		
		self.settings["options"]["update"] = True
		
		pass
	

import xbmc, datetime, tarfile, os, glob, urllib, httplib, sys, os.path, time, datetime
from threading import Thread
TEMPFOLDER = os.path.join( os.getcwd().replace( ";", "" ), "temp\\" )	

class Xbmcearth_communication:
	sTargetServer = ""
	sTargetUrl = ""
	sData = []
	def get_Query_Place(self, url, key, place):
		header = {
			"Host":"maps.google.com",
			"User-Agent":"Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11",
			"Accept":"*/*",
			"Accept-Language":"de-de,de;q=0.8,en-us;q=0.5,en;q=0.3",
			"Accept-Charset":"ISO-8859-1,utf-8;q=0.7,*;q=0.7",
			"Keep-Alive":"300",
			"Proxy-Connection":"keep-alive",
			"Referer": url}
		place = urllib.quote(place) 
		params = '?q=' + place + '&output=kml&key='+ key 
		body = ''
		self.sTargetUrl = "http://maps.google.com/maps"
		if self._request("GET",params,header, body)!=True:
			return False
		data = self.sData
		fName = file
		f = open(TEMPFOLDER + "query.kml", 'wb')
		f.write(data)
		f.close()
		return self.sData

	
	#http://maps.google.com//maps?f=d&source=s_d&saddr=Offenburg&daddr=Schutterwald&hl=de&geocode=&mra=ls&output=kml
	def get_Route(self, url, saddr, daddr):
		try:
			os.mkdir(TEMPFOLDER+"Route")
		except: pass
		header = {
			"Host":"maps.google.com",
			"User-Agent":"Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11",
			"Accept":"*/*",
			"Accept-Language":"de-de,de;q=0.8,en-us;q=0.5,en;q=0.3",
			"Accept-Charset":"ISO-8859-1,utf-8;q=0.7,*;q=0.7",
			"Keep-Alive":"300",
			"Proxy-Connection":"keep-alive",
			"Referer": url}
		if xbmc.getLanguage() == 'German':
			lang = 'de'
		else:
			lang = 'en'
		saddr = urllib.quote(saddr) 
		daddr = urllib.quote(daddr) 
		params = '?f=d&source=s_d&saddr=\"' + saddr + '\"&daddr=\"' + daddr + '\"&hl='+ lang +'&geocode=&mra=ls&output=kml' 
		body = ''
		self.sTargetUrl = "http://maps.google.com/maps"
		if self._request("GET",params,header, body)!=True:
			return False
		data = self.sData
		fName = file
		f = open(TEMPFOLDER + "Route\\route.kml", 'wb')
		f.write(data)
		f.close()
		return self.sData
	
	def get_Panoramio(self, url, param):
		header = {
			"Host":"www.panoramio.com",
			"User-Agent":"Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11",
			"Accept":"*/*",
			"Accept-Language":"de-de,de;q=0.8,en-us;q=0.5,en;q=0.3",
			"Accept-Charset":"ISO-8859-1,utf-8;q=0.7,*;q=0.7",
			"Keep-Alive":"300",
			"Proxy-Connection":"keep-alive",
			"Referer": url} 
		params = param
		#-print params
		body = ''
		self.sTargetUrl = "http://www.panoramio.com/map/get_panoramas.php"
		if self._request("GET",params,header, body)!=True:
			return False
		data = self.sData
		fName = file
		f = open(TEMPFOLDER + "panoramio.xml", 'wb')
		f.write(data)
		f.close()
		return self.sData
		
	def get_Flickr(self, url, param):
		header = {
			"Host":"api.flickr.com",
			"User-Agent":"Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11",
			"Accept":"*/*",
			"Accept-Language":"de-de,de;q=0.8,en-us;q=0.5,en;q=0.3",
			"Accept-Charset":"ISO-8859-1,utf-8;q=0.7,*;q=0.7",
			"Keep-Alive":"300",
			"Proxy-Connection":"keep-alive",
			"Referer": url} 
		params = param
		body = ''
		self.sTargetUrl = "http://api.flickr.com/services/rest"
		if self._request("GET",params,header, body)!=True:
			return False
		data = self.sData
		fName = file
		f = open(TEMPFOLDER + "flickr.xml", 'wb')
		f.write(data)
		f.close()
		return self.sData


	def get_Maps_JS(self, url, key):
		#http://maps.google.com/maps?file=api&v=2&key=ABQIAAAAnyP-GOJDhG7H7ozm0RRsCBSiQ_eECfBHgA9cMSxRoMYUiueUzxSinT-_iJIghikcXgs_lmKq8_i5pQ
		#GET /maps?file=api&v=2&key=ABQIAAAAnyP-GOJDhG7H7ozm0RRsCBSiQ_eECfBHgA9cMSxRoMYUiueUzxSinT-_iJIghikcXgs_lmKq8_i5pQ HTTP/1.1
		#Host: maps.google.com
		#User-Agent: Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11
		#Accept: */*
		#Accept-Language: de-de,de;q=0.8,en-us;q=0.5,en;q=0.3
		#Accept-Encoding: gzip,deflate
		#Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.7
		#Keep-Alive: 300
		#Connection: keep-alive
		#Referer: http://www.informatik.uni-jena.de/~sack/test.htm
		#Cookie: PREF=ID=20f16b2c860a0bb0:TM=1200137261:LM=1200137261:S=KrXC-VU3vnlqGSna; NID=7=W2xBZleMgTCTpgpF1f_RQrvziIveCJt9_GK09Zx293A7hh_8R-ACdz7RxRc6hzWzrRyYfEfjLMA1jTObCLokylOVPlf_AkZ9iAvh2PLbgXVac5ahb1FOiuz6cu2kq1c7
		
		header = {
			"Host":"maps.google.com",
			"User-Agent":"Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11",
			"Accept":"*/*",
			"Accept-Language":"de-de,de;q=0.8,en-us;q=0.5,en;q=0.3",
			"Accept-Charset":"ISO-8859-1,utf-8;q=0.7,*;q=0.7",
			"Keep-Alive":"300",
			"Proxy-Connection":"keep-alive",
			"Referer": url}
		params = '?file=api&v=2&key='+ key
		body = ''
		self.sTargetUrl = "http://maps.google.com/maps"
		if self._request("GET",params,header, body)!=True:
			return False
		data = self.sData
		fName = file
		#TEMPFOLDER = "Q:\\temp\\"
		f = open(TEMPFOLDER + "maps1.js", 'wb')
		f.write(data)
		f.close()
		return self.sData
	
	def get_Maps_Copyright(self, url, key, spn, t, z, vp, ev, v):
		#GET /maps?spn=0.008115,0.021458&t=k&z=15&key=ABQIAAAAnyP-GOJDhG7H7ozm0RRsCBSiQ_eECfBHgA9cMSxRoMYUiueUzxSinT-_iJIghikcXgs_lmKq8_i5pQ&vp=50.927032,11.601734&ev=p&v=24 HTTP/1.1
		#Accept: */*
		#Referer: http://www.informatik.uni-jena.de/~sack/test.htm
		#Accept-Language: de
		#UA-CPU: x86
		#Accept-Encoding: gzip, deflate
		#User-Agent: Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; InfoPath.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)
		#Host: maps.google.com
		#Connection: Keep-Alive

		header = {
			"Host":"maps.google.com",
			"User-Agent":"Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11",
			"Accept":"*/*",
			"Accept-Language":"de-de,de;q=0.8,en-us;q=0.5,en;q=0.3",
			"Accept-Charset":"ISO-8859-1,utf-8;q=0.7,*;q=0.7",
			"Keep-Alive":"300",
			"Proxy-Connection":"keep-alive",
			"Referer":  url}
		params = '?spn='+ spn +'&t='+ t +'&z='+ z +'&key=' + key + '&vp=' + vp + '&ev=' + ev + '&v=' + v
		body = ''
		self.sTargetUrl = "http://maps.google.com/maps"
		if self._request("GET",params,header, body)!=True:
			return False
		#data = self.sData
		#fName = file
		#TEMPFOLDER = "Q:\\temp\\"
		#f = open(TEMPFOLDER + "maps1.js", 'wb')
		#f.write(data)
		#f.close()
		return self.sData 		

	def connect (self, targetserver, targetport=80):
		self.sTargetServer=targetserver
		self.sTargetPort = targetport
		self.connection = httplib.HTTPConnection(self.sTargetServer, self.sTargetPort)	
	
	def close(self):
		self.connection.close()
	
	def _request(self, action, params, header, body ):
		try:
			self.connection.request(action, self.sTargetUrl+params, body, header)
		except:
			print "Connection Error"
			return False
		response = self.connection.getresponse()
		if response.status != 200:
			print response.status, response.reason
			return False
		else:
			#-print response.status, response.reason
			data = response.read()
			if data != '':
				self.sData = data
			else:
				return False
		return True
		
	def _Dump(self):
		name = datetime.datetime.now().strftime('%Y%m%d%H%M%S'+timezone)
		while os.path.exists(name+'.html'):
			name = datetime.datetime.now().strftime('%Y%m%d%H%M%S'+timezone)
		outfile= open(name+'.html','w+')
		outfile.write(self.sData)
		outfile.close()


class get_pic(Thread):
	
	def __init__ (self,params,FileName,referer_url,imgBlocks):
		Thread.__init__(self)
		self.parms = params[params.find('?'):len(params)]
		self.referer_url = referer_url
		self.filename = FileName
		self.path = ""
		self.sTargetUrl = params[0:params.find('?')]
		self.host = params[params.find('//')+2:params.find('/',params.find('//')+2)]
		self.imgBlocks = imgBlocks
		self.connect(self.host)
	def run(self):
		if not os.path.exists(TEMPFOLDER + self.filename + ".png"):
			header = {
				"Host": self.host,
				"User-Agent":"Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11",
				"Accept":"*/*",
				"Accept-Language":"de-de,de;q=0.8,en-us;q=0.5,en;q=0.3",
				"Accept-Charset":"ISO-8859-1,utf-8;q=0.7,*;q=0.7",
				"Keep-Alive":"300",
				"Proxy-Connection":"keep-alive",
				"Referer":  self.referer_url}
			params = self.parms
			body = ''
			if self._request("GET",params,header, body)!=True:
				self.imgBlocks.setImage('')
				return False
			data = self.sData
			fName = file
			f = open(TEMPFOLDER + self.filename + ".png", 'wb')
			f.write(data)
			f.close()
		else:
			f = TEMPFOLDER + self.filename + ".png"
			today = datetime.datetime.now()
			atime = int(time.mktime(today.timetuple()))
			mtime = atime
			times = (atime,mtime)
			os.utime(f, times)
		self.path = TEMPFOLDER + self.filename + ".png"
		self.imgBlocks.setImage(self.path)
		return True
	
	def _request(self, action, params, header, body ):
		try:
			self.connection.request(action, self.sTargetUrl+params, body, header)
		except:
			print "Connection Error"
			return False
		response = self.connection.getresponse()
		if response.status != 200:
			print response.status, response.reason
			return False
		else:
			#-print response.status, response.reason
			data = response.read()
			if data != '':
				self.sData = data
			else:
				return False
		return True	
	
	def connect (self, targetserver):
		self.sTargetServer=targetserver
		self.sTargetPort = "80"
		self.connection = httplib.HTTPConnection(self.sTargetServer, self.sTargetPort)	

class get_file(Thread):
	
	def __init__ (self,params,FileName,referer_url,imgBlocks=""):
		Thread.__init__(self)
		self.parms = params[params.find('?'):len(params)]
		self.referer_url = referer_url
		self.filename = FileName
		self.path = ""
		self.sTargetUrl = params[0:params.find('?')]
		self.host = params[params.find('//')+2:params.find('/',params.find('//')+2)]
		self.tarname = FileName[0:FileName.rfind('\\')].replace('\\','_')
		self.tarfilename = FileName[FileName.find('\\')+1:len(FileName)]
		self.imgBlocks = imgBlocks
		self.connect(self.host)
		
	def run(self):	
		folders = self.tarname.split('_')
		try:
			os.mkdir(TEMPFOLDER + folders[0])
		except: pass
		try:
			os.mkdir(TEMPFOLDER + folders[0] + '\\' + folders[1])
		except: pass
		if not os.path.exists(TEMPFOLDER + self.filename):
			#try:
			#	tar = tarfile.open(TEMPFOLDER + self.tarname + ".tar", "r")
			#	tar_file = tar.getmember(self.tarfilename)
			#	today = datetime.datetime.now()
			#	mtime = int(time.mktime(today.timetuple()))
			#	tar_file.mtime = mtime
			#	tar.extract(tar_file,TEMPFOLDER + self.tarname.replace('_','\\'))
			#except:
			header = {
				"Host": self.host,
				"User-Agent":"Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11",
				"Accept":"*/*",
				"Accept-Language":"de-de,de;q=0.8,en-us;q=0.5,en;q=0.3",
				"Accept-Charset":"ISO-8859-1,utf-8;q=0.7,*;q=0.7",
				"Keep-Alive":"300",
				"Proxy-Connection":"keep-alive",
				"Referer":  self.referer_url}
			params = self.parms
			body = ''
			
			if self._request("GET",params,header, body)!=True:
				return
			data = self.sData
			fName = file
			f = open(TEMPFOLDER + self.filename, 'wb')
			f.write(data)
			f.close()
			#	try:
			#		tar = tarfile.open(TEMPFOLDER + self.tarname + ".tar", "a")
			#	except:
			#		tar = tarfile.open(TEMPFOLDER + self.tarname + ".tar", "w")
			#	tar.add(TEMPFOLDER + self.filename, self.tarfilename)
			#	tar.close()
		else:
			f = TEMPFOLDER + self.filename
			today = datetime.datetime.now()
			atime = int(time.mktime(today.timetuple()))
			mtime = atime
			times = (atime,mtime)
			os.utime(f, times)
		if self.imgBlocks != "":
			self.path = TEMPFOLDER + self.filename
			self.imgBlocks.setImage(self.path)
		return
	
	def _request(self, action, params, header, body ):
		try:
			self.connection.request(action, self.sTargetUrl+params, body, header)
		except:
			print "Connection Error"
			return False
		response = self.connection.getresponse()
		if response.status != 200:
			print response.status, response.reason
			return False
		else:
			#-print response.status, response.reason
			data = response.read()
			if data != '':
				self.sData = data
			else:
				return False
		return True	
	
	def connect (self, targetserver):
		self.sTargetServer=targetserver
		self.sTargetPort = "80"
		self.connection = httplib.HTTPConnection(self.sTargetServer, self.sTargetPort)	
		

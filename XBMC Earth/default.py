#http://maps.google.com//maps?f=d&source=s_d&saddr=Offenburg&daddr=Schutterwald&hl=de&geocode=&mra=ls&output=kml&jsv=140g&sll=48.449845,7.967885&sspn=0.06638,0.263672&abauth=86e35f80:%20v72OFahWiOC_BHLC05bUP-jow8s&absince=404
#http://maps.google.com//maps?f=d&source=s_d&saddr=Offenburg&daddr=Schutterwald&hl=de&geocode=&mra=ls&output=kml
#lansinoh
#http://api.flickr.com/services/rest/?method=flickr.photos.search&format=json&api_key=7458156304b50b74b675aca223f44d28&min_upload_date=977957078&sort=interestingness-desc&bbox=13.011494%2C52.023480%2C13.911494%2C52.923480&extras=+date_taken%2C+owner_name%2C+geo%2C+o_dims%2C&per_page=20
#http://picasaweb.google.com/data/feed/api/featured?bbox=13.011494,52.023480,13.911494,52.923480&max-results=20&alt=json

#Lotta Mooser
#40°C max  - 37°Ziel
#^Bärlauch Johannis
#Basen Bad

import xbmc, xbmcgui, time, threading, datetime, os, urllib, httplib, sys, glob, random

try: Emulating = xbmcgui.Emulating
except: Emulating = False

# Script constants
__scriptname__ = "XBMC Earth"
__author__ = "MrLight"
__version__ = "0.1"
__date__ = '21-12-2008'
xbmc.output(__scriptname__ + " Version: " + __version__ + " Date: " + __date__)


# Shared resources

BASE_RESOURCE_PATH = os.path.join( os.getcwd().replace( ";", "" ), "resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )

__language__ = xbmc.Language( os.getcwd() ).getLocalizedString 

from threading import Thread

from googleearth_coordinates import  Googleearth_Coordinates
from xbmcearth_communication import *
from pic import Pic_GUI
import update 

from PIL import Image, ImageFont, ImageDraw, ImageFilter
import aggdraw

from xml.dom import minidom 
import simplejson

from global_data import *
TEMPFOLDER = os.path.join( os.getcwd().replace( ";", "" ), "temp" )



class MainClass(xbmcgui.WindowXML):
	lon = 13.411494
	lat = 52.523480
	zoom = 8
	xbmcearth_communication = Xbmcearth_communication()
	markercontainer = []
	map_size_x = 3	#Größe der angezeigten Karte (3 Tiles) muss ungerade sein
	map_size_y = 3  #Größe der angezeigten Karte (3 Tiles) muss ungerade sein
	map_pos_x_windowed = 320
	map_pos_y_windowed = 270
	pic_size_windowed = 190
	map_pos_x_full = 0
	map_pos_y_full = 0
	pic_size_full = 0
	map_pos_x = 0	#will be calculated
	map_pos_y = 0	#will be calculated
	pic_size = 0	#will be calculated
	hybrid = 1 	#enables the hybridview
	map_move = 0
	routecontainer = dict({'enable': 0, 'linestring': ''}) 
	piccontainer = dict({'enable': 0, 'url_query': '', 'url_pic': ''})
	cleanup_thread = ''
	
	
	def __init__(self, *args, **kwargs):
		global URL_satPic
		global cookie_txt
		if Emulating: 
			xbmcgui.Window.__init__(self)
		
		#self.settings = {}
		#self._initSettings(forceReset=False)
		# check for script update
		if True: #self.settings[self.SETTING_CHECK_UPDATE]:    # check for update ?
			scriptUpdated = updateScript(False, False)
		else:
			scriptUpdated = False




		#Clear cached Files
		self.cleanup_thread = file_remove(self)
		self.cleanup_thread.start()
		#Connect to GoogleMaps
		try:
			os.mkdir(TEMPFOLDER)
		except: pass
		self.connect()
		#Get maps.JS
		maps_js = self.xbmcearth_communication.get_Maps_JS(referer_url, maps_key)
		x = maps_js.find('_mSatelliteToken = "') #find CookieData
		cookie_txt = maps_js[x+20:maps_js.find('";',x+20)]
		URL_satPic = URL_satPic + "&cookie=" + cookie_txt + "&t="  #extend Sat_Pic URL
		
		#setup picsize
		w = 720
		h = 576
		w = w/self.map_size_x
		h = h/self.map_size_y
		if w>h:
			self.pic_size = int(w)
			self.map_pos_x_full = int(w)
			self.map_pos_y_full = int((float(576)-int(w))/2)
		else:
			self.pic_size = int(h)
			self.map_pos_x_full = int((1-(self.getWidth()/(self.getHeight())))*self.getWidth())
			self.map_pos_y_full = int(h)
		self.pic_size_full	= self.pic_size
		self.map_pos_x = self.map_pos_x_windowed
		self.map_pos_y = self.map_pos_y_windowed
		self.pic_size = self.pic_size_windowed
		#make ImageBlocks for Map and Sat
		#SatBlocks
		self.satBlocks = [[] for i in range(self.map_size_x)]
		for x in range(self.map_size_x):
			self.satBlocks.append(xbmcgui.ControlImage(0,0,0,0, ''))
			for y in range(self.map_size_y):
				Pic_size = self.pic_size
				Map_pos_x = (self.map_pos_x - Pic_size) + (Pic_size*x)
				Map_pos_y = (self.map_pos_y - Pic_size) + (Pic_size*y)
				self.satBlocks[x].append(xbmcgui.ControlImage(Map_pos_x,Map_pos_y,Pic_size,Pic_size, ''))
				self.addControl(self.satBlocks[x][y])
		#Overlay
		self.mapBlocks = [[] for i in range(self.map_size_x)]
		for x in range(self.map_size_x):
			self.mapBlocks.append(xbmcgui.ControlImage(0,0,0,0, ''))
			for y in range(self.map_size_y):
				Pic_size = self.pic_size
				Map_pos_x = (self.map_pos_x - Pic_size) + (Pic_size*x)
				Map_pos_y = (self.map_pos_y - Pic_size) + (Pic_size*y)
				self.mapBlocks[x].append(xbmcgui.ControlImage(Map_pos_x,Map_pos_y,Pic_size,Pic_size, ''))
				self.addControl(self.mapBlocks[x][y])

		self.route_pic = xbmcgui.ControlImage(130,80,Pic_size*3,Pic_size*3, '')
		self.addControl(self.route_pic)
		#self.makeRoute('test')

		self.drawSAT()
	
	def onInit(self):
		self.getControl(2001).setVisible(0)
		for button_id in range( 100, 106 ):
			try:
				self.getControl( button_id ).setLabel( __language__( button_id ) )
			except:
				pass
		#Start Backgroundthread
		self.background = background_thread(self)
		self.background.start()
		pass
		


			
	def onClick(self, controlID):
		#Action to map_move
		if controlID == 100:
			if self.map_move == 0:
				self.map_mov()
				self.getControl(2000).setVisible(0)
			elif self.map_move == 1:
				self.map_mov()
				self.getControl(2000).setVisible(1)
		elif controlID == 101:
			self.search_map()
		elif controlID == 102:
			self.showPanoramio()
		elif controlID == 103:
			self.showFlickr()
		elif controlID == 105:
			self.search_Route()
		elif ( 50 <= controlID <= 59 ):
			self.zoom_to_select(int(self.getCurrentListPosition()))


	def onFocus(self, controlID):
		pass
			
	def onAction(self, action):
		self.getControl(200).setLabel( str(action.getButtonCode()) )
		googleearth_coordinates = Googleearth_Coordinates()
		#main_menu active
		if self.map_move == 0:
			if action.getButtonCode() == 61467 or action.getButtonCode() == REMOTE_BACK or action.getButtonCode() == pad_button_back:
				if self.routecontainer['enable'] == 1:
					self.routecontainer['enable'] = 0
					self.getControl(2001).setVisible(0)
					self.drawSAT()
				elif self.piccontainer['enable'] == 1:
					self.piccontainer['enable'] = 0
					self.delete_markers()
					self.getControl(2001).setVisible(0)
					self.drawSAT()
				else:
					self.goodbye()
		#map_move active
		if self.map_move == 1:
			if action.getButtonCode() == 61467 or action.getButtonCode() == REMOTE_BACK or action.getButtonCode() == pad_button_back:
				self.map_mov()
				self.getControl(2000).setVisible(1)
			if action.getButtonCode() == KEYBOARD_UP or action.getButtonCode() == REMOTE_UP or action.getButtonCode() == pad_button_dpad_up:
				if maploaded == 1:
					coord_dist =[]
					coord=googleearth_coordinates.getTileRef(self.lon, self.lat, self.zoom)
					coord_dist = googleearth_coordinates.getLatLong(coord)
					self.lat = self.lat + coord_dist[3]
					#if lat > 90.0:
					#	lat -=180.0
					self.drawSAT()
			if action.getButtonCode() == KEYBOARD_DOWN or action.getButtonCode() == REMOTE_DOWN or action.getButtonCode() == pad_button_dpad_down:
				if maploaded == 1:
					coord_dist =[]
					coord=googleearth_coordinates.getTileRef(self.lon, self.lat, self.zoom)
					coord_dist = googleearth_coordinates.getLatLong(coord)
					self.lat = self.lat - coord_dist[3]
					#if lat < -90.0:
					#	lat += 180.0
					self.drawSAT()
			if action.getButtonCode() == KEYBOARD_LEFT or action.getButtonCode() == REMOTE_LEFT or action.getButtonCode() == pad_button_dpad_left:
				if maploaded == 1:
					coord_dist =[]
					coord=googleearth_coordinates.getTileRef(self.lon, self.lat, self.zoom)
					coord_dist = googleearth_coordinates.getLatLong(coord)
					self.lon = self.lon - coord_dist[2]
					#if lon < 0.0:
					#	lon +=360.0
					self.drawSAT()	
			if action.getButtonCode() == KEYBOARD_RIGHT or action.getButtonCode() == REMOTE_RIGHT or action.getButtonCode() == pad_button_dpad_right:
				if maploaded == 1:
					coord_dist =[]
					coord=googleearth_coordinates.getTileRef(self.lon, self.lat, self.zoom)
					coord_dist = googleearth_coordinates.getLatLong(coord)
					self.lon = self.lon + coord_dist[2]
					#if lon > 360.0:
					#	lon -= 360.0
					self.drawSAT()
		if self.map_move == 2:
			if action.getButtonCode() == 61467 or action.getButtonCode() == REMOTE_BACK or action.getButtonCode() == pad_button_back:
				self.map_move = 0
				try:
					self.pan_pic.setImage("")
					self.removeControl(self.pan_pic.getId())
				except:
					pass
				self.getControl(2000).setVisible(1)
		# do always
		if action.getButtonCode() == KEYBOARD_PG_DW or action.getButtonCode() == REMOTE_4 or action.getButtonCode() == pad_button_left_trigger:
			if maploaded == 1:
				self.zoom += 1
				self.getControl(200).setLabel( str(action.getButtonCode()) + " | " + str(self.zoom) )
				self.drawSAT()
		if action.getButtonCode() == KEYBOARD_PG_UP or action.getButtonCode() == REMOTE_1 or action.getButtonCode() == pad_button_right_trigger:
			if maploaded == 1:
				self.zoom -= 1
				self.getControl(200).setLabel( str(action.getButtonCode()) + " | " + str(self.zoom) )
				self.drawSAT()
		if action.getButtonCode() == KEYBOARD_INSERT or action.getButtonCode() == REMOTE_INFO or action.getButtonCode() == pad_button_white:
			if maploaded == 1:
				if self.hybrid == 1:
					self.hybrid = 2
					map_center_x = int(self.map_size_x / 2)
					map_center_y = int(self.map_size_y / 2)
					for x in range(self.map_size_x):
						for y in range(self.map_size_y):
							self.mapBlocks[x][y].setVisible(1)
							self.satBlocks[x][y].setVisible(0)
				elif self.hybrid ==2:
					self.hybrid = 3
					map_center_x = int(self.map_size_x / 2)
					map_center_y = int(self.map_size_y / 2)
					for x in range(self.map_size_x):
						for y in range(self.map_size_y):
							self.mapBlocks[x][y].setVisible(1)
							self.satBlocks[x][y].setVisible(0)
				elif self.hybrid ==3:
					self.hybrid = 0
					map_center_x = int(self.map_size_x / 2)
					map_center_y = int(self.map_size_y / 2)
					for x in range(self.map_size_x):
						for y in range(self.map_size_y):
							self.mapBlocks[x][y].setVisible(0)
							self.satBlocks[x][y].setVisible(1)
				else:
					self.hybrid = 1
					map_center_x = int(self.map_size_x / 2)
					map_center_y = int(self.map_size_y / 2)
					for x in range(self.map_size_x):
						for y in range(self.map_size_y):
							self.mapBlocks[x][y].setVisible(1)
							self.satBlocks[x][y].setVisible(1)
				self.drawHYBRID()
		
	
		
	def goodbye(self):
		global run_backgroundthread
		try:
			run_backgroundthread = 0
			self.cleanup_thread.join(1.0)
			self.background.join(1.0)
		except: 
			LOG( LOG_ERROR, self.__class__.__name__, "[%s]", sys.exc_info()[ 1 ] )
		self.close()
		
	def connect(self):
		self.xbmcearth_communication.connect("maps.google.com")
	
	#Plan a Route from A to B
	#Show virtual Keyboard for Start and Destintion
	def search_Route(self):
		self.start = ""
		self.ziel = ""
		keyboard = xbmc.Keyboard()
		keyboard.setHeading(__language__( 10001 ))
		keyboard.doModal()
		if keyboard.isConfirmed():
			search_string = ''
			search_string = keyboard.getText()
			self.connect()
			search_kml = self.xbmcearth_communication.get_Query_Place(referer_url, maps_key, search_string)
			result = self.parse_kml(search_kml)
			import chooser
			ch = chooser.GUI( "script-%s-chooser.xml" % ( __scriptname__.replace( " ", "_" ), ), os.getcwd(),  "Default", 0, choices=result["Placemarks"], descriptions=result["Placemarks"], original=-1, selection=0, list_control=1, title="Hallo" )
			self.start = ch.selection
			del ch
		keyboard = xbmc.Keyboard()
		keyboard.setHeading(__language__( 10002 ))
		keyboard.doModal()
		if keyboard.isConfirmed():
			search_string = ''
			search_string = keyboard.getText()
			self.connect()
			search_kml = self.xbmcearth_communication.get_Query_Place(referer_url, maps_key, search_string)
			result = self.parse_kml(search_kml)
			import chooser
			ch = chooser.GUI( "script-%s-chooser.xml" % ( __scriptname__.replace( " ", "_" ), ), os.getcwd(),  "Default", 0, choices=result["Placemarks"], descriptions=result["Placemarks"], original=-1, selection=0, list_control=1, title="Hallo" )
			self.ziel = ch.selection
			del ch
		self.proc_route_result(self.planRoute( self.start, self.ziel))
		self.drawSAT()	
	def planRoute(self, start, ziel):
		self.connect()
		search_kml = self.xbmcearth_communication.get_Route(referer_url,start, ziel)
		if search_kml != False:
			resultcontainer = dict()
			#self.delete_markers()
			#self.clearList()
			xmldoc = minidom.parseString(search_kml)
			resultcontainer = dict()
			#read route name
			nodelist = xmldoc.getElementsByTagName("name")
			node = nodelist[0]
			name =  node.firstChild.data.encode('latin-1', 'ignore')
			resultcontainer["name"] = name
			#read length
			nodelist = xmldoc.getElementsByTagName("Placemark")
			node = nodelist[len(nodelist)-1]
			sub_node2 = node.getElementsByTagName('description')
			for node in sub_node2:
				description = node.firstChild.data.encode('latin-1', 'ignore').replace('<br/>','\n').replace('<![CDATA[','').replace('&#160;',' ').replace(']]>',' ')
				resultcontainer["info"] = description
			index = 0
			placemark_seq = []
			resultcontainer["Placemarks"] = placemark_seq
			for node in nodelist[0:len(nodelist)-2]:
				placemark = dict()
				resultcontainer["Placemarks"].append(placemark)
				node_temp = node
				sub_node2 = node_temp.getElementsByTagName('name')
				for node in sub_node2:
					name = node.firstChild.data.encode('latin-1', 'ignore')
					resultcontainer["Placemarks"][index]["name"] = name
				sub_node2 = node_temp.getElementsByTagName('description')
				for node in sub_node2:
					description = node.firstChild.data.encode('latin-1', 'ignore').replace('<br/>','\n').replace('<![CDATA[','').replace('&#160;',' ').replace(']]>',' ')
					resultcontainer["Placemarks"][index]["info"] = description
				sub_node2 = node_temp.getElementsByTagName('text')
				#for node in sub_node2:
				#	x = node.firstChild.data.find('<img src="http://base.googlehosted.com/')
				#	if x != -1:
				#		url =  node.firstChild.data[x+10:node.firstChild.data.find('"/>',node.firstChild.data.find('<img src="http://base.googlehosted.com/'))].encode('UTF-8', 'ignore')
				#		searchresult[index][2] = url
				sub_node2 = node_temp.getElementsByTagName('coordinates')
				for node in sub_node2:
					Lon = node.firstChild.data[0:node.firstChild.data.find(',')]
					Lat = node.firstChild.data[node.firstChild.data.find(',')+1:node.firstChild.data.find(',', node.firstChild.data.find(',')+1)]
					resultcontainer["Placemarks"][index]["lon"] = float(Lon)
					resultcontainer["Placemarks"][index]["lat"] = float(Lat)
				index += 1
			nodelist = xmldoc.getElementsByTagName("GeometryCollection")
			for node in nodelist:
				node_temp = node
				self.routecontainer['linestring'] = ''
				sub_node2 = node_temp.getElementsByTagName('coordinates')
				for node in sub_node2:
					#print node.firstChild.data.encode('latin-1', 'ignore')
					self.routecontainer['linestring'] = self.routecontainer['linestring'] + node.firstChild.data.encode('latin-1', 'ignore') 
			self.routecontainer['enable'] = 1
			return resultcontainer
			
	
	def proc_route_result(self, result):
		self.delete_markers()
		#calc zoomlevel to fit
		self.fit_placemarks(result["Placemarks"])
		#make resultlist in MainGUI
		self.clearList()
		list_item = xbmcgui.ListItem(result["name"], '', '', '')
		list_item.setInfo( 'video', { "Title": result["name"], "Genre":result["info"] }) 				
		list_item.setProperty('name', urllib.quote(result["name"]))
		list_item.setProperty('lon',str(self.lon))
		list_item.setProperty('lat',str(self.lat))
		list_item.setProperty('zoom',str(self.zoom))
		self.addItem(list_item)
		for placemark in result["Placemarks"]:
			if "name" in placemark:
				pass
			else:
				placemark["name"] = 'error - no name'
			if "info" in placemark:
				pass
			else:
				placemark["info"] = ''
			list_item = xbmcgui.ListItem(placemark["name"], '', '', '')
			list_item.setInfo( 'video', { "Title": placemark["name"], "Genre": placemark["info"] }) 				
			list_item.setProperty('name', urllib.quote(placemark["name"]))
			if "lon" in placemark and "lat" in placemark:
				list_item.setProperty('lon',str(placemark["lon"]))
				list_item.setProperty('lat',str(placemark["lat"]))
			
			self.addItem(list_item)
		self.makeRoute(self.routecontainer['linestring'])
		self.getControl(2001).setVisible(1)
	
	#Panoramio Support
	def showPanoramio(self):
		self.proc_panoramio_result(self.getPanoramio(0,20))
		self.piccontainer["enable"] = 1
		self.piccontainer["type"] = "Panoramio"
		
	def getPanoramio(self, start, size):
		Lon = self.lon
		Lat = self.lat
		Zoom = self.zoom
		googleearth_coordinates = Googleearth_Coordinates()
		coord=googleearth_coordinates.getTileRef(Lon, Lat, Zoom)
		coord_dist =[]
		coord_dist = googleearth_coordinates.getLatLong(coord)
		#maplist = []
		map_center_x = int(self.map_size_x / 2)
		map_center_y = int(self.map_size_y / 2)
		self.connect()
		Lon = (self.lon - coord_dist[2]*map_center_x)+coord_dist[2]
		Lat = (self.lat + coord_dist[3]*map_center_y)-coord_dist[3]					
		coord=googleearth_coordinates.getTileRef(Lon, Lat, Zoom)
		coord_dist_min = googleearth_coordinates.getLatLong(coord)
		Lon = (self.lon - coord_dist[2]*map_center_x)+coord_dist[2]*2
		Lat = (self.lat + coord_dist[3]*map_center_y)-coord_dist[3]*2					
		coord=googleearth_coordinates.getTileRef(Lon, Lat, Zoom)
		coord_dist_max = googleearth_coordinates.getLatLong(coord)
		result = simplejson.loads(self.xbmcearth_communication.get_Panoramio(referer_url,"?order=popularity&set=public&from="+str(start)+"&to="+str(start+size)+"&minx="+ str(coord_dist_min[0]-coord_dist_min[2]) +"&miny=" + str(coord_dist_max[1]-coord_dist_max[3]) + "&maxx="+str(coord_dist_max[0]+coord_dist_max[2])+"&maxy="+str(coord_dist_min[1]+coord_dist_min[3]*2)+"&size=medium"))
		index = 0
		resultcontainer = dict()
		resultcontainer["count"] = result['count']
		resultcontainer["start"] = start + size
		resultcontainer["size"] = size
		results = result['photos']
		placemark_seq = []
		resultcontainer["Placemarks"] = placemark_seq
		for photos in results:
			placemark = dict()
			resultcontainer["Placemarks"].append(placemark)
			resultcontainer["Placemarks"][index]["name"] = photos["photo_title"]
			resultcontainer["Placemarks"][index]["photo_id"] = photos["photo_id"]
			resultcontainer["Placemarks"][index]["photo_file_url"] = photos["photo_file_url"]
			resultcontainer["Placemarks"][index]["lon"] = photos["longitude"]
			resultcontainer["Placemarks"][index]["lat"] = photos["latitude"]
			resultcontainer["Placemarks"][index]["width"] = photos["width"]
			resultcontainer["Placemarks"][index]["height"] = photos["height"]
			resultcontainer["Placemarks"][index]["upload_date"] = photos["upload_date"]
			resultcontainer["Placemarks"][index]["owner_name"] = photos["owner_name"]
			index += 1
		return resultcontainer
	
	def proc_panoramio_result(self, result):
		self.clearList()
		self.delete_markers()
		for photo in result["Placemarks"]:	
			current = get_file(photo["photo_file_url"].replace("medium","square"), "Panoramio\\small\\sm"+str(photo["photo_id"])+".jpg", referer_url)
			current.start()
			current.join(1000)
			list_item = xbmcgui.ListItem(photo["name"], '', "", TEMPFOLDER + "\\Panoramio\\small\\sm"+str(photo["photo_id"])+".jpg")
			list_item.setInfo( 'video', { "Title": photo["name"], "Genre": "Upload Date: " + photo["upload_date"] + " - Owner: " + photo["owner_name"]}) 				
			list_item.setProperty('Piclink', TEMPFOLDER + "\\Panoramio\\medium\\m"+str(photo["photo_id"])+".jpg")
			list_item.setProperty('Title', urllib.quote(photo["name"]))
			list_item.setProperty('Genre', urllib.quote("Upload Date: " + photo["upload_date"] + " - Owner: " + photo["owner_name"]))
			list_item.setProperty('lon',str(photo["lon"]))
			list_item.setProperty('lat',str(photo["lat"]))
			list_item.setProperty('photo_file_url',photo["photo_file_url"])
			list_item.setProperty('photo_id',str(photo["photo_id"]))
			list_item.setProperty('width',str(photo["width"]))
			list_item.setProperty('height',str(photo["height"]))
			list_item.setProperty('type',"Panoramio")
			self.markercontainer.append(marker(self, float(photo["lat"]), float(photo["lon"]), TEMPFOLDER + "\\Panoramio\\small\\sm"+str(photo["photo_id"])+".jpg",16,32,32,32))
			self.addItem(list_item)
		if  result["count"] > result["start"]:
			list_item = xbmcgui.ListItem(__language__( 10003 ) % (str(result["size"])), '', "", "")
			list_item.setInfo( 'video', { "Title": __language__( 10003 ) % (str(result["size"])), "Genre": str(result["count"]) + " Photos"})
			list_item.setProperty('type',"Panoramio")
			list_item.setProperty('next',"next")
			list_item.setProperty('start',str(result["start"]))
			list_item.setProperty('size',str(result["size"]))
			self.addItem(list_item)
		list_item = xbmcgui.ListItem(photo["name"], '', "", TEMPFOLDER + "\\Panoramio\\small\\sm"+str(photo["photo_id"])+".jpg")
		self.getControl(2001).setVisible(1)

			
	#Flickr Support
	def showFlickr(self):
		self.proc_flickr_result(self.getFlickr_bbox(1,20))
		self.piccontainer["enable"] = 1
		self.piccontainer["type"] = "Flickr"
	
	def getFlickr_bbox(self, page, size):
		Lon = self.lon
		Lat = self.lat
		Zoom = self.zoom
		googleearth_coordinates = Googleearth_Coordinates()
		coord=googleearth_coordinates.getTileRef(Lon, Lat, Zoom)
		coord_dist =[]
		coord_dist = googleearth_coordinates.getLatLong(coord)
		#maplist = []
		map_center_x = int(self.map_size_x / 2)
		map_center_y = int(self.map_size_y / 2)
		self.connect()
		Lon = (self.lon - coord_dist[2]*map_center_x)+coord_dist[2]
		Lat = (self.lat + coord_dist[3]*map_center_y)-coord_dist[3]					
		coord=googleearth_coordinates.getTileRef(Lon, Lat, Zoom)
		coord_dist_min = googleearth_coordinates.getLatLong(coord)
		Lon = (self.lon - coord_dist[2]*map_center_x)+coord_dist[2]*2
		Lat = (self.lat + coord_dist[3]*map_center_y)-coord_dist[3]*2					
		coord=googleearth_coordinates.getTileRef(Lon, Lat, Zoom)
		coord_dist_max = googleearth_coordinates.getLatLong(coord)
		self.xbmcearth_communication.connect("api.flickr.com")
		#result = self.xbmcearth_communication.get_Flickr("","?method=flickr.photos.search&format=json&api_key=7458156304b50b74b675aca223f44d28&min_upload_date=977957078&sort= \"interestingness-desc\"&bbox=\"13.011494,52.023480,13.911494,52.923480\"&per_page=20")

		#result = self.xbmcearth_communication.get_Flickr(referer_url,"?method=flickr.photos.search&format=json&api_key=" + flickr_Key + "&min_upload_date=977957078&sort=interestingness-desc&bbox="+str(coord_dist_min[0]-coord_dist_min[2])+","+str(coord_dist_max[1]-coord_dist_max[3])+","+str(coord_dist_max[0]+coord_dist_max[2])+","+str(coord_dist_min[1]+coord_dist_min[3]*2)+"&extras=+date_taken%2C+owner_name%2C+geo%2C&per_page="+str(page)+"&per_page="+str(size))
		result = self.xbmcearth_communication.get_Flickr(referer_url,"?method=flickr.photos.search&format=json&api_key=" + flickr_Key + "&min_upload_date=977957078&sort=interestingness-desc&bbox="+str(coord_dist_min[0]-coord_dist_min[2])+","+str(coord_dist_max[1]-coord_dist_max[3])+","+str(coord_dist_max[0]+coord_dist_max[2])+","+str(coord_dist_min[1]+coord_dist_min[3]*2)+"&extras=+date_taken%2C+owner_name%2C+geo%2C&page="+str(page)+"&per_page="+str(size))
		result = result.replace("jsonFlickrApi(","").replace(")","")
		result = simplejson.loads(result)
		#result = simplejson.loads(self.xbmcearth_communication.get_Panoramio(referer_url,"?order=popularity&set=public&from="+str(start)+"&to="+str(start+size)+"&minx="+ str(coord_dist_min[0]-coord_dist_min[2]) +"&miny=" + str(coord_dist_max[1]-coord_dist_max[3]) + "&maxx="+str(coord_dist_max[0]+coord_dist_max[2])+"&maxy="+str(coord_dist_min[1]+coord_dist_min[3]*2)+"&size=medium"))
		index = 0
		results = result['photos']
		resultcontainer = dict()
		resultcontainer["count"] = results['total']
		resultcontainer["start"] = page + 1
		resultcontainer["size"] = size
		results = results['photo']
		placemark_seq = []
		resultcontainer["Placemarks"] = placemark_seq
		for photos in results:
			placemark = dict()
			resultcontainer["Placemarks"].append(placemark)
			resultcontainer["Placemarks"][index]["name"] = photos["title"]
			resultcontainer["Placemarks"][index]["photo_id"] = photos["id"]
			#resultcontainer["Placemarks"][index]["photo_file_url"] = photos["photo_file_url"]
			resultcontainer["Placemarks"][index]["lon"] = photos["longitude"]
			resultcontainer["Placemarks"][index]["lat"] = photos["latitude"]
			#resultcontainer["Placemarks"][index]["width"] = photos["width"]
			#resultcontainer["Placemarks"][index]["height"] = photos["height"]
			resultcontainer["Placemarks"][index]["upload_date"] = photos["datetaken"]
			resultcontainer["Placemarks"][index]["owner_name"] = photos["ownername"]
			resultcontainer["Placemarks"][index]["farm"] = photos["farm"]
			resultcontainer["Placemarks"][index]["server"] = photos["server"]
			resultcontainer["Placemarks"][index]["secret"] = photos["secret"]
			index += 1
		return resultcontainer
		
	def proc_flickr_result(self, result):
		self.clearList()
		self.delete_markers()
		for photo in result["Placemarks"]:	
			current = get_file("http://farm"+str(photo["farm"])+".static.flickr.com/"+str(photo["server"])+"/"+str(photo["photo_id"])+"_"+str(photo["secret"])+"_s.jpg", "Flickr\\small\\"+str(photo["photo_id"])+".jpg", referer_url)
			current.start()
			current.join(1000)
			list_item = xbmcgui.ListItem(photo["name"], '', "", TEMPFOLDER + "\\Flickr\\small\\"+str(photo["photo_id"])+".jpg")
			list_item.setInfo( 'video', { "Title": photo["name"], "Genre": "Date taken: " + photo["upload_date"] + " - Owner: " + photo["owner_name"]}) 				
			list_item.setProperty('Piclink', TEMPFOLDER + "\\Panoramio\\medium\\"+str(photo["photo_id"])+".jpg")
			list_item.setProperty('Title', urllib.quote(photo["name"]))
			list_item.setProperty('Genre', urllib.quote("Date taken: " + photo["upload_date"] + " - Owner: " + photo["owner_name"]))
			list_item.setProperty('lon',str(photo["lon"]))
			list_item.setProperty('lat',str(photo["lat"]))
			list_item.setProperty('farm',str(photo["farm"]))
			list_item.setProperty('photo_id',str(photo["photo_id"]))
			list_item.setProperty('server',str(photo["server"]))
			list_item.setProperty('secret',str(photo["secret"]))
			list_item.setProperty('type',"flickr")
			self.markercontainer.append(marker(self, float(photo["lat"]), float(photo["lon"]), TEMPFOLDER + "\\Flickr\\small\\"+str(photo["photo_id"])+".jpg",16,32,32,32))
			self.addItem(list_item)
		if  result["count"] > result["start"]*result["size"]:
			list_item = xbmcgui.ListItem(__language__( 10003 ) % (str(result["size"])), '', "", "")
			list_item.setInfo( 'video', { "Title": __language__( 10003 ) % (str(result["size"])), "Genre": str(result["count"]) + " Photos"})
			list_item.setProperty('type',"flickr")
			list_item.setProperty('next',"next")
			list_item.setProperty('start',str(result["start"]))
			list_item.setProperty('size',str(result["size"]))
			self.addItem(list_item)
		list_item = xbmcgui.ListItem(photo["name"], '', "", TEMPFOLDER + "\\Flickr\\small\\"+str(photo["photo_id"])+".jpg")
		self.getControl(2001).setVisible(1)
	#Search Support
	def search_map(self, key_txt = ''):
		keyboard = xbmc.Keyboard(key_txt)
		keyboard.doModal()
		if keyboard.isConfirmed():
			search_string = ''
			search_string = keyboard.getText()
			self.connect()
			search_kml = self.xbmcearth_communication.get_Query_Place(referer_url, maps_key, search_string)
			result = self.parse_kml(search_kml)
			self.proc_search_result(result)
			self.drawSAT()

	
	def proc_search_result(self, result):
		self.delete_markers()
		#Look at -> Single result zoom to result
		if "lookAT_lon" in result and "lookAT_lat" in result	:
			self.lon = result["lookAT_lon"]
			self.lat = result["lookAT_lat"]
		else:
		#more than one result -> calc zoomlevel to fit
			self.fit_placemarks(result["Placemarks"])
		#make resultlist in MainGUI
		self.clearList()
		index = 0
		for placemark in result["Placemarks"]:
			if "name" in placemark:
				pass
			else:
				placemark["name"] = 'error - no name'
			if "info" in placemark:
				pass
			else:
				placemark["info"] = ''
			index += 1
			if len(result["Placemarks"]) > 1:
				if "lon" in placemark and "lat" in placemark:
					self.markercontainer.append(marker(self, float(placemark["lat"]), float(placemark["lon"]), BASE_RESOURCE_PATH + '\\skins\\Default\\media\\icon' + str(index) + '.png',12,38,24,38))
				list_item = xbmcgui.ListItem(placemark["name"], '', BASE_RESOURCE_PATH + '\\skins\\Default\\media\\icon' + str(index) + '.png', BASE_RESOURCE_PATH + '\\skins\\Default\\media\\icon' + str(index) + '.png')
			else:
				if "lon" in placemark and "lat" in placemark:
					self.markercontainer.append(marker(self, float(placemark["lat"]), float(placemark["lon"])))
					self.zoom = 1
				list_item = xbmcgui.ListItem(placemark["name"], '', BASE_RESOURCE_PATH + '\\skins\\Default\\media\\arrow.png', BASE_RESOURCE_PATH + '\\skins\\Default\\media\\arrow.png')
			list_item.setInfo( 'video', { "Title": placemark["name"], "Genre": placemark["info"] }) 				
			list_item.setProperty('name', urllib.quote(placemark["name"]))
			if "lon" in placemark and "lat" in placemark:
				list_item.setProperty('lon',str(placemark["lon"]))
				list_item.setProperty('lat',str(placemark["lat"]))
			
			self.addItem(list_item)
		self.getControl(2001).setVisible(1)
		
		
	def fit_placemarks(self, placemarks):
		min_lon = 999.9
		max_lon = -999.9
		min_lat = 999.9
		max_lat = -999.9
		for placemark in placemarks:
			if "lon" in placemark and "lat" in placemark:
				if placemark["lon"] < min_lon:
					min_lon = placemark["lon"]
				if placemark["lon"] > max_lon:
					max_lon = placemark["lon"]
				if placemark["lat"] < min_lat:
					min_lat = placemark["lat"]
				if placemark["lat"] > max_lat:
					max_lat = placemark["lat"]
		if min_lon != 999.9 and max_lon != -999.9 and min_lat != 999.0 and max_lat != -999.0:
			self.lon = min_lon + ((max_lon-min_lon) / 2.0)
			self.lat = min_lat + ((max_lat-min_lat) / 2.0)
			googleearth_coordinates = Googleearth_Coordinates()
			coord=googleearth_coordinates.getTileRef(self.lon, self.lat, 0)
			coord_dist = googleearth_coordinates.getLatLong(coord)
			index = 1
			while ((max_lon - min_lon) > (coord_dist[2]*self.map_size_x) and (max_lat - min_lat) > (coord_dist[3]*self.map_size_y)):
				coord=googleearth_coordinates.getTileRef(self.lon, self.lat, index)
				coord_dist = googleearth_coordinates.getLatLong(coord)
				index += 1
			self.zoom = index

	def parse_kml(self, kml):
		if kml != False:
			resultcontainer = dict()
			xmldoc = minidom.parseString(kml)
			nodelist = xmldoc.getElementsByTagName("LookAt")
			for node in nodelist:
				node_temp = node
				sub_node2 = node_temp.getElementsByTagName('longitude')
				for node in sub_node2:
					Lon = float(node.firstChild.data)
					resultcontainer["lookAT_lon"] = Lon
				sub_node2 = node_temp.getElementsByTagName('latitude')
				for node in sub_node2:
					Lat = float(node.firstChild.data)
					resultcontainer["lookAT_lat"] = Lat
				sub_node2 = node_temp.getElementsByTagName('range')
				for node in sub_node2:
					Range =  float(node.firstChild.data)
					resultcontainer["lookAT_Range"] = Range
			nodelist = xmldoc.getElementsByTagName("Placemark")
			index = 0
			placemark_seq = []
			resultcontainer["Placemarks"] = placemark_seq
			for node in nodelist:
				placemark = dict()
				resultcontainer["Placemarks"].append(placemark)
				node_temp = node
				sub_node2 = node_temp.getElementsByTagName('name')
				for node in sub_node2:
					name = node.firstChild.data.encode('latin-1', 'ignore')
					resultcontainer["Placemarks"][index]["name"] = name
				sub_node2 = node_temp.getElementsByTagName('address')
				for node in sub_node2:
					address = node.firstChild.data.encode('latin-1', 'ignore').replace('<br/>','\n')
					resultcontainer["Placemarks"][index]["info"] = address
				sub_node2 = node_temp.getElementsByTagName('text')
				for node in sub_node2:
					x = node.firstChild.data.find('<img src="http://base.googlehosted.com/')
					if x != -1:
						url =  node.firstChild.data[x+10:node.firstChild.data.find('"/>',node.firstChild.data.find('<img src="http://base.googlehosted.com/'))].encode('UTF-8', 'ignore')
						resultcontainer["Placemarks"][index]["url"] = url
				sub_node2 = node_temp.getElementsByTagName('coordinates')
				for node in sub_node2:
					Lon = node.firstChild.data[0:node.firstChild.data.find(',')]
					Lat = node.firstChild.data[node.firstChild.data.find(',')+1:node.firstChild.data.find(',', node.firstChild.data.find(',')+1)]
					resultcontainer["Placemarks"][index]["lon"] = float(Lon)
					resultcontainer["Placemarks"][index]["lat"] = float(Lat)
				index += 1
			return resultcontainer
		
	def zoom_to_select(self, index):
		lon_temp = self.lon
		lat_temp = self.lat
		zoom_temp = self.zoom
		if self.getListItem(self.getCurrentListPosition()).getProperty('type')  == "Panoramio": 
			#Panoramio
			self.zoom_to_panoramio()			
		elif self.getListItem(self.getCurrentListPosition()).getProperty('type')  == "flickr":
			#FLICKR
			self.zoom_to_flickr()		
		elif self.getListItem(self.getCurrentListPosition()).getProperty('lon') != '' and self.getListItem(self.getCurrentListPosition()).getProperty('lat') != '':
			self.lon = float(self.getListItem(self.getCurrentListPosition()).getProperty('lon'))
			self.lat = float(self.getListItem(self.getCurrentListPosition()).getProperty('lat'))
			if self.getListItem(self.getCurrentListPosition()).getProperty('zoom') != '':
				self.zoom = int(self.getListItem(self.getCurrentListPosition()).getProperty('zoom'))
			elif self.zoom > 2:
				self.zoom = 2
		else:
			self.search_map(urllib.unquote(self.getListItem(self.getCurrentListPosition()).getProperty('name')))
			pass
		self.lon = lon_temp
		self.lat = lat_temp
		self.zoom = zoom_temp
		self.drawSAT()

	def zoom_to_panoramio(self):
		if self.getListItem(self.getCurrentListPosition()).getProperty('next')  == "next":
			self.proc_panoramio_result(self.getPanoramio(int(self.getListItem(self.getCurrentListPosition()).getProperty('start')),int(self.getListItem(self.getCurrentListPosition()).getProperty('size')) ))
			pass
		else:
			self.lon = float(self.getListItem(self.getCurrentListPosition()).getProperty('lon'))
			self.lat = float(self.getListItem(self.getCurrentListPosition()).getProperty('lat'))
			if self.getListItem(self.getCurrentListPosition()).getProperty('zoom') != '':
				self.zoom = int(self.getListItem(self.getCurrentListPosition()).getProperty('zoom'))
			elif self.zoom > 2:
				self.zoom = 2
			if self.getListItem(self.getCurrentListPosition()).getProperty('type')  == "Panoramio":
				if self.getListItem(self.getCurrentListPosition()).getProperty('photo_file_url') != '' and self.getListItem(self.getCurrentListPosition()).getProperty('width') != '' and self.getListItem(self.getCurrentListPosition()).getProperty('height') != '' and self.getListItem(self.getCurrentListPosition()).getProperty('photo_id') != '':
					self.getControl(2000).setVisible(0)
					#self.map_move = 2
					googleearth_coordinates = Googleearth_Coordinates()
					coord=googleearth_coordinates.getTileRef(self.lon, self.lat, self.zoom)
					coord_dist = googleearth_coordinates.getLatLong(coord)
					self.lon = self.lon - coord_dist[2]
					self.drawSAT()
					current = get_file(self.getListItem(self.getCurrentListPosition()).getProperty('photo_file_url'), "Panoramio\\medium\\m" + self.getListItem(self.getCurrentListPosition()).getProperty('photo_id') + ".jpg", referer_url)
					current.start()
					current.join(1000)
					cpic = Pic_GUI("script-%s-pic.xml" % ( __scriptname__.replace( " ", "_" ), ), os.getcwd(), "Default", 0,pic=TEMPFOLDER + "\\Panoramio\\medium\\m"+self.getListItem(self.getCurrentListPosition()).getProperty('photo_id')+".jpg", width=self.getListItem(self.getCurrentListPosition()).getProperty('width'), height=self.getListItem(self.getCurrentListPosition()).getProperty('height'), mainWindow = self)
					del cpic
					self.getControl(2000).setVisible(1)
	
	def zoom_to_flickr(self):
		if self.getListItem(self.getCurrentListPosition()).getProperty('next')  == "next":
			self.proc_flickr_result(self.getFlickr_bbox(int(self.getListItem(self.getCurrentListPosition()).getProperty('start')),int(self.getListItem(self.getCurrentListPosition()).getProperty('size')) ))
			pass
		else:
			self.lon = float(self.getListItem(self.getCurrentListPosition()).getProperty('lon'))
			self.lat = float(self.getListItem(self.getCurrentListPosition()).getProperty('lat'))
			if self.getListItem(self.getCurrentListPosition()).getProperty('zoom') != '':
				self.zoom = int(self.getListItem(self.getCurrentListPosition()).getProperty('zoom'))
			elif self.zoom > 2:
				self.zoom = 2
			if self.getListItem(self.getCurrentListPosition()).getProperty('type')  == "flickr":
				if self.getListItem(self.getCurrentListPosition()).getProperty('server') != '' and self.getListItem(self.getCurrentListPosition()).getProperty('secret') != '' and self.getListItem(self.getCurrentListPosition()).getProperty('farm') != '' and self.getListItem(self.getCurrentListPosition()).getProperty('photo_id') != '':
					self.getControl(2000).setVisible(0)
					#self.map_move = 2
					googleearth_coordinates = Googleearth_Coordinates()
					coord=googleearth_coordinates.getTileRef(self.lon, self.lat, self.zoom)
					coord_dist = googleearth_coordinates.getLatLong(coord)
					self.lon = self.lon - coord_dist[2]
					self.drawSAT()
					self.xbmcearth_communication.connect("farm"+str(self.getListItem(self.getCurrentListPosition()).getProperty('farm'))+".static.flickr.com")
					current = get_file("http://farm"+str(self.getListItem(self.getCurrentListPosition()).getProperty('farm'))+".static.flickr.com/"+str(self.getListItem(self.getCurrentListPosition()).getProperty('server'))+"/"+str(self.getListItem(self.getCurrentListPosition()).getProperty('photo_id'))+"_"+str(self.getListItem(self.getCurrentListPosition()).getProperty('secret'))+".jpg", "Flickr\\medium\\"+str(self.getListItem(self.getCurrentListPosition()).getProperty('photo_id'))+".jpg", referer_url)
					current.start()
					current.join(1000)
					im = Image.open(TEMPFOLDER + "\\Flickr\\medium\\"+self.getListItem(self.getCurrentListPosition()).getProperty('photo_id')+".jpg")
					size = im.size
					cpic = Pic_GUI("script-%s-pic.xml" % ( __scriptname__.replace( " ", "_" ), ), os.getcwd(), "Default", 0,pic=TEMPFOLDER + "\\Flickr\\medium\\"+self.getListItem(self.getCurrentListPosition()).getProperty('photo_id')+".jpg", width=size[0], height=size[1], mainWindow = self)
					del cpic
					self.getControl(2000).setVisible(1)
	#handle map	
	def map_mov(self):
		if self.map_move == 0:
			self.pic_size = self.pic_size_full
			self.map_move = 1
			#Move Map to Fullscreen
			for x in range(self.map_size_x):
				for y in range(self.map_size_y):
					Pic_size = self.pic_size
					Map_pos_x = (self.map_pos_x_full - Pic_size) + (Pic_size*x)
					Map_pos_y = (self.map_pos_y_full - Pic_size) + (Pic_size*y)
					self.satBlocks[x][y].setPosition(Map_pos_x,Map_pos_y)
					self.mapBlocks[x][y].setPosition(Map_pos_x,Map_pos_y)
					self.satBlocks[x][y].setWidth(Pic_size)
					self.satBlocks[x][y].setHeight(Pic_size)
					self.mapBlocks[x][y].setWidth(Pic_size)
					self.mapBlocks[x][y].setHeight(Pic_size)
			self.redraw_markers()
			self.route_pic.setPosition(self.map_pos_x_full - Pic_size,self.map_pos_y_full - Pic_size)
			self.route_pic.setHeight(Pic_size*3)
			self.route_pic.setWidth(Pic_size*3)
		else:
			self.map_move = 0
			self.pic_size = self.pic_size_windowed
			#Move Map to Window
			for x in range(self.map_size_x):
				for y in range(self.map_size_y):
					Pic_size = self.pic_size
					Map_pos_x = (self.map_pos_x_windowed - Pic_size) + (Pic_size*x)
					Map_pos_y = (self.map_pos_y_windowed - Pic_size) + (Pic_size*y)
					self.satBlocks[x][y].setPosition(Map_pos_x,Map_pos_y)
					self.mapBlocks[x][y].setPosition(Map_pos_x,Map_pos_y)
					self.satBlocks[x][y].setWidth(Pic_size)
					self.satBlocks[x][y].setHeight(Pic_size)
					self.mapBlocks[x][y].setWidth(Pic_size)
					self.mapBlocks[x][y].setHeight(Pic_size)
			self.route_pic.setPosition(self.map_pos_x_windowed - Pic_size,self.map_pos_y_windowed - Pic_size)
			self.route_pic.setHeight(Pic_size*3)
			self.route_pic.setWidth(Pic_size*3)
			self.redraw_markers()
				
	def drawHYBRID(self):
		current = draw_map(self,self.mapBlocks)
		current.start()
		current.join()
		
	def drawSAT(self):
		sat = draw_sat(self,self.satBlocks)
		sat.start()
		map = draw_map(self,self.mapBlocks)
		map.start()
		self.redraw_markers()
		sat.join()
		map.join()
		if self.routecontainer['enable'] == 1:
			self.makeRoute(self.routecontainer['linestring'])
		else:
			self.route_pic.setImage('')
		#self.makeRoute('')
		
	def redraw_markers(self):
		for x in range(len(self.markercontainer)):
			self.markercontainer[x].redraw_Marker()
			
	def pulse_markers(self,pulse):
		for x in range(len(self.markercontainer)):
			if pulse == x:
				self.markercontainer[x].pulse_Marker(1)		
			else:
				self.markercontainer[x].pulse_Marker(0)		
			
	def delete_markers(self):
		while len(self.markercontainer) > 0:
			self.markercontainer.pop()
			
	def makeRoute(self, LineString ):
		text = 'test-string'
		fnt = BASE_RESOURCE_PATH + '\\skins\\Default\\media\\1.ttf'
		fnt_sz = 80
		fmt='PNG'
		font = ImageFont.truetype(fnt,fnt_sz)
		dim = font.getsize(text)
		im = Image.new('RGBA', (self.map_size_x*self.pic_size,self.map_size_y*self.pic_size), (0,0,0,0))
		d = ImageDraw.Draw(im)
		x, y = im.size
		d = aggdraw.Draw(im)
		p = aggdraw.Pen("blue", 5, 180)
		path = aggdraw.Path()
		line = LineString.split(' ')
		for point in line:
			if len(point) > 0:
				point_lon = float(point[0:point.find(',')])
				point_lat = float(point[point.find(',')+1:point.find(',', point.find(',')+1)])
				pos = self.get_current_POS(point_lon,point_lat)
				path.lineto(pos[0],pos[1])
		if self.map_move == 1:
			d.path((0,75),path,p)
		else:
			d.path((-130,-80),path,p)
		d.flush()
		
		#d.text((3,3), text, font=font, fill=(r(0,255),r(0,255),r(0,255),r(128,255)))
		im = im.filter(ImageFilter.EDGE_ENHANCE_MORE)
		# write image to filesystem
		im.save(TEMPFOLDER + '\\Route\\Route.png', format=fmt,**{"optimize":1})
		self.route_pic.setImage('')
		self.route_pic.setImage(TEMPFOLDER + '\\Route\\Route.png')
		#self.route_pic.setImage(TEMPFOLDER + '\\test.png')
		
	
	def get_current_POS(self, lon_marker, lat_marker):
		self.x_offset = 0
		self.y_offset = 0
		self.x_size = 1
		self.y_size = 1
		self.lat_marker = lat_marker
		self.lon_marker = lon_marker
		googleearth_coordinates = Googleearth_Coordinates()
		coord=googleearth_coordinates.getTileRef(self.lon, self.lat, self.zoom)
		self.coord_dist = googleearth_coordinates.getLatLong(coord)
		map_center_x = int(self.map_size_x / 2)
		map_center_y = int(self.map_size_y / 2)
		self.pos = self.satBlocks[map_center_x][map_center_y].getPosition()
		self.x_res = self.coord_dist[2]/self.pic_size
		self.y_res = self.coord_dist[3]/self.pic_size
		lon_marker = self.lon_marker-self.coord_dist[0]
		lat_marker = self.lat_marker-self.coord_dist[1]
		gui_pos = []
		gui_pos.append(self.pos[0]+int((lon_marker/self.x_res))-self.x_offset)
		gui_pos.append(self.pos[1]+(self.pic_size)-int((lat_marker/self.y_res))-self.y_offset)
		return gui_pos

	
class marker:
	x_res = 0.0
	y_res = 0.0
	pos = []
	coord_dist = []
	lat_marker = 0.0
	lon_marker = 0.0
	def __init__ (self,window, lat_marker, lon_marker, pic_path =  BASE_RESOURCE_PATH + '\\skins\\Default\\media\\arrow.png', x_offset=8,y_offset=39, x_size=34,y_size=39):
		self.window = window
		self.lat_marker = lat_marker
		self.lon_marker = lon_marker
		self.pic_path = pic_path
		self.x_offset = x_offset
		self.y_offset = y_offset
		self.x_size = x_size
		self.y_size = y_size
		self.add_Marker()
		
	def add_Marker(self):
		pos = self.get_current_POS()
		self.marker_pic = xbmcgui.ControlImage(pos[0],pos[1],self.x_size,self.y_size, self.pic_path)
		self.window.addControl(self.marker_pic)
	
	def pulse_Marker(self, on_off):
		if on_off == 1:
			self.marker_pic.setAnimations([('conditional', 'effect=zoom pulse=true start=100 end=120 center=auto time=1000 condition=Control.HasFocus(50)')])
		else:
			self.marker_pic.setAnimations([('conditional', 'effect=zoom start=100 end=100 center=auto time=1000 condition=Control.HasFocus(50)')])

		
	def redraw_Marker(self):
		pos = self.get_current_POS()
		self.marker_pic.setPosition(pos[0],pos[1])
		if pos[2] == 0:
			self.marker_pic.setVisible(0)
		else:
			self.marker_pic.setVisible(1)
		
	def get_current_POS(self):
		googleearth_coordinates = Googleearth_Coordinates()
		coord=googleearth_coordinates.getTileRef(self.window.lon, self.window.lat, self.window.zoom)
		self.coord_dist = googleearth_coordinates.getLatLong(coord)
		map_center_x = int(self.window.map_size_x / 2)
		map_center_y = int(self.window.map_size_y / 2)
		self.pos = self.window.satBlocks[map_center_x][map_center_y].getPosition()
		self.x_res = self.coord_dist[2]/self.window.pic_size
		self.y_res = self.coord_dist[3]/self.window.pic_size
		lon_marker = self.lon_marker-self.coord_dist[0]
		lat_marker = self.lat_marker-self.coord_dist[1]
		gui_pos = []
		gui_pos.append(self.pos[0]+int((lon_marker/self.x_res))-self.x_offset)
		gui_pos.append(self.pos[1]+(self.window.pic_size)-int((lat_marker/self.y_res))-self.y_offset)
		gui_pos.append(1) #draw Marker =1 ; hideMarker = 0
		# check if marker is in window
		pos = self.window.satBlocks[0][0].getPosition()
		if gui_pos[0] < pos[0] or gui_pos[1] < pos[1]:
			gui_pos[2] = 0
		pos = self.window.satBlocks[self.window.map_size_x-1][self.window.map_size_y-1].getPosition()
		if gui_pos[0] > (pos[0] + self.window.pic_size) or gui_pos[1] > (pos[0] + self.window.pic_size):
			gui_pos[2] = 0
		return gui_pos
		
	def __del__(self):
		self.window.removeControl(self.marker_pic)
		pass

class draw_sat(Thread):
	xbmcearth_communication = Xbmcearth_communication()
	def __init__ (self, window, satBlocks):
		Thread.__init__(self)
		self.window = window
		self.satBlocks = satBlocks


	def run(self):
		global maploaded
		maploaded = 0
		googleearth_coordinates = Googleearth_Coordinates()
		Lon = self.window.lon
		Lat = self.window.lat
		Zoom = self.window.zoom
		coord=googleearth_coordinates.getTileRef(Lon, Lat, Zoom)
		tileCoord = []
		tileCoord = googleearth_coordinates.getTileCoord(Lon, Lat, Zoom-1)
		resultset =[]
		coord_dist = googleearth_coordinates.getLatLong(coord)
		
		#/maps?spn=0.008115,0.021458&t=k&z=15&key=ABQIAAAAnyP-GOJDhG7H7ozm0RRsCBSiQ_eECfBHgA9cMSxRoMYUiueUzxSinT-_iJIghikcXgs_lmKq8_i5pQ&vp=50.927032,11.601734&ev=p&v=24
		spn = str(coord_dist[2])+','+str(coord_dist[3])
		t = 'k'
		z = str(Zoom)
		vp = str(coord_dist[0]) + ',' + str(coord_dist[1])
		ev = 'p'
		v = '24'
		
		self.xbmcearth_communication.connect("maps.google.com")
		copyright_xml = self.xbmcearth_communication.get_Maps_Copyright(referer_url, maps_key, spn, t, z, vp, ev, v)
		
		satlist = []
		map_center_x = int(self.window.map_size_x / 2)
		map_center_y = int(self.window.map_size_y / 2)
		for x in range(self.window.map_size_x):
			for y in range(self.window.map_size_y):
				Lon = (self.window.lon - coord_dist[2]*map_center_x)+coord_dist[2]*x
				Lat = (self.window.lat + coord_dist[3]*map_center_y)-coord_dist[3]*y
				#if Lon > 360.0:
				#	Lon -= 360.0
				#elif Lon < 0.0:
				#	Lon += 360.0
				#if Lat < -90.0:
				#	Lat += 180.0
				#elif Lat > 90.0:
				#	Lat -= 180.0u
				coord=googleearth_coordinates.getTileRef(Lon, Lat, Zoom)
				current = get_file(URL_satPic + coord, "Sat\\z"+str(Zoom)+"\\"+coord+".png", referer_url,self.satBlocks[x][y])
				satlist.append(current)
				current.start()
				current.join(100)
		maploaded = 1
			
		
class draw_map(Thread):
	def __init__ (self, window, mapBlocks):
		Thread.__init__(self)
		self.mapBlocks = mapBlocks
		self.window = window
	def run(self):
		global maploaded
		maploaded = 0
		if self.window.hybrid == 1:
			googleearth_coordinates = Googleearth_Coordinates()
			Lon = self.window.lon
			Lat = self.window.lat
			Zoom = self.window.zoom
			coord=googleearth_coordinates.getTileRef(Lon, Lat, Zoom)
			coord_dist =[]
			coord_dist = googleearth_coordinates.getLatLong(coord)
			maplist = []
			map_center_x = int(self.window.map_size_x / 2)
			map_center_y = int(self.window.map_size_y / 2)
			for x in range(self.window.map_size_x):
				for y in range(self.window.map_size_y):
					Lon = (self.window.lon - coord_dist[2]*map_center_x)+coord_dist[2]*x
					Lat = (self.window.lat + coord_dist[3]*map_center_y)-coord_dist[3]*y					
					coord=googleearth_coordinates.getTileRef(Lon, Lat, Zoom)
					Map_Tile = googleearth_coordinates.getTileCoord(Lon, Lat, Zoom-1)
					current = get_file(URL_mapHybrid + str(Map_Tile[0]) + "&y=" + str(Map_Tile[1]) + "&z=" + str(18-Zoom), "Hyb\\z"+str(Zoom)+"\\"+str(Map_Tile[0]) + str(Map_Tile[1])+".png", referer_url,self.mapBlocks[x][y])
					maplist.append(current)
					current.start()
					current.join(100)
		elif self.window.hybrid == 2:
			googleearth_coordinates = Googleearth_Coordinates()
			Lon = self.window.lon
			Lat = self.window.lat
			Zoom = self.window.zoom
			coord=googleearth_coordinates.getTileRef(Lon, Lat, Zoom)
			coord_dist =[]
			coord_dist = googleearth_coordinates.getLatLong(coord)
			maplist = []
			map_center_x = int(self.window.map_size_x / 2)
			map_center_y = int(self.window.map_size_y / 2)
			for x in range(self.window.map_size_x):
				for y in range(self.window.map_size_y):
					Lon = (self.window.lon - coord_dist[2]*map_center_x)+coord_dist[2]*x
					Lat = (self.window.lat + coord_dist[3]*map_center_y)-coord_dist[3]*y					
					coord=googleearth_coordinates.getTileRef(Lon, Lat, Zoom)
					Map_Tile = googleearth_coordinates.getTileCoord(Lon, Lat, Zoom-1)
					current = get_file(URL_mapStreet + str(Map_Tile[0]) + "&y=" + str(Map_Tile[1]) + "&z=" + str(18-Zoom), "Map\\z"+str(Zoom)+"\\m"+str(Map_Tile[0]) + str(Map_Tile[1])+".png", referer_url,self.mapBlocks[x][y])
					maplist.append(current)
					current.start()
					current.join(100)
		elif self.window.hybrid == 3:
			googleearth_coordinates = Googleearth_Coordinates()
			Lon = self.window.lon
			Lat = self.window.lat
			Zoom = self.window.zoom
			if Zoom < 3:
				Zoom = 3
			coord=googleearth_coordinates.getTileRef(Lon, Lat, Zoom)
			coord_dist =[]
			coord_dist = googleearth_coordinates.getLatLong(coord)
			maplist = []
			map_center_x = int(self.window.map_size_x / 2)
			map_center_y = int(self.window.map_size_y / 2)
			for x in range(self.window.map_size_x):
				for y in range(self.window.map_size_y):
					Lon = (self.window.lon - coord_dist[2]*map_center_x)+coord_dist[2]*x
					Lat = (self.window.lat + coord_dist[3]*map_center_y)-coord_dist[3]*y					
					coord=googleearth_coordinates.getTileRef(Lon, Lat, Zoom)
					Map_Tile = googleearth_coordinates.getTileCoord(Lon, Lat, Zoom-1)
					current = get_file(URL_mapArea + str(Map_Tile[0]) + "&y=" + str(Map_Tile[1]) + "&z=" + str(18-Zoom), "Area\\z"+str(Zoom)+"\\a"+str(Map_Tile[0]) + str(Map_Tile[1])+".png", referer_url,self.mapBlocks[x][y])
					maplist.append(current)
					current.start()
					current.join(100)
		else:
			try:
				map_center_x = int(self.map_size_x / 2)
				map_center_y = int(self.map_size_y / 2)
				for x in range(self.map_size_x):
					for y in range(self.map_size_y):
						self.mapBlocks[x][y].setVisible(false)
			except: pass
		maploaded = 1


						
						
class file_remove(Thread):
	def __init__(self,MainWindow):
		Thread.__init__(self)
		self.mainWindow = MainWindow
	
	def run(self):
		for folder in glob.glob(TEMPFOLDER + "\\*\\*"):        
			# select the type of file, for instance *.jpg or all files *.*    
			if (run_backgroundthread > 0):
				i = 0
				while(run_backgroundthread > 0 and i < 10):
					time.sleep(1)
					i += 1
				date_file_list = []
				if len(glob.glob(folder + '/*.*'))>50:
					for file in glob.glob(folder + '/*.*'):               
						stats = os.stat(file)    
						lastmod_date = time.localtime(stats[8])        
						date_file_tuple = lastmod_date, file        
						date_file_list.append(date_file_tuple) 
					date_file_list.sort()
					for file in date_file_list[0:len(glob.glob(folder + '/*.*'))-50]:      
						try:                                
							os.remove(file[1])  # commented out for testing            
						except OSError:                
							print 'Could not remove', file_name
		i = 0
		while(run_backgroundthread > 0 and i < 120):
			time.sleep(1)
			i += 1
		"""	
		#-print '-'*50
		for folder in glob.glob(TEMPFOLDER):   
			print len(folder)
			for image in glob.glob(folder + '/*.png'):              
				stats = os.stat(image)                   
				lastmodDate = time.localtime(stats[8])        
				expDate = time.strptime(self.date, '%Y-%m-%d')               
				if expDate > lastmodDate:            
					try:                                
						os.remove(image)  # commented out for testing            
					except OSError:                
						print 'Could not remove', image
		"""
class background_thread(Thread):
	def __init__(self,window):
		Thread.__init__(self)
		self.window = window
		self.temp = 0
	
	def run(self):
		while(run_backgroundthread > 0):
			try:
				time.sleep(1)
				if self.window.getCurrentListPosition() != -1:
					self.window.pulse_markers(int(self.window.getCurrentListPosition()))
			except:
				pass
				#LOG( LOG_ERROR, self.__class__.__name__, "[%s]", sys.exc_info()[ 1 ] )	






######################################################################################
def updateScript(silent=False, notifyNotFound=False):
        print "> updateScript() silent=%s" %silent

        updated = False
        up = update.Update(__language__, __scriptname__)
        version = up.getLatestVersion(silent)
        print "Current Version: %s Tag Version: %s" % (__version__,version)
        if version and version != "-1":
                if __version__ < version:
                        if xbmcgui.Dialog().yesno( __language__(0), \
                                                                "%s %s %s." % ( __language__(1006), version, __language__(1002) ), \
                                                                __language__(1003 )):
                                updated = True
                                up.makeBackup()
                                up.issueUpdate(version)
                elif notifyNotFound:
                        dialogOK(__language__(0), __language__(1000))
#       elif not silent:
#               dialogOK(__language__(0), __language__(1030))                           # no tagged ver found

        del up
        print "< updateScript() updated=%s" % updated
        return updated

if __name__ == '__main__':
	# This is the main call 
	#mydisplay = MainClass()
	mydisplay = MainClass("script-%s-main.xml" % ( __scriptname__.replace( " ", "_" ), ), os.getcwd(), "Default", 0)
	mydisplay.doModal()
	del mydisplay
import xbmc, xbmcgui, datetime, tarfile, os, glob, urllib, httplib, sys, os.path, time, datetime, urllib2
from threading import Thread

BASE_RESOURCE_PATH = os.path.join( os.getcwd().replace( ";", "" ), "resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )

__language__ = xbmc.Language( os.getcwd() ).getLocalizedString 

from threading import Thread
from googleearth_coordinates import  Googleearth_Coordinates
from xbmcearth_communication import Xbmcearth_communication
from xbmcearth_communication import get_file
from global_data import *
TEMPFOLDER = os.path.join( os.getcwd().replace( ";", "" ), "temp" )


import sys
import os
import xbmcgui
import xbmc
import urllib

_ = sys.modules[ "__main__" ].__language__
__scriptname__ = sys.modules[ "__main__" ].__scriptname__
__version__ = sys.modules[ "__main__" ].__version__
BASE_RESOURCE_PATH = os.path.join( os.getcwd().replace( ";", "" ), "resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )
__language__ = xbmc.Language( os.getcwd() ).getLocalizedString 

from xbmcearth_communication import *
from global_data import *

class GUI(xbmcgui.WindowXML):
	map_size_x = 7	#Groesse der angezeigten Karte (3 Tiles) muss ungerade sein
	map_size_y = 3  #Groesse der angezeigten Karte (3 Tiles) muss ungerade sein
	map_pos_x_windowed = 0 #will be overwritten through XML-Position
	map_pos_y_windowed = 0 #will be overwritten through XML-Position
	pic_size_windowed = 0 #will be overwritten through XML-Size-X
	map_pos_x_full = 0
	map_pos_y_full = 0
	pic_size_full = 0
	map_pos_x = 0	#will be calculated
	map_pos_y = 0	#will be calculated
	pic_size = 0	#will be calculated
	
	xbmcearth_communication = Xbmcearth_communication()
	""" Settings module: used for changing settings """
	def __init__( self, *args, **kwargs ):
		xbmcgui.WindowXMLDialog.__init__( self, *args, **kwargs )
		self.MainWindow = kwargs[ "mainWindow" ]
		self.doModal()
		
	def onInit( self ):
		self.move = -9912
		self.zoom = 100
		self.panoid = ''
		self.pano_yaw_deg = 0 #Deg of first Tile
		self.image_width = 0
		self.pic_width = 0
		self.image_height = 0
		self.pic_height = 0
		self.last_tile = 0#Last Tile in left right nav
		self.xml_data = dict()
		self.tile_px = 0 #px Begin of tiles
		self.first_pic = 0 #Index of first tile
		Lon = self.MainWindow.lon
		Lat = self.MainWindow.lat
		self.get_PanoID_LatLon(Lat, Lon)
		#http://maps.google.com/cbk?output=xml&ll=37.765,-122.4
		self.pic_size_windowed = self.getControl(575).getWidth()
		w = 720
		h = 576
		self.pic_size_windowed = (int)(h / (self.image_height / self.pic_height))*2
		self.map_pos_x_windowed = self.getControl(575).getPosition()[0] #+ self.pic_size_windowed
		self.map_pos_y_windowed = self.getControl(575).getPosition()[1] #+ self.pic_size_windowed
		self.map_pos_x = self.map_pos_x_windowed
		self.map_pos_y = self.map_pos_y_windowed
		self.pic_size = self.pic_size_windowed
		self.streetViewBlocks = [[] for i in range(7)]
		i = 1
		for x in range(7):
			for y in range(3):
				Pic_size = self.pic_size
				Map_pos_x = (self.map_pos_x - Pic_size) + ((Pic_size)*x)
				Map_pos_y = (self.map_pos_y - Pic_size) + (Pic_size*y)
				self.streetViewBlocks[x].append(self.getControl(574+i))
				self.streetViewBlocks[x][y].setPosition(Map_pos_x, Map_pos_y)
				self.streetViewBlocks[x][y].setHeight(Pic_size)
				self.streetViewBlocks[x][y].setWidth(Pic_size)
				i= i+1
		self.getControl(574).setAnimations([('conditional', ('effect=slide start=%s,0 end=%s,0 time=200 condition=Control.IsVisible(574)')%(self.move+10, self.move),),('conditional',('animation effect=zoom start=%s end=%s time=200 center=%s,288 condition=Control.IsVisible(574)')%(self.zoom, self.zoom, 360+(self.move*-1)),)])
				
		streetview = draw_streetview(self,self.streetViewBlocks)
		streetview.start()
		pass
		
	def onClick( self, controlId ):
		pass
		
	def onFocus( self, controlId ):
		pass
		
	def onAction( self, action ):
	
		if ( action in ACTION_CANCEL_DIALOG ):
			self._close_dialog()
		if action.getButtonCode() == KEYBOARD_LEFT or action.getButtonCode() == REMOTE_LEFT or action.getButtonCode() == pad_button_dpad_left:
			self.moveLEFT()
		if action.getButtonCode() == KEYBOARD_RIGHT or action.getButtonCode() == REMOTE_RIGHT or action.getButtonCode() == pad_button_dpad_right:
			self.moveRIGHT()
		if action.getButtonCode() == KEYBOARD_PG_DW or action.getButtonCode() == REMOTE_4 or action.getButtonCode() == pad_button_left_trigger:
			#self.zoomOUT()
			pass
		if action.getButtonCode() == KEYBOARD_PG_UP or action.getButtonCode() == REMOTE_1 or action.getButtonCode() == pad_button_right_trigger:
			#self.zoomIN()
			pass

	def moveLEFT(self):
		if self.move < 0:
			self.move = self.move + 10
			self.getControl(574).setAnimations([('conditional', ('effect=slide start=%s,0 end=%s,0 time=200 condition=Control.IsVisible(574)')%(self.move-10,self.move),),('conditional',('animation effect=zoom start=%s end=%s time=200 center=%s,288 condition=Control.IsVisible(574)')%(self.zoom, self.zoom, 360+(self.move*-1)),)])
			self.calc_pos_left()
			#self.printDebug()
			pass
	
	def moveRIGHT(self):
		self.move = self.move - 10
		self.getControl(574).setAnimations([('conditional', ('effect=slide start=%s,0 end=%s,0 time=200 condition=Control.IsVisible(574)')%(self.move+10, self.move),),('conditional',('animation effect=zoom start=%s end=%s time=200 center=%s,288 condition=Control.IsVisible(574)')%(self.zoom, self.zoom, 360+(self.move*-1)),)])
		self.calc_pos_right()
		"""
		self.printDebug()
		"""
		pass
		
	def calc_pos_right(self):
		if self.move < 0:
			move = self.move +360 # actual Pic-Position
			size = self.pic_size # Size of one Tile (resized)
			f_tiles = (self.image_width/self.pic_width) # float Tiles in Pic
			tiles = int(f_tiles)+1 #int Tiles in Pic
			full_sized_tiles = int(f_tiles) # Tiles in Fullsize
			ratio_last_Tile = f_tiles - full_sized_tiles
			calc_pics = 0 #how many pics
			calc_pics_px = 0 #how many pixels
			calc_pics_round = 0 #full Tile or half
			calc_round = 0 #which round
			while (abs(move)>calc_pics_px):
				calc_pics = calc_pics + 1
				if calc_pics_round == tiles:
					calc_pics_round = 0
					calc_round = calc_round +1
				if calc_pics_round < full_sized_tiles:
					calc_pics_round = calc_pics_round + 1
					calc_pics_px = calc_pics_px + size
				else:
					calc_pics_round =  calc_pics_round + 1
					calc_pics_px = calc_pics_px + (size * ratio_last_Tile)
			self.tile_px = calc_pics_px
			x=0
			y = calc_pics_round
			if y>=tiles:
				y = 0
			self.first_pic = y
			for x in range(tiles):
				self.streetViewBlocks[y][0].setPosition(int(calc_pics_px),(self.map_pos_y - self.pic_size) + (self.pic_size*0))
				self.streetViewBlocks[y][1].setPosition(int(calc_pics_px),(self.map_pos_y - self.pic_size) + (self.pic_size*1))
				self.streetViewBlocks[y][2].setPosition(int(calc_pics_px),(self.map_pos_y - self.pic_size) + (self.pic_size*2))
				y = y+1
				if y>=tiles:
					y = 0
					calc_pics_px = calc_pics_px + (size * ratio_last_Tile)
				else:
					calc_pics_px = calc_pics_px + size
			self.calc_Labels()
	
	def calc_pos_left(self):
		if self.move < 0:
			move = self.move+360  # actual Pic-Position
			size = self.pic_size # Size of one Tile (resized)
			f_tiles = (self.image_width/self.pic_width) # float Tiles in Pic
			tiles = int(f_tiles)+1 #int Tiles in Pic
			full_sized_tiles = int(f_tiles) # Tiles in Fullsize
			ratio_last_Tile = f_tiles - full_sized_tiles
			calc_pics = 0 #how many pics
			calc_pics_px = 0 #how many pixels
			calc_pics_round = 0 #full Tile or half
			calc_round = 0 #which round
			while (abs(move)>calc_pics_px):
				calc_pics = calc_pics + 1
				if calc_pics_round == tiles:
					calc_pics_round = 0
					calc_round = calc_round +1
				if calc_pics_round < full_sized_tiles:
					calc_pics_round = calc_pics_round + 1
					calc_pics_px = calc_pics_px + size
				else:
					calc_pics_round =  calc_pics_round + 1
					calc_pics_px = calc_pics_px + (size * ratio_last_Tile)
			self.tile_px = calc_pics_px
			x=0
			y = calc_pics_round
			if y>=tiles:
				y = 0
			self.first_pic = y
			for x in range(tiles):
				self.streetViewBlocks[y][0].setPosition(int(calc_pics_px),(self.map_pos_y - self.pic_size) + (self.pic_size*0))
				self.streetViewBlocks[y][1].setPosition(int(calc_pics_px),(self.map_pos_y - self.pic_size) + (self.pic_size*1))
				self.streetViewBlocks[y][2].setPosition(int(calc_pics_px),(self.map_pos_y - self.pic_size) + (self.pic_size*2))	
				y = y+1
				if y>=tiles:
					y = 0
					calc_pics_px = calc_pics_px + (size * ratio_last_Tile)
				else:
					calc_pics_px = calc_pics_px + size
			self.calc_Labels()
	
	def calc_Labels(self):
		pano_yaw_deg = self.pano_yaw_deg #Deg of Tile 0
		size = self.pic_size # Size of one Tile (resized)
		f_tiles = (self.image_width/self.pic_width) # float Tiles in Pic
		tiles = int(f_tiles)+1 #int Tiles in Pic
		full_sized_tiles = int(f_tiles) # Tiles in Fullsize
		ratio_last_Tile = f_tiles - full_sized_tiles
		deg_per_px = 360 / (f_tiles*size)
		px_per_deg = (f_tiles*self.pic_size) / 360
		first_pic = self.first_pic
		x = 1
		
		start_deg =  float(pano_yaw_deg)-(self.first_pic * size * deg_per_px)
		for placemark in self.xml_data["Placemarks"]:
			#print placemark["yaw_deg"]
			deg = float(placemark["yaw_deg"])
			deg_temp = (float(start_deg)-deg)
			if deg_temp<0:
				deg_temp= deg_temp+360.0
			posx = deg_temp*px_per_deg + self.tile_px 
			#print str((float(pano_yaw_deg)-deg)) + ' -- ' + str(px_per_deg) + ' -- ' + str(posx) + '-- ' + str(self.tile_px)
			self.getControl(600+x).setPosition(int(posx),20)
			self.getControl(600+x).setLabel(str(placemark["link_text"]))
			x = x+1
		pass
	
	def zoomIN(self):
		self.zoom = self.zoom + 10
		self.getControl(574).setAnimations([('conditional', ('effect=slide start=%s,0 end=%s,0 time=200 condition=Control.IsVisible(574)')%(self.move,self.move),),('conditional',('animation effect=zoom start=%s end=%s time=200 center=%s,288 condition=Control.IsVisible(574)')%(self.zoom-10, self.zoom, 360+(self.move*-1)),)])
		pass
		
	def zoomOUT(self):
		if self.zoom > 10:
			self.zoom = self.zoom - 10
		self.getControl(574).setAnimations([('conditional', ('effect=slide start=%s,0 end=%s,0 time=200 condition=Control.IsVisible(574)')%(self.move,self.move),),('conditional',('animation effect=zoom start=%s end=%s time=200 center=%s,288 condition=Control.IsVisible(574)')%(self.zoom+10, self.zoom, 360+(self.move*-1)),)])
		pass
		
	def printDebug(self):
		zoom = (float)(((self.zoom-100.0)/100.0)/1.5)+1.0
		self.getControl(2003).setLabel(
			str(self.move) + '\n'+ str(float(self.pano_yaw_deg)+
			(360/((self.image_width/self.pic_width)*self.pic_size*zoom))*(self.move)) + '\n' + 
			str(float(self.pano_yaw_deg)+((360/(self.image_width))*360)+(360/((self.image_width/self.pic_width)*self.pic_size*zoom))*(self.move))+ '\n' + 
			str(float(self.pano_yaw_deg)+((360/(self.image_width))*720)+(360/((self.image_width/self.pic_width)*self.pic_size*zoom))*(self.move))+ '\n' +
			str((self.image_width/self.pic_width)) + '\n number' +
			str(int(self.last_tile / (self.image_width/self.pic_width)+1)) + '\n Div' +
			str(self.tile-((int(self.tile / (int(self.image_width/self.pic_width)+1)))*(int(self.image_width/self.pic_width)+1))) + '\n Last Tile' +
			str(self.last_tile) + '\n NewPos' +
			str(self.move-((self.image_width/self.pic_width)*self.pic_size))+ '\n' +
			str((((360/self.image_width)*720) / ((360.0/((self.image_width/self.pic_width)*self.pic_size))*self.pic_size))/(self.pic_size/self.pic_width) )
			)
			
	def get_PanoID_LatLon(self,Lat,Lon):	
		index = 0
		resultcontainer = dict()
		placemark_seq = []
		resultcontainer["Placemarks"] = placemark_seq
		
		self.xbmcearth_communication.connect("maps.google.com")
		result = self.xbmcearth_communication.get_GoogleStreetView(referer_url,"?output=xml&ll="+str(Lat)+","+str(Lon))
		xmldoc = minidom.parseString(result)
		nodelist = xmldoc.getElementsByTagName("data_properties")
		for node in nodelist:
			self.panoid = node.getAttribute("pano_id").encode('latin-1', 'ignore')
			self.image_width = float(node.getAttribute("image_width").encode('latin-1', 'ignore'))
			self.pic_width = float(node.getAttribute("tile_width").encode('latin-1', 'ignore'))
			self.image_height = float(node.getAttribute("image_height").encode('latin-1', 'ignore'))
			self.pic_height = float(node.getAttribute("tile_height").encode('latin-1', 'ignore'))
		nodelist = xmldoc.getElementsByTagName("projection_properties")
		for node in nodelist:
			self.pano_yaw_deg = node.getAttribute("pano_yaw_deg")
		nodelist = xmldoc.getElementsByTagName("link")
		for node in nodelist:
			placemark = dict()
			resultcontainer["Placemarks"].append(placemark)
			resultcontainer["Placemarks"][index]["yaw_deg"] = node.getAttribute("yaw_deg")
			resultcontainer["Placemarks"][index]["pano_id"] = node.getAttribute("pano_id")
			index = index + 1
		index = 0
		nodelist = xmldoc.getElementsByTagName("link_text")
		for node in nodelist:
			print node.toxml()
			#if node.nodeType == node.TEXT_NODE:
			resultcontainer["Placemarks"][index]["link_text"] = node.firstChild.data.encode('latin-1', 'ignore')
			print node.firstChild.data.encode('latin-1', 'ignore')
				index = index + 1
		self.xml_data = resultcontainer
	
	
	def _close_dialog( self ):	
		self.close()

class draw_streetview(Thread):
	xbmcearth_communication = Xbmcearth_communication()
	def __init__ (self, window, image):
		Thread.__init__(self)
		self.window = window
		self.image = image

	def run(self):
		streetview_list=[]
		i = 1
		for x in range(7):
			for y in range(3):
				self.image[x][y].setVisible(False)
		for x in range((int)(self.window.image_width/self.window.pic_width)+1):
			for y in range(3):
				self.image[x][y].setVisible(True)
				current = get_file(("http://cbk0.google.com/cbk?output=tile&panoid=%s&zoom=3&x=%s&y=%s")%(self.window.panoid,x,y),("Street/z3/%s_%s%s.jpg")%(self.window.panoid,x,y), referer_url,self.image[x][y])
				streetview_list.append(current)
				thread_starter=0
				while thread_starter<10:
					try:
						current.start()
						thread_starter=100
					except:
						time.sleep(1)
						thread_starter +=1
#!/usr/bin/env python3

import sys
import os


from . import sitemanager
from . import MainWindow
from . import SiteBox
from . import EditBox
from . import settings
from . import Screenshot

class Core:
	
	singleton=None
	DEBUG=False
	
	@classmethod
	def get_core(self):
		
		if Core.singleton==None:
			Core.singleton=Core()
			Core.singleton.init()

		return Core.singleton
		
	
	def __init__(self,args=None):

	
		self.dprint("Init...")
		
	#def __init__
	
	def init(self):

		self.rsrc_dir= settings.RSRC_DIR + "/"
		self.ui_path= settings.RSRC_DIR + "/easy-sites.ui"
		
		'''
		try:
			cache_dir=os.environ["XDG_CACHE_HOME"]

		except:
			cache_dir=os.path.expanduser("~/.cache/")

		self.image_dir=cache_dir+"easy-sites"

		if not os.path.exists(self.image_dir):
			os.mkdir(self.image_dir)
		'''
		
		self.screenshot=Screenshot.ScreenshotNeo()	
		self.sitesmanager=sitemanager.SiteManager()
		self.siteBox=SiteBox.SiteBox()
		self.editBox=EditBox.EditBox()
		self.mainWindow=MainWindow.MainWindow()

		self.image_dir=self.screenshot.image_dir
		self.custom_image="/usr/share/lliurex-easy-sites/custom.png"
		self.nodisp_image="/usr/share/lliurex-easy-sites/nodisp.png"

		# Main window must be the last one
		if len(sys.argv)>1:
			sync_folder=sys.argv[1]
		else:
			sync_folder=None		
		self.mainWindow=MainWindow.MainWindow(sync_folder)

		self.mainWindow.load_gui()
		self.mainWindow.start_gui()
			
		
		
	#def init
	
	
	
	def dprint(self,msg):
		
		if Core.DEBUG:
			
			print("[CORE] %s"%msg)
	
	#def  dprint

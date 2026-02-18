#!/usr/bin/env python3

import sys
import os


from . import SiteManager
from . import SiteStack
from . import SitesOptionsStack
from . import MainStack

class Core:
	
	singleton=None
	DEBUG=False
	
	@classmethod
	def get_core(self):
		
		if Core.singleton==None:
			Core.singleton=Core()
			Core.singleton.init()

		return Core.singleton
		
	#def get_core
	
	def __init__(self,args=None):

	
		self.dprint("Init...")
		
	#def __init__
	
	def init(self):

		self.siteManager=SiteManager.SiteManager()
		self.siteStack=SiteStack.Bridge()
		self.sitesOptionsStack=SitesOptionsStack.Bridge()
		self.mainStack=MainStack.Bridge()
		
		self.mainStack.initBridge()
		
	#def init

	
	def dprint(self,msg):
		
		if Core.DEBUG:
			
			print("[CORE] %s"%msg)
	
	#def  dprint

#class Core

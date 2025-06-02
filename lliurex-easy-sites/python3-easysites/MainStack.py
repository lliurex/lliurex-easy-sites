from PySide2.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os 
import sys
import threading
import time
import copy

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

CREATE_SITE_FROM_MENU_ERROR=-38

class GatherInfo(QThread):

	def __init__(self,*args):
		
		QThread.__init__(self)

	#def _init__

	def run(self,*args):
		
		time.sleep(1)
		self.readConf=Bridge.siteManager.readConf()

	#def run

#class GatherInfo

class Bridge(QObject):

	def __init__(self):

		QObject.__init__(self)
		self.core=Core.Core.get_core()
		Bridge.siteManager=self.core.siteManager
		self._currentStack=0
		self._mainCurrentOption=0
		self._closePopUp=[True,""]
		self.moveToStack=""
		self._closeGui=True
		self._showLoadErrorMessage=[False,""]
		Bridge.siteManager.createN4dClient(sys.argv[2],sys.argv[3])

	#def _init__

	def initBridge(self):

		self.currentStack=0
		self.closeGui=False
		self.gatherInfo=GatherInfo()
		self.gatherInfo.start()
		self.gatherInfo.finished.connect(self._loadConfig)
	
	#def initBridge
	
	def _loadConfig(self):

		self.closeGui=True
		
		if self.gatherInfo.readConf['status']:
			self.core.sitesOptionsStack.loadConfig()
			self._systemLocale=Bridge.siteManager.systemLocale
			if len(sys.argv)<5:
				if Bridge.siteManager.loadError:
					self.core.sitesOptionsStack.showMainMessage=[True,Bridge.siteManager.SITES_WITH_ERRORS,"Error"]
				self.currentStack=1
			else:
				tmpFile=sys.argv[1]
				if os.path.exists(tmpFile):
					self.core.siteStack.addNewSite(tmpFile)
				else:
					self.showLoadErrorMessage=[True,CREATE_SITE_FROM_MENU_ERROR]
		else:
			self.showLoadErrorMessage=[True,self.gatherInfo.readConf['code']]
	
	#def _loadConfig

	def _getSystemLocale(self):

		return self._systemLocale

	#def _getSystemLocale

	def _getCurrentStack(self):

		return self._currentStack

	#def _getCurrentStack	

	def _setCurrentStack(self,currentStack):
		
		if self._currentStack!=currentStack:
			self._currentStack=currentStack
			self.on_currentStack.emit()

	#def _setCurentStack

	def _getMainCurrentOption(self):

		return self._mainCurrentOption

	#def _getMainCurrentOption	

	def _setMainCurrentOption(self,mainCurrentOption):
		
		if self._mainCurrentOption!=mainCurrentOption:
			self._mainCurrentOption=mainCurrentOption
			self.on_mainCurrentOption.emit()

	#def _setMainCurrentOption

	def _getClosePopUp(self):

		return self._closePopUp

	#def _getClosePopUp

	def _setClosePopUp(self,closePopUp):

		if self._closePopUp!=closePopUp:
			self._closePopUp=closePopUp
			self.on_closePopUp.emit()

	#def _setClosePopUp

	def _getShowLoadErrorMessage(self):

		return self._showLoadErrorMessage

	#def _getShowLoadErrorMessage

	def _setShowLoadErrorMessage(self,showLoadErrorMessage):

		if self._showLoadErrorMessage!=showLoadErrorMessage:
			self._showLoadErrorMessage=showLoadErrorMessage
			self.on_showLoadErrorMessage.emit()

	#def _setShowLoadErrorMessage

	def _getCloseGui(self):

		return self._closeGui

	#def _getCloseGui	

	def _setCloseGui(self,closeGui):
		
		if self._closeGui!=closeGui:
			self._closeGui=closeGui
			self.on_closeGui.emit()

	#def _setCloseGui

	@Slot(int)
	def moveToMainOptions(self,stack):

		if self.mainCurrentOption!=stack:
			if stack==0:
				self.mainCurrentOption=stack
			else:
				self.core.sitesOptionsStack.showMainMessage=[False,"","Ok"]

	#def moveToMainOptions	

	def manageGoToStack(self):

		if self.moveToStack!="":
			self.currentStack=self.moveToStack
			self.mainCurrentOption=0
			self.moveToStack=""

	#def _manageGoToStack

	@Slot()
	def openHelp(self):
		
		if 'valencia' in self._systemLocale:
			self.helpCmd='xdg-open https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Easy-Sites.'
		else:
			self.helpCmd='xdg-open https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Easy-Sites'
		
		self.openHelpT=threading.Thread(target=self._openHelp)
		self.openHelpT.daemon=True
		self.openHelpT.start()

	#def openHelp

	def _openHelp(self):

		os.system(self.helpCmd)

	#def _openHelp

	@Slot()
	def closeEasySites(self):

		if self.core.siteStack.changesInSite:
			self.closeGui=False
			self.core.siteStack.showChangesInSiteDialog=True

	#def closeBellScheduler
	
	on_currentStack=Signal()
	currentStack=Property(int,_getCurrentStack,_setCurrentStack, notify=on_currentStack)

	on_mainCurrentOption=Signal()
	mainCurrentOption=Property(int,_getMainCurrentOption,_setMainCurrentOption, notify=on_mainCurrentOption)

	on_showLoadErrorMessage=Signal()
	showLoadErrorMessage=Property('QVariantList',_getShowLoadErrorMessage,_setShowLoadErrorMessage, notify=on_showLoadErrorMessage)

	on_closePopUp=Signal()
	closePopUp=Property('QVariantList',_getClosePopUp,_setClosePopUp, notify=on_closePopUp)

	on_closeGui=Signal()
	closeGui=Property(bool,_getCloseGui,_setCloseGui, notify=on_closeGui)

	systemLocale=Property(str,_getSystemLocale,constant=True)

#class Bridge

from . import Core



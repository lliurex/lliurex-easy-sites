from PySide2.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os 
import sys
import threading
import time
import copy

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

NEW_SITE_CONFIG=1
LOAD_SITE_CONFIG=2
CHECK_DATA=3
SAVE_DATA=4
HIDE_SITE=5
SHOW_SITE=6
SYNC_CONTENT=7
DELETE_SITE=8

class LoadSite(QThread):

	def __init__(self,*args):

		QThread.__init__(self)
		self.newSite=args[0]
		self.siteInfo=args[1]

	#def __init__

	def run(self,*args):

		time.sleep(0.5)
		ret=Bridge.siteManager.initValues()
		if not self.newSite:
			ret=Bridge.siteManager.loadSiteConfig(self.siteInfo)

	#def run

#class LoadSite

class CheckData(QThread):

	def __init__(self,*args):

		QThread.__init__(self)
		self.dataToCheck=args[0]
		self.edit=args[1]
		self.siteToLoad=args[2]
		self.retData={}

	#def __init__

	def run(self,*args):

		time.sleep(0.5)
		self.retData=Bridge.siteManager.checkData(self.dataToCheck,self.edit,self.siteToLoad)
		'''
		if self.retData:
			self.retDuplicate=Bridge.siteManager.checkDuplicateSite(self.dataToCheck)
		'''		
	#def run

#class CheckData

class SaveData(QThread):

	def __init__(self,*args):

		QThread.__init__(self)
		self.action=args[0]
		self.dataToSave=args[1]
		self.completeData=args[2]
		self.ret=[]

	#def __init__

	def run(self,*args):

		time.sleep(0.5)
		self.ret=Bridge.siteManager.saveData(self.action,self.dataToSave,self.completeData)

	#def run

#class SaveData

class Bridge(QObject):

	def __init__(self):

		QObject.__init__(self)
		self.core=Core.Core.get_core()
		Bridge.siteManager=self.core.siteManager
		self._siteName=Bridge.siteManager.siteName
		self._siteImage=Bridge.siteManager.siteImage
		self._siteDescription=Bridge.siteManager.siteDescription
		self._isSiteVisible=Bridge.siteManager.isSiteVisible
		self._siteFolder=Bridge.siteManager.siteFolder
		self._mountUnit=Bridge.siteManager.mountUnit
		self._canMount=Bridge.siteManager.canMount
		self._siteCurrentOption=0
		self._showSiteFormMessage=[False,"","Ok"]
		self._showChangesInSiteDialog=False
		self._changesInSite=False
		self._actionType="add"
		self.onlySync=True
		self.requiredMoveToStack=True

	#def _init__

	def _getSiteName(self):

		return self._siteName

	#def _getSiteName

	def _setSiteName(self,siteName):

		if self._siteName!=siteName:
			self._siteName=siteName
			self.on_siteName.emit()

	#def _setSiteName 

	def _getSiteImage(self):

		return self._siteImage

	#def _getSiteImage

	def _setSiteImage(self,siteImage):

		if self._siteImage!=siteImage:
			self._siteImage=siteImage
			self.on_siteImage.emit()

	#def _setSiteImage

	def _getSiteDescription(self):

		return self._siteDescription

	#def _getSiteDescription

	def _setSiteDescription(self,siteDescription):

		if self._siteDescription!=siteDescription:
			self._siteDescription=siteDescription
			self.on_siteDescription.emit()

	#def _setSiteDescription

	def _getIsSiteVisible(self):

		return self._isSiteVisible

	#def _getIsSiteVisible

	def _setIsSiteVisible(self,isSiteVisible):

		if self._isSiteVisible!=isSiteVisible:
			self._isSiteVisible=isSiteVisible
			self.on_isSiteVisible.emit()

	#def _setIsSiteVisible

	def _getSiteFolder(self):

		return self._siteFolder

	#def _getSiteFolder

	def _setSiteFolder(self,siteFolder):

		if self._siteFolder!=siteFolder:
			self._siteFolder=siteFolder
			self.on_siteFolder.emit()

	#def _setBellDuration

	def _getMountUnit(self):

		return self._mountUnit

	#def _getMountUnit

	def _setMountUnit(self,mountUnit):

		if self._mountUnit!=mountUnit:
			self._mountUnit=mountUnit
			self.on_mountUnit.emit()

	#def _setMountUnit

	def _getCanMount(self):

		return self._canMount

	#def _getCanMount

	def _setCanMount(self,canMount):

		if self._canMount!=canMount:
			self._canMount=canMount
			self.on_canMount.emit()

	#def _setCanMount

	def _getSiteCurrentOption(self):

		return self._siteCurrentOption

	#def _getBellCurrentOption	

	def _setSiteCurrentOption(self,siteCurrentOption):
		
		if self._siteCurrentOption!=siteCurrentOption:
			self._siteCurrentOption=siteCurrentOption
			self.on_siteCurrentOption.emit()

	#def _setSiteCurrentOption

	def _getShowChangesInSiteDialog(self):

		return self._showChangesInSiteDialog

	#def _getShowchangesInSiteDialog

	def _setShowChangesInSiteDialog(self,showChangesInSiteDialog):

		if self._showChangesInSiteDialog!=showChangesInSiteDialog:
			self._showChangesInSiteDialog=showChangesInSiteDialog
			self.on_showChangesInSiteDialog.emit()

	#def _setShowChangesInSiteDialog

	def _getChangesInSite(self):

		return self._changesInSite

	#def _getChangesInSite

	def _setChangesInSite(self,changesInSite):

		if self._changesInSite!=changesInSite:
			self._changesInSite=changesInSite
			self.on_changesInSite.emit()

	#def _setChangesInSite

	def _getShowSiteFormMessage(self):

		return self._showSiteFormMessage

	#def _getShowSiteFormMessage

	def _setShowSiteFormMessage(self,showSiteFormMessage):

		if self._showSiteFormMessage!=showSiteFormMessage:
			self._showSiteFormMessage=showSiteFormMessage
			self.on_showSiteFormMessage.emit()

	#def _setShowSiteFormMessage

	def _getActionType(self):

		return self._actionType

	#def _getActionType

	def _setActionType(self,actionType):

		if self._actionType!=actionType:
			self._actionType=actionType
			self.on_actionType.emit()

	#def _setActionType

	@Slot()
	def addNewSite(self,folderPath=None):

		self.folderFromMenu=folderPath
		self.edit=False
		self.actionType="add"
		self.siteToLoad=""
		self.onlySync=False
		self.requiredSync=False

		if self.folderFromMenu==None:
			self.core.mainStack.closePopUp=[False,NEW_SITE_CONFIG]
			self.core.sitesOptionsStack.showMainMessage=[False,"","Ok"]
		self.newSite=LoadSite(True,"")
		self.newSite.start()
		self.newSite.finished.connect(self._addNewSiteRet)

	#def addNewSite

	def _addNewSiteRet(self):

		self.currentSiteConfig=copy.deepcopy(Bridge.siteManager.currentSiteConfig)
		self._initializeVars()
		if self.folderFromMenu==None:
			self.core.mainStack.closePopUp=[True,""]
		else:
			self.siteFolder=self.folderFromMenu
			self.updateSiteFolderValue(self.folderFromMenu)
		self.core.mainStack.currentStack=2
		self.siteCurrentOption=1

	#def _addNewBellRet

	def _initializeVars(self):

		self.siteName=Bridge.siteManager.siteName
		self.siteImage=Bridge.siteManager.siteImage
		self.siteDescription=Bridge.siteManager.siteDescription
		self.isSiteVisible=Bridge.siteManager.isSiteVisible
		self.siteFolder=Bridge.siteManager.siteFolder
		self.showSiteFormMessage=[False,"","Ok"]
		self.changesInSite=False
		self.mountUnit=Bridge.siteManager.mountUnit
		self.canMount=Bridge.siteManager.canMount

	#def _initializeVars

	@Slot()
	def goHome(self):

		if not self.changesInSite:
			self.core.mainStack.currentStack=1
			self.core.mainStack.mainCurrentOption=0
			self.siteCurrentOption=0
			self.core.mainStack.moveToStack=""
		else:
			self.showChangesInSiteDialog=True
			self.core.mainStack.moveToStack=1

	#def goHome

	@Slot(str)
	def loadSite(self,siteToLoad):

		self.siteToLoad=siteToLoad
		self.edit=True
		self.requiredSync=False
		self.changeInFolder=False
		self.changeInName=False
		self.changeInMountOption=False
		self.core.mainStack.closePopUp=[False,LOAD_SITE_CONFIG]
		self.core.sitesOptionsStack.showMainMessage=[False,"","Ok"]
		self.actionType="edit"
		self.editSite=LoadSite(False,siteToLoad)
		self.editSite.start()
		self.editSite.finished.connect(self._loadSiteRet)

	#def loadSite

	def _loadSiteRet(self):

		self.currentSiteConfig=copy.deepcopy(Bridge.siteManager.currentSiteConfig)
		self._initializeVars()
		self.core.mainStack.closePopUp=[True,""]
		self.core.mainStack.currentStack=2
		self.siteCurrentOption=1

	#def _loadSiteRet

	@Slot('QVariantList')
	def changeSiteStatus(self,data):

		action="visibility"
		completeData=False

		self.requiredMoveToStack=False
		if data[1]:
			msgCode=SHOW_SITE
		else:
			msgCode=HIDE_SITE

		self.saveDataChanges(action,data,completeData,msgCode)

	#def changeSiteStatus
	
	@Slot(str)
	def viewSiteInBrowser(self,siteUrl):

		self.viewSiteCmd="xdg-open %s"%siteUrl
		self.viewSiteT=threading.Thread(target=self._viewSite)
		self.viewSiteT.daemon=True
		self.viewSiteT.start()

	#def viewSiteInBrowser

	def _viewSite(self):

		os.system(self.viewSiteCmd)

	#def _viewSite

	@Slot(str)
	def openSiteFolder(self,siteFolder):

		self.openSiteCmd="xdg-open %s"%siteFolder
		self.openSiteT=threading.Thread(target=self._openSite)
		self.openSiteT.daemon=True
		self.openSiteT.start()

	#def openSiteFolderr

	def _openSite(self):

		os.system(self.openSiteCmd)

	#def _openSite

	@Slot('QVariantList')
	def syncSiteContent(self,data):

		action="sync"
		completeData=False
		self.requiredMoveToStack=False
		self.saveDataChanges(action,data,completeData,SYNC_CONTENT)

	#def syncSiteContent

	def removeSite(self,siteId):

		action="delete"
		completeData=False
		self.requiredMoveToStack=False
		self.saveDataChanges(action,siteId,completeData,DELETE_SITE)
	
	#def removeSite

	@Slot(str)
	def updateSiteNameValue(self,value):

		if value!=self.siteName:
			self.siteName=value
			self.currentSiteConfig["id"]=Bridge.siteManager.getSiteId(value)
			self.currentSiteConfig["name"]=self.siteName

		if self.currentSiteConfig!=Bridge.siteManager.currentSiteConfig:
			self.changesInSite=True
			self.onlySync=False
			if self.currentSiteConfig["mountUnit"]:
				self.changeInName=True
		else:
			self.changesInSite=False
			self.onlySync=True
			self.changeInName=False

	#def updatesiteNameValue

	@Slot(str,result=bool)
	def checkMimeTypes(self,imagePath):

		ret=Bridge.siteManager.checkMimeTypes(imagePath)
		return ret["result"]

	#def checkMimeTypes

	@Slot('QVariantList')
	def updateImageValues(self,values):

		tmpImage=[]
		tmpImage.append(values[0])
		if values[0]=="stock":
			values[1]=os.path.join(Bridge.siteManager.stockImagesFolder,"custom.png")
		tmpImage.append(values[1])
		tmpImage.append(False)

		if tmpImage!=self.siteImage:
			self.siteImage=tmpImage
			self.currentSiteConfig["image"]["option"]=self.siteImage[0]
			self.currentSiteConfig["image"]["img_path"]=self.siteImage[1]
	
		if self.currentSiteConfig!=Bridge.siteManager.currentSiteConfig:
			self.changesInSite=True
			self.onlySync=False
		else:
			self.changesInSite=False
			self.onlySync=True

	#def updateImageValues

	@Slot(str)
	def updateSiteDescriptionValue(self,value):

		if value!=self.siteDescription:
			self.siteDescription=value
			self.currentSiteConfig["description"]=self.siteDescription

		if self.currentSiteConfig!=Bridge.siteManager.currentSiteConfig:
			self.changesInSite=True
			self.onlySync=False
		else:
			self.changesInSite=False
			self.onlySync=True

	#def updateSiteDescriptionValue

	@Slot(str)
	def updateSiteFolderValue(self,value):

		if self.currentSiteConfig["sync_folder"]!=value:
			self.currentSiteConfig["sync_folder"]=value

		if os.path.exists(value):
			self.canMount=True
		else:
			self.canMount=False
			
		self.changeInFolder=True
		self.changesInSite=True
	
	#def updateSiteFolderValue

	@Slot(bool)
	def updateIsSiteVisibleValue(self,value):

		if value!=self.isSiteVisible:
			self.isSiteVisible=value
			self.currentSiteConfig["visibility"]=self.isSiteVisible

		if self.currentSiteConfig!=Bridge.siteManager.currentSiteConfig:
			self.changesInSite=True
			self.onlySync=False
		else:
			self.changesInSite=False
			self.onlySync=True

	#def updateIsSiteVisibleValue

	@Slot(bool)
	def updateMountValue(self,value):

		if value!=self.mountUnit:
			self.mountUnit=value
			self.currentSiteConfig["mountUnit"]=self.mountUnit

		if self.currentSiteConfig!=Bridge.siteManager.currentSiteConfig:
			self.changesInSite=True
			self.onlySync=False
			self.changeInMountOption=True
		else:
			self.changeInMountOption=False
			self.changesInSite=False
			self.onlySync=True

	#def updateMountValue

	@Slot(str)
	def manageChangesDialog(self,action):

		self.showChangesInSiteDialog=False

		if action=="Accept":
			self._applySiteChanges()
		elif action=="Discard":
			self._cancelSiteChanges()
		elif action=="Cancel":
			pass

	#def manageChangesDialog

	@Slot()
	def applySiteChanges(self):

		self._applySiteChanges()

	#def applyBellChanges

	def _applySiteChanges(self):

		self.core.mainStack.closePopUp=[False,CHECK_DATA]
		self.core.mainStack.closeGui=False
		self.checkData=CheckData(self.currentSiteConfig,self.edit,self.siteToLoad)
		self.checkData.start()
		self.checkData.finished.connect(self._checkDataRet)

	#def _applySiteChanges

	def _checkDataRet(self):

		completeData=False
		
		if self.checkData.retData["result"]:
			if self.onlySync:
				action="sync"
				data=[self.siteToLoad,self.currentSiteConfig["sync_folder"]]
			else:
				completeData=True
				action=self.actionType
				if self.changeInFolder or self.changeInName or self.changeInMountOption:
					self.requiredSync=True
				data=[self.currentSiteConfig,self.requiredSync]

			self.saveDataChanges(action,data,completeData,SAVE_DATA)
		else:
			self.core.mainStack.closePopUp=[True,""]
			self.showSiteFormMessage=[True,self.checkData.retData["code"],"Error"]

	#def _checkDataRet

	def saveDataChanges(self,action,data,completeData,msgCode):

		self.core.mainStack.closePopUp=[False,msgCode]
		
		self.saveData=SaveData(action,data,completeData)
		self.saveData.start()
		self.saveData.finished.connect(self._saveDataRet)

	#def saveData

	def _saveDataRet(self):

		if self.saveData.ret["status"]:
			self.core.sitesOptionsStack._updateSitesModel()
			self.core.sitesOptionsStack.showMainMessage=[True,self.saveData.ret["code"],"Ok"]
		else:
			self.core.sitesOptionsStack.showMainMessage=[True,self.saveData.ret["code"],"Error"]	

		self.core.sitesOptionsStack.enableGlobalOptions=Bridge.siteManager.checkGlobalOptionStatus()
		self.core.sitesOptionsStack.enableChangeStatusOptions=Bridge.siteManager.checkChangeStatusSitesOption()
		self.core.sitesOptionsStack.filterStatusValue="all"
		self.changesInSite=False
		self.core.mainStack.closeGui=True

		if self.requiredMoveToStack:
			self.core.mainStack.moveToStack=1
			self.core.mainStack.manageGoToStack()
		
		self.core.mainStack.closePopUp=[True,""]
		self.requiredMoveToStack=True

	#def _saveDataRet

	@Slot()
	def cancelSiteChanges(self):

		self._cancelSiteChanges()

	#def cancelSiteChanges

	def _cancelSiteChanges(self):

		self.changesInSite=False
		self.core.mainStack.closeGui=True
		self.core.mainStack.moveToStack=1
		self.core.mainStack.manageGoToStack()

	#def _cancelSiteChanges


	on_siteName=Signal()
	siteName=Property(str,_getSiteName,_setSiteName,notify=on_siteName)

	on_siteImage=Signal()
	siteImage=Property('QVariantList',_getSiteImage,_setSiteImage,notify=on_siteImage)

	on_siteDescription=Signal()
	siteDescription=Property(str,_getSiteDescription,_setSiteDescription,notify=on_siteDescription)

	on_siteFolder=Signal()
	siteFolder=Property(str,_getSiteFolder,_setSiteFolder,notify=on_siteFolder)

	on_mountUnit=Signal()
	mountUnit=Property(bool,_getMountUnit,_setMountUnit,notify=on_mountUnit)

	on_canMount=Signal()
	canMount=Property(bool,_getCanMount,_setCanMount,notify=on_canMount)

	on_isSiteVisible=Signal()
	isSiteVisible=Property(bool,_getIsSiteVisible,_setIsSiteVisible,notify=on_isSiteVisible)

	on_showSiteFormMessage=Signal()
	showSiteFormMessage=Property('QVariantList',_getShowSiteFormMessage,_setShowSiteFormMessage, notify=on_showSiteFormMessage)

	on_siteCurrentOption=Signal()
	siteCurrentOption=Property(int,_getSiteCurrentOption,_setSiteCurrentOption, notify=on_siteCurrentOption)

	on_showChangesInSiteDialog=Signal()
	showChangesInSiteDialog=Property(bool,_getShowChangesInSiteDialog,_setShowChangesInSiteDialog,notify=on_showChangesInSiteDialog)

	on_changesInSite=Signal()
	changesInSite=Property(bool,_getChangesInSite,_setChangesInSite,notify=on_changesInSite)

	on_actionType=Signal()
	actionType=Property(str,_getActionType,_setActionType,notify=on_actionType)

#class Bridge

from . import Core



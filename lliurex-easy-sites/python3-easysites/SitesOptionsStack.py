from PySide2.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os 
import sys
import threading
import time
import copy

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

from . import SitesModel

ACTIVE_SITE=5
ACTIVE_ALL_SITES=6
DEACTIVE_SITE=7
DEACTIVE_ALLS_SITES=8
REMOVING_SITE=9
REMOVING_ALL_SITES=10
EXPORT_SITES_CONFIG=11
IMPORT_SITES_CONFIG=12
RECOVERY_SITES_CONFIG=13

class ChangeSiteStatus(QThread):

	def __init__(self,*args):

		QThread.__init__(self)
		self.allSites=args[0]
		self.active=args[1]
		self.siteToEdit=args[2]
		self.ret=[]

	#def __init__

	def run(self,*args):

		time.sleep(0.5)
		self.ret=Bridge.siteManager.changeSiteStatus(self.allSites,self.active,self.siteToEdit)

	#def run

#class ChangeSiteStatus

class RemoveSite(QThread):

	def __init__(self,*args):

		QThread.__init__(self)
		self.allSites=args[0]
		self.siteToRemove=args[1]
		self.ret=[]

	#def __init__

	def run(self,*args):

		time.sleep(0.5)
		self.ret=Bridge.siteManager.removeSites(self.allSites,self.siteToRemove)

	#def run

#class RemoveSite

	
class Bridge(QObject):

	def __init__(self):

		QObject.__init__(self)
		self.core=Core.Core.get_core()
		Bridge.siteManager=self.core.siteManager
		self._sitesModel=SitesModel.SitesModel()
		self._showMainMessage=[False,"","Ok"]
		self._showRemoveSiteDialog=[False,False]
		self._enableGlobalOptions=False
		self._enableChangeStatusOptions=[False,False,False]
		self._filterStatusValue="all"

	#def _init__
	
	def loadConfig(self):

		self._updateSitesModel()
		self._manageOptions()
	
	#def loadConfig

	def _manageOptions(self):

		self.enableGlobalOptions=Bridge.siteManager.checkGlobalOptionStatus()
		self.enableChangeStatusOptions=Bridge.siteManager.checkChangeStatusSitesOption()

	#def _manageOptions

	def _getshowRemoveSiteDialog(self):

		return self._showRemoveSiteDialog

	#def _getshowRemoveSiteDialog

	def _setshowRemoveSiteDialog(self,showRemoveSiteDialog):

		if self._showRemoveSiteDialog!=showRemoveSiteDialog:
			self._showRemoveSiteDialog=showRemoveSiteDialog
			self.on_showRemoveSiteDialog.emit()

	#def _setshowRemoveSiteDialog

	def _getSitesModel(self):

		return self._sitesModel

	#def _getsitesModel

	def _getShowMainMessage(self):

		return self._showMainMessage

	#def _getShowMainMessage

	def _setShowMainMessage(self,showMainMessage):

		if self._showMainMessage!=showMainMessage:
			self._showMainMessage=showMainMessage
			self.on_showMainMessage.emit()

	#def _setShowMainMessage

	def _getEnableGlobalOptions(self):

		return self._enableGlobalOptions

	#def _getEnableGlobalOptions

	def _setEnableGlobalOptions(self,enableGlobalOptions):

		if self._enableGlobalOptions!=enableGlobalOptions:
			self._enableGlobalOptions=enableGlobalOptions
			self.on_enableGlobalOptions.emit()

	#def _setEnableGlobalOptions

	def _getEnableChangeStatusOptions(self):

		return self._enableChangeStatusOptions

	#def _getEnableChangeStatusOptions

	def _setEnableChangeStatusOptions(self,enableChangeStatusOptions):

		if self._enableChangeStatusOptions!=enableChangeStatusOptions:
			self._enableChangeStatusOptions=enableChangeStatusOptions
			self.on_enableChangeStatusOptions.emit()

	#def _setEnableChangeStatusOptions

	def _getFilterStatusValue(self):

		return self._filterStatusValue

	#def _getFilterStatusValue

	def _setFilterStatusValue(self,filterStatusValue):

		if self._filterStatusValue!=filterStatusValue:
			self._filterStatusValue=filterStatusValue
			self.on_filterStatusValue.emit()

	#def _setFilterStatusValue

	def _updateSitesModel(self):

		ret=self._sitesModel.clear()
		sitesEntries=Bridge.siteManager.sitesConfigData
		for item in sitesEntries:
			if item["id"]!="":
				self._sitesModel.appendRow(item["id"],item["img"],item["name"],item["createdBy"],item["updatedBy"],item["isVisible"],item["url"],item["folder"])
	
	#def _updatesitesModel

	def _updatesitesModelInfo(self,param):

		updatedInfo=Bridge.siteManager.sitesConfigData
		if len(updatedInfo)>0:
			for i in range(len(updatedInfo)):
				index=self._sitesModel.index(i)
				self._sitesModel.setData(index,param,updatedInfo[i][param])

	#def _updatesitesModelInfo

	@Slot(str)
	def manageStatusFilter(self,value):

		self.filterStatusValue=value

	#def manageStatusFilter

	@Slot('QVariantList')
	def changeSiteStatus(self,data):

		self.core.mainStack.closeGui=False
		self.showMainMessage=[False,"","Ok"]
		self.changeAllSites=data[0]
		active=data[1]
		if self.changeAllSites:
			siteToEdit=None
			if active:
				self.core.mainStack.closePopUp=[False,ACTIVE_ALL_SITES]
			else:
				self.core.mainStack.closePopUp=[False,DEACTIVE_ALLS_SITES]
		
		else:
			siteToEdit=data[2]
			if active:
				self.core.mainStack.closePopUp=[False,ACTIVE_SITE]
			else:
				self.core.mainStack.closePopUp=[False,DEACTIVE_SITE]
		
		self.changeStatus=ChangeSitesStatus(self.changeAllSites,active,siteToEdit)
		self.changeStatus.start()
		self.changeStatus.finished.connect(self._changeSiteStatusRet)

	#def changeSITEStatus

	def _changeSiteStatusRet(self):

		if self.changeStatus.ret[0]:
			if self.changeAllSites:
				self._updatesitesModel()
			else:
				self._updatesitesModelInfo('isVisible')
			self.showMainMessage=[True,self.changeStatus.ret[1],"Ok"]
		else:
			self.showMainMessage=[True,self.changeStatus.ret[1],"Error"]

		self.enableChangeStatusOptions=Bridge.siteManager.checkChangeStatusSitesOption()
		self.filterStatusValue="all"
		self.core.mainStack.closePopUp=[True,""]
		self.core.mainStack.closeGui=True

	#def _changeSiteStatusRet

	@Slot('QVariantList')
	def removeSite(self,data):

		self.showMainMessage=[False,"","Ok"]
		self.removeAllSites=data[0]
		if self.removeAllSites:
			self.siteToRemove=None
		else:
			self.siteToRemove=data[1]

		self.showRemoveSiteDialog=[True,self.removeAllSites]

	#def removeSITE

	@Slot(str)
	def manageRemoveSiteDialog(self,response):

		self.showRemoveSiteDialog=[False,False]
		if response=="Accept":
			self._launchRemoveSiteProcess()

	#def manageRemoveSITEDialog

	def _launchRemoveSiteProcess(self):

		self.core.mainStack.closeGui=False
		if self.removeSitesSITES:
			self.core.mainStack.closePopUp=[False,REMOVING_ALL_SITES]
		else:
			self.core.mainStack.closePopUp=[False,REMOVING_SITE]

		self.removeSiteProcess=RemoveSite(self.removeAllSites,self.siteToRemove)
		self.removeSiteProcess.start()
		self.removeSiteProcess.finished.connect(self._removeSiteProcessRet)

	#def _launchRemoveSiteProcess

	def _removeSiteProcessRet(self):

		if self.removeSiteProcess.ret[0]:
			self._updatesitesModel()
			self.showMainMessage=[True,self.removeSiteProcess.ret[1],"Ok"]
		else:
			self.showMainMessage=[False,self.removeSiteProcess.ret[1],"Error"]

		self._manageOptions()
		self.filterStatusValue="all"
		self.core.mainStack.closePopUp=[True,""]
		self.core.mainStack.closeGui=True

	#def _removeSiteProcessRet

	on_showMainMessage=Signal()
	showMainMessage=Property('QVariantList',_getShowMainMessage,_setShowMainMessage, notify=on_showMainMessage)
	
	on_showRemoveSiteDialog=Signal()
	showRemoveSiteDialog=Property('QVariantList',_getshowRemoveSiteDialog,_setshowRemoveSiteDialog,notify=on_showRemoveSiteDialog)

	on_enableGlobalOptions=Signal()
	enableGlobalOptions=Property(bool,_getEnableGlobalOptions,_setEnableGlobalOptions,notify=on_enableGlobalOptions)

	on_enableChangeStatusOptions=Signal()
	enableChangeStatusOptions=Property('QVariantList',_getEnableChangeStatusOptions,_setEnableChangeStatusOptions,notify=on_enableChangeStatusOptions)

	on_filterStatusValue=Signal()
	filterStatusValue=Property(str,_getFilterStatusValue,_setFilterStatusValue,notify=on_filterStatusValue)

	sitesModel=Property(QObject,_getSitesModel,constant=True)

#class Bridge

from . import Core



from PySide6.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os 
import sys
import threading
import time
import copy

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

from . import SitesModel

SHOW_ALL_SITES=23
HIDE_ALL_SITES=24
REMOVING_ALL_SITES=25


class ChangeAllSitesStatus(QThread):

	def __init__(self,*args):

		QThread.__init__(self)
		self.visible=args[0]
		self.ret={}

	#def __init__

	def run(self,*args):

		time.sleep(0.5)
		self.ret=Bridge.siteManager.changeAllSiteStatus(self.visible)

	#def run

#class ChangeAllSitesStatus

class RemoveAllSites(QThread):

	def __init__(self,*args):

		QThread.__init__(self)
		self.ret={}

	#def __init__

	def run(self,*args):

		time.sleep(0.5)
		self.ret=Bridge.siteManager.removeAllSites()

	#def run

#class RemoveAllSites

	
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

		self.updateSitesModel()
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

	def updateSitesModel(self):

		ret=self._sitesModel.clear()
		sitesEntries=Bridge.siteManager.sitesConfigData

		for item in sitesEntries:
			if item["id"]!="":
				self._sitesModel.appendRow(item["id"],item["img"],item["name"],item["createdBy"],item["updatedBy"],item["isVisible"],item["url"],item["folder"],item["mountUnit"],item["canMount"],item["isActive"])

	#def updateSitesModel

	@Slot(str)
	def manageStatusFilter(self,value):

		self.filterStatusValue=value

	#def manageStatusFilter

	@Slot(bool)
	def changeAllSiteStatus(self,visible):

		self.core.mainStack.closeGui=False
		self.showMainMessage=[False,"","Ok"]
	
		if visible:
			self.core.mainStack.closePopUp=[False,SHOW_ALL_SITES]
		else:
			self.core.mainStack.closePopUp=[False,HIDE_ALL_SITES]
		
		self.changeStatus=ChangeAllSitesStatus(visible)
		self.changeStatus.start()
		self.changeStatus.finished.connect(self._changeSiteStatusRet)

	#def changeAllSiteStatus

	def _changeSiteStatusRet(self):

		self.updateSitesModel()

		if self.changeStatus.ret['status']:
			self.showMainMessage=[True,self.changeStatus.ret["code"],"Ok"]
		else:
			self.showMainMessage=[True,self.changeStatus.ret["code"],"Error"]

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
			if not self.removeAllSites:
				self.core.siteStack.removeSite(self.siteToRemove)
			else:
				self._launchRemoveSiteProcess()

	#def manageRemoveSITEDialog

	def _launchRemoveSiteProcess(self):

		self.core.mainStack.closeGui=False
		self.core.mainStack.closePopUp=[False,REMOVING_ALL_SITES]
	
		self.removeAllSitesProcess=RemoveAllSites()
		self.removeAllSitesProcess.start()
		self.removeAllSitesProcess.finished.connect(self._removeAllSitesProcessRet)

	#def _launchRemoveSiteProcess

	def _removeAllSitesProcessRet(self):

		self.updateSitesModel()

		if self.removeAllSitesProcess.ret['status']:
			self.showMainMessage=[True,self.removeAllSitesProcess.ret["code"],"Ok"]
		else:
			self.showMainMessage=[True,self.removeAllSitesProcess.ret["code"],"Error"]

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



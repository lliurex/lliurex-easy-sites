#!/usr/bin/env python3

import os
import json
import codecs
import datetime
from mimetypes import MimeTypes
import shutil
import glob
import unicodedata
import re
import subprocess
import urllib.request as urllib2
import n4d.client
import cairosvg
from PIL import Image
import time

from jinja2 import Environment
from jinja2.loaders import FileSystemLoader
from jinja2 import Template

import psutil
from pathlib import Path

class SiteManager(object):

	SITE_NAME_MISSING_ERROR=-19
	SITE_NAME_DUPLICATE_ERROR=-20
	IMAGE_FORMART_ERROR=-21
	IMAGE_FILE_MISSING_ERROR=-22
	FOLDER_TOSYNC_MISSING_ERROR=-23
	SITE_ICON_ERROR=-24
	FREE_SPACE_ERROR=-25

	ALL_DATA_CORRECT=0

	def __init__(self,server=None):

		super(SiteManager, self).__init__()

		self.dbg=0
		self.userValidated=False
		self.credentials=[]
		self.sitesConfigData=[]
		self.netFolder="/net/server-sync/easy-sites"
		self.imageDir=os.path.expanduser("~/.cache/")+"easy-sites"
		self.urlSite="http://server/easy-sites/easy-"
		self.adiServer="/usr/bin/natfree-adi"
		self.stockImagesFolder="/usr/share/lliurex-easy-sites/images"
		self.tmpIconPath="/tmp/easy-"
		self.loadError=False
		self.origImagePath=""
		self.systemdPath="/etc/systemd/system"
		self.sitesIconsFolder="/var/www/easy-sites/icons"
		self._getSystemLocale()
		self.initValues()
	
	#def __init__	
	
	def createN4dClient(self,ticket,passwd):

		ticket=ticket.replace('##U+0020##',' ')
		self.serverIP=ticket.split(' ')[1].split(":")[1].split("//")[1]
		self.credentials.append(ticket.split(' ')[2])
		self.credentials.append(passwd)

		self.tk=n4d.client.Ticket(ticket)
		self.client=n4d.client.Client(ticket=self.tk)

		'''
		self.localClient=n4d.client.Client("https://localhost:9779",self.credentials[0],self.credentials[1])
		local_t=self.localClient.get_ticket()
		if local_t.valid():
			self.localClient=n4d.client.Client(ticket=local_t)
			self.userValidated=True
		else:
			self.userValidated=False
		'''
		
	#def createN4dClient

	def _debug(self,function,msg):

		if self.dbg==1:
			print("[EASY_SITES]: "+ str(function) + str(msg))

	#def _debug

	def initValues(self):

		if not os.path.exists(self.imageDir):
			os.makedirs(self.imageDir)

		self.siteToLoad=""
		self.siteName=""
		self.siteDescription=""
		self.siteImage=["stock","/usr/share/lliurex-easy-sites/images/custom.png"]
		self.siteFolder=""
		self.siteUrl=""
		self.isSiteVisible=True
		self.origImagePath=""
		self.mountUnit=False
		self.canMount=False
		self.autoMount="disable"
		self.freeSpaceChecked=[]
		
		self.currentSiteConfig={}
		self.currentSiteConfig["id"]=self.siteToLoad
		self.currentSiteConfig["name"]=self.siteName
		self.currentSiteConfig["description"]=self.siteDescription
		self.currentSiteConfig["image"]={}
		self.currentSiteConfig["image"]["option"]=self.siteImage[0]
		self.currentSiteConfig["image"]["img_path"]=self.siteImage[1]
		self.currentSiteConfig["site_folder"]=self.siteFolder
		self.currentSiteConfig["sync_folder"]=""
		self.currentSiteConfig["url"]=self.siteUrl
		self.currentSiteConfig["icon"]=""
		self.currentSiteConfig["visibility"]=self.isSiteVisible
		self.currentSiteConfig["author"]=""
		self.currentSiteConfig["updated_by"]=""
		self.currentSiteConfig["date_creation"]=""
		self.currentSiteConfig["last_update"]=""
		self.currentSiteConfig["mountUnit"]=self.mountUnit
		self.currentSiteConfig["systemdUnit"]=None
		self.currentSiteConfig["auto_mount"]=self.autoMount

	#def initValues		

	def readConf(self):
		
		result=self.client.EasySitesManager.read_conf()
		self._debug("Read configuration file: ",result)
		self.sitesConfig=result["data"]
		self.sitesConfigData=[]
		if result["status"]:
			self._getSitesConfig()

		return result
		
	#def readConf

	def _getSitesConfig(self):

		for item in self.sitesConfig:
			tmp={}
			tmp["id"]=self.sitesConfig[item]["id"]
			tmp["name"]=self.sitesConfig[item]["name"]
			tmp["createdBy"]=self.sitesConfig[item]["author"]
			tmp["updatedBy"]=self.sitesConfig[item]["updated_by"]
			tmp["url"]=self.sitesConfig[item]["url"]
			tmp["folder"]=self.sitesConfig[item]["site_folder"]
			tmp["isVisible"]=self.sitesConfig[item]["visibility"]
			tmp["mountUnit"]=self.sitesConfig[item]["mountUnit"]
			if self.sitesConfig[item]["image"]["option"]=="stock":
				tmp["img"]=self.sitesConfig[item]["image"]["img_path"]
			else:
				tmp["img"]=self._getImageFromSite(self.sitesConfig[item]["image"]["img_path"])

			if os.path.exists(self.sitesConfig[item]["sync_folder"]):
				self.canMount=True
			else:
				self.canMount=False
			
			tmp["canMount"]=self.canMount
			
			if tmp["mountUnit"]:
				isActive=self._getSystemdUnitStatus(self.sitesConfig[item]["systemdUnit"])
				tmp["isActive"]=isActive
			else:
				tmp["isActive"]=False
			
			self.sitesConfigData.append(tmp)

	#def _getSitesConfig

	def loadSiteConfig(self,siteToLoad):

		self.siteToLoad=siteToLoad
		self.currentSiteConfig=self.sitesConfig[siteToLoad]
		self.origImagePath=self.currentSiteConfig["image"]["img_path"]

		self.siteName=self.currentSiteConfig["name"]
		
		if self.currentSiteConfig["image"]["option"]=="stock":
			error=False
			imgPath=self.currentSiteConfig["image"]["img_path"]
		else:
			error=False
			imgPath=self.currentSiteConfig["image"]["img_path"]
			if not os.path.exists(imgPath):
				error=True
				imgPath=os.path.join(self.stockImagesFolder,"no_disp.png")
			self.currentSiteConfig["image"]["img_path"]=imgPath
		
		self.siteImage=[self.currentSiteConfig["image"]["option"],imgPath,error]
		self.siteDescription=self.currentSiteConfig["description"]
		self.siteFolder=self.currentSiteConfig["sync_folder"]
		self.isSiteVisible=self.currentSiteConfig["visibility"]
		self.mountUnit=self.currentSiteConfig["mountUnit"]
		self.autoMount=self.currentSiteConfig["auto_mount"]
		if os.path.exists(self.currentSiteConfig["sync_folder"]):
			self.canMount=True
		else:
			self.canMount=False

		self.freeSpaceChecked=[]

	#def loadSiteConfig

	def saveData(self,action,data,completeData=True):

		action=action
		error=False

		result={}
				
		if action in ["add","edit"]:
			info=data[0]
	
		elif action in ["sync","visibility","mount"]:
			info=self.sitesConfig[data[0]]
			'''
			if self.origImagePath!="":
				info["image"]["img_path"]=self.origImagePath
			'''
		if completeData:
			newImage=info["image"]["img_path"]
			info.update(self._formatData(info,action))
			if info["mountUnit"]:
				info["systemdUnit"]=self._getSystemdUnitName(info["site_folder"])
			else:
				info["systemdUnit"]=None
		
		
		if action=="add" or action=="edit":
			requiredSync=data[1]
			generateSiteIcon=False
			
			if action=="add":
				generateSiteIcon=True
				info["icon"]="easy-%s.png"%info["id"]
			else:
				if info["id"]!=self.currentSiteConfig["id"]:
					generateSiteIcon=True
					info["icon"]="easy-%s.png"%info["id"]
				else:
					currentImg=os.path.basename(self.currentSiteConfig["image"]["img_path"])
					if os.path.basename(newImage)!=currentImg:
						generateSiteIcon=True
	
			if generateSiteIcon:
				siteIconPath="%s%s.png"%(self.tmpIconPath,info["id"])
				result=self._generateSiteIcon(siteIconPath,newImage)
			else:
				siteIconPath=None
				result["status"]=True
			
			if result["status"]:
				if action=="add":			
					result=self.client.EasySitesManager.create_new_site(info,siteIconPath)
					if not result['status']:
						self.client.EasySitesManager.delete_site(info["id"],info["systemdUnit"])	
					
					self._removeTmpFiles(siteIconPath)		
					
					self._debug("Create new site: ",result)

				elif action=="edit":	
					confirmEdit=True
					origId=self.currentSiteConfig["id"]
					result=self.client.EasySitesManager.edit_site(info,siteIconPath,origId,requiredSync)
					self._removeTmpFiles(siteIconPath)

					self._debug("Edit new site: ",result)

		elif action=="delete":
			siteId=data
			result=self.client.EasySitesManager.delete_site(siteId,self.sitesConfig[siteId]["systemdUnit"])
			self._debug("Delete site: ",result)

		elif action=="visibility":
			info["visibility"]=data[1]
			result=self.client.EasySitesManager.change_site_visibility(info)
			
			self._debug("Change visibility: ",result)

		elif action=="mount":
			systemdUnit=info["systemdUnit"]
			action=data[1]
			result=self.client.EasySitesManager.manage_systemd_status(systemdUnit,action)

			self._debug("Change mount status: ",result)
		
		elif action=="sync":
			siteId=data[0]
			syncFrom=data[1]
			result=self.client.EasySitesManager.sync_content(siteId,syncFrom)

			self._debug("Sync new content: ",result)
		
		if result["status"]:
			retRead=self.readConf()
			if not retRead["status"]:
				result=retRead
		
		return result	
	
	#def save_conf		

	def checkData(self,data,edit,origId=None):

		checkImage=None
		sitesKeys=self.sitesConfig.keys()
		
		if data["name"]=="":
			return {"result":False,"code":SiteManager.SITE_NAME_MISSING_ERROR,"data":""}

		else:
			checkDuplicates=True
			if edit:
				if data["id"]==origId:
					checkDuplicates=False

			if checkDuplicates:		
				if data["id"] in sitesKeys:
					return {"result":False,"code":SiteManager.SITE_NAME_DUPLICATE_ERROR,"data":""}
							
		if not edit:
			if data["sync_folder"]==None or data["sync_folder"]=="":
				return {"result":False,"code":SiteManager.FOLDER_TOSYNC_MISSING_ERROR,"data":""}

		if data["image"]["option"]=="custom":						
			if data["image"]["img_path"]!=None or data["image"]["img_path"]!="":
				checkImage=self.checkMimeTypes(data["image"]["img_path"])
				
			else:
				return {"result":False,"code":SiteManager.IMAGE_FILE_MISSING_ERROR,"data":""}
		
		if not data["mountUnit"]:
			if len(self.freeSpaceChecked)>0 and not self.freeSpaceChecked[0]:
				return {"result":False,"code":SiteManager.FREE_SPACE_ERROR,"data":""}
		
		if checkImage==None:
			return {"result":True,"code":SiteManager.ALL_DATA_CORRECT,"data":""}
						
		else:
			return checkImage			
	
	#def check_data
	
	def checkMimeTypes(self,file):

		mime = MimeTypes()
		fileMimeType= mime.guess_type(file)
		error=False
		if fileMimeType[0]!=None:
			if not 'image' in fileMimeType[0]: 
				error=True
		else:
			error=True

		if error:
			return {"result":False,"code":SiteManager.IMAGE_FORMART_ERROR,"data":""}				
		else:
			return {"result":True,"code":"","data":""}

	#def checkMimeTypes			
				
	def getSiteId(self,name):

		siteId= ''.join((c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn'))
		siteId=siteId.lower().replace(" ","_")
		siteId=re.sub(r'[^\w\s-]', '', siteId).strip()
		siteId=re.sub(r'[-\s]+', '', siteId)
		siteId=re.sub(r'[_\s]+', '_', siteId)

		return siteId

	#def getSiteId

	def _removeTmpFiles(self,siteIconPath):
	
		if siteIconPath!=None:
			if os.path.exists(siteIconPath):
				os.remove(siteIconPath)
	
	#def _removeTmpFiles		
	
	def _copyImageFile(self,siteId,copy_image):

		imageName=os.path.basename(copy_image)
		tmpImage="."+imageName
		destSite="easy-"+siteId
		destSitePath=os.path.join(self.netFolder,destSite)
		destPath=os.path.join(destSitePath,tmpImage)
		try:
			ret=self.client.EasySitesManager.copy_image_to_site(copy_image,destPath)
		except n4d.client.CallFailedError as e:
			pass
	
	#def _copyImageFile

	def _formatData(self,data,action):

		tmp={}
		tmp["url"]="%s%s"%(self.urlSite,data["id"])
		tmp["site_folder"]="%s/easy-%s"%(self.netFolder,data["id"])
		tmp["updated_by"]=self.credentials[0]
		tmp["last_update"]=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

		if data["image"]["option"]=="custom":
			imgBasename=os.path.basename(data["image"]["img_path"])
			tmp["image"]={}
			tmp["image"]["option"]=data["image"]["option"]
			if "no_disp" in imgBasename:
				tmp["image"]["img_path"]=self.origImagePath
			else:
				tmp["image"]["img_path"]="%s/easy-%s.png"%(self.sitesIconsFolder,data["id"])

		if action=="add":
			tmp["author"]=self.credentials[0]
			tmp["date_creation"]=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

		return tmp

	#def _formatData

	def _generateSiteIcon(self,siteIconPath,imgPath):

		result={}
		result["status"]=True
		imgBasename=os.path.basename(imgPath)

		if 'svg' in imgBasename:
			try:
				cairosvg.svg2png(url=imgPath,write_to=siteIconPath)
				imgPath=siteIconPath
			except Exception as e:
				result["status"]=False
				result ["msg"]=e
				result["code"]=SiteManager.SITE_ICON_ERROR
				return result
		try:
			tmpImg=Image.open(imgPath)
			tmpImg=tmpImg.resize((110,110))
			tmpImg.save(siteIconPath)
			tmpImg.close()

			return result
		
		except Exception as e:
			result["status"]=False
			result ["msg"]=e
			result["code"]=SiteManager.SITE_ICON_ERROR
			return result

	#def _generateSiteIcon

	def _searchMeta(self,meta):

		match=False
		for item in self.flavours:
			if meta in item:
				match=True
				break

		return match

	#def_ searchMeta

	def _getSystemLocale(self):

		language=os.environ["LANGUAGE"]

		if language!="":
			tmpLang=language.split(":")
			self.systemLocale=tmpLang[0]
		else:
			self.systemLocale=os.environ["LANG"]

	#def _getSystemLocale

	def _getImageFromSite(self,imgPath):

		if os.path.exists(imgPath):
			return imgPath
		else:
			return os.path.join(self.stockImagesFolder,"no_disp.png")

	#def _getImageFromSite	

	def checkGlobalOptionStatus(self):

		if len(self.sitesConfig)>0:
			return True
		else:
			return False
			
	#def checkGlobalOptionStatus

	def checkChangeStatusSitesOption(self):

		allActivated=False
		allDeactivated=False
		enableStatusFilter=True
		countActivated=0
		countDeactivated=0
		result=[]
		
		if len(self.sitesConfig)>0:
			for item in self.sitesConfig:
				if self.sitesConfig[item]['visibility']:
					countActivated+=1
				else:
					countDeactivated+=1

			if countActivated==0:
				allDeactivated=True
				enableStatusFilter=False

			if countDeactivated==0:
				allActivated=True
				enableStatusFilter=False
		else:
			enableStatusFilter=False

		result=[allActivated,allDeactivated,enableStatusFilter]

		return result

	#def checkChangeStatusSitesOption

	def removeAllSites(self):

		result=self.client.EasySitesManager.delete_all_sites()
		self._debug("Remove all sites: ",result)
		retRead=self.readConf()
		
		if not retRead["status"]:
			result=retRead

		return result

	#def removeAllSites

	def changeAllSiteStatus(self,visible):

		result=self.client.EasySitesManager.change_all_sites_visibility(visible)
		self._debug("Change visibility all sites: ",result)
		retRead=self.readConf()
		
		if not retRead["status"]:
			result=retRead

		return result

	#def changeAllSiteStatus

	def checkFreeSpace(self,syncFrom):

		freeSpaceBytes=psutil.disk_usage("/").free
		freespaceGb=round(psutil.disk_usage("/").free/(1024**3),2)
		folderToCheck=Path(syncFrom)
		sizeOfContentBytes=sum(f.stat().st_size for f in folderToCheck.rglob('*') if f.is_file())
		sizeOfContentGb=round(sum(f.stat().st_size for f in folderToCheck.rglob('*') if f.is_file())/(1024**3),2)

		canCopy=True
		self.freeSpaceChecked=[]

		if sizeOfContentGb<0.1:
			sizeOfContent="%s MB"%str(round(sum(f.stat().st_size for f in folderToCheck.rglob('*') if f.is_file())/(1024**2),2))
		else:
			sizeOfContent="%s GB"%str(sizeOfContentGb)

		
		sizeAfterCopy=round((freeSpaceBytes-sizeOfContentBytes)/(1024**3),2)

		if freespaceGb<5 or sizeAfterCopy<5:
			canCopy=False
		
		self.freeSpaceChecked.append(canCopy)
		self.freeSpaceChecked.append(sizeOfContent)
		self.freeSpaceChecked.append("%s GB"%str(freespaceGb))
		self.freeSpaceChecked.append("%s GB"%str(sizeAfterCopy))

		return self.freeSpaceChecked

	#def getFreeSpace

	def _getSystemdUnitName(self,siteFolder):

		try:
			result=subprocess.run(['systemd-escape','-p','--suffix=mount',siteFolder],capture_output=True,text=True,check=True)
			return result.stdout.strip().replace("'","")
		except subprocess.CalledProcessError as e:
			return None

	#def _getSystemdUnitName

	def _getSystemdUnitStatus(self,systemdUnit):

		if os.path.exists(os.path.join(self.systemdPath,systemdUnit)):
			try:
				result=subprocess.run(["systemctl","is-active","--quiet", systemdUnit])
				if result.returncode==0:
					return True
				else:
					return False
			except Exception as e:
				return False

	#def _getSystemdUnitStatus


#class SiteManager

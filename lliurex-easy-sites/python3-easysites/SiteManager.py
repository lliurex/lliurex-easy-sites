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



class SiteManager(object):

	SITE_NAME_MISSING_ERROR=-1
	SITE_NAME_DUPLICATE_ERROR=-2
	IMAGE_FORMART_ERROR=-5
	IMAGE_FILE_MISSING_ERROR=-7
	FOLDER_TOSYNC_MISSING_ERROR=-8
	SCP_CONTENT_TOSERVER_ERROR=-39
	SCP_FILE_TOSERVER_ERROR=-40
	SITE_ICON_ERROR=-41

	ALL_DATA_CORRECT=0
	SYNC_CONTENT_CORRECT=8

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
		self.detectFlavour()
		self._getSystemLocale()
		self.initValues()	
	
	#def __init__	
	
	def detectFlavour(self):
		
		cmd='lliurex-version -v'
		p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
		result=p.communicate()[0]

		if type(result) is bytes:
			result=result.decode()
		self.flavours = [ x.strip() for x in result.split(',') ]

	#def detect_flavour

	def createN4dClient(self,ticket,passwd):

		ticket=ticket.replace('##U+0020##',' ')
		self.serverIP=ticket.split(' ')[1].split(":")[1].split("//")[1]
		self.credentials.append(ticket.split(' ')[2])
		self.credentials.append(passwd)

		self.tk=n4d.client.Ticket(ticket)
		self.client=n4d.client.Client(ticket=self.tk)

		self.localClient=n4d.client.Client("https://localhost:9779",self.credentials[0],self.credentials[1])
		local_t=self.localClient.get_ticket()
		if local_t.valid():
			self.localClient=n4d.client.Client(ticket=local_t)
			self.userValidated=True
		else:
			self.userValidated=False

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
		
		self.currentSiteConfig={}
		self.currentSiteConfig["id"]=self.siteToLoad
		self.currentSiteConfig["name"]=self.siteName
		self.currentSiteConfig["description"]=self.siteDescription
		self.currentSiteConfig["image"]={}
		self.currentSiteConfig["image"]["option"]=self.siteImage[0]
		self.currentSiteConfig["image"]["img_path"]=self.siteImage[1]
		self.currentSiteConfig["sync_folder"]=self.siteFolder
		self.currentSiteConfig["site_folder"]=""
		self.currentSiteConfig["url"]=self.siteUrl
		self.currentSiteConfig["visibility"]=self.isSiteVisible
		self.currentSiteConfig["author"]=""
		self.currentSiteConfig["updated_by"]=""
		self.currentSiteConfig["date_creation"]=""
		self.currentSiteConfig["last_update"]=""
	
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
			if self.sitesConfig[item]["image"]["option"]=="stock":
				tmp["img"]=os.path.join(self.stockImagesFolder,"custom.png")
			else:
				tmp["img"]=self._getImageFromSite(self.sitesConfig[item]["image"]["img_path"])

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
			imgName=self.currentSiteConfig["image"]["img_path"].split("/.")[1]
			if os.path.exists(os.path.join(self.imageDir,imgName)):
				error=False
				imgPath=os.path.join(self.imageDir,imgName)
			else:
				error=True
				imgPath=os.path.join(self.stockImagesFolder,"no_disp.png")
		
			self.currentSiteConfig["image"]["img_path"]=imgPath

		self.siteImage=[self.currentSiteConfig["image"]["option"],imgPath,error]
		self.siteDescription=self.currentSiteConfig["description"]
		self.siteFolder=self.currentSiteConfig["sync_folder"]
		self.isSiteVisible=self.currentSiteConfig["visibility"]
		
	#def loadSiteConfig

	def saveData(self,action,data,completeData=True):

		action=action
		error=False

		result={}
		
		if action in ["add","edit"]:
			info=data[0]
		elif action in ["sync","visibility"]:
			info=self.sitesConfig[data[0]]

		if completeData:
			newImage=info["image"]["img_path"]
			info.update(self._formatData(info,action))
		
		if action=="add" or action=="edit":

			requiredSync=data[1]
			generateSiteIcon=False
			
			if action=="add":
				generateSiteIcon=True
			else:
				if info["id"]!=self.currentSiteConfig["id"]:
					generateSiteIcon=True
				else:
					currentImg=os.path.basename(self.currentSiteConfig["image"]["img_path"])
					if os.path.basename(newImage)!=currentImg:
						generateSiteIcon=True
	
			siteIconPath="%s%s.png"%(self.tmpIconPath,info["id"])

			if generateSiteIcon:
				result=self._generateSiteIcon(siteIconPath,newImage)
			else:
				result["status"]=True
			
			if result["status"]:
				if action=="add":			
					result=self.client.EasySitesManager.create_new_site(info,siteIconPath)
					if result['status']:
						resultSync=self.syncContent(info["id"],info["sync_folder"])
						if resultSync['status']:
							if info["image"]["option"]=="custom":
								self.copyImageFile(info["id"],newImage)
						else:
							self.client.EasySitesManager.delete_site(info["id"])	
							result=resultSync
					
					self.removeTmpFiles(siteIconPath)		
					
					self._debug("Create new site: ",result)

				elif action=="edit":	
					confirmEdit=True
					origId=self.currentSiteConfig["id"]
					result=self.client.EasySitesManager.edit_site(info,siteIconPath,origId)
					if result['status']:
						if requiredSync:
							resultSync=self.syncContent(info["id"],info["sync_folder"])
							if not resultSync['status']:
								confirmEdit=False
								result=resulSync
						if confirmEdit:
							if info["image"]["option"]=="custom":
								if newImage!=os.path.basename(self.currentSiteConfig["image"]["img_path"]):
									self.copyImageFile(info["id"],newImage)

					self.removeTmpFiles(siteIconPath)

					self._debug("Edit new site: ",result)

		elif action=="delete":
			siteId=data
			result=self.client.EasySitesManager.delete_site(siteId)
			self._debug("Delete site: ",result)

		elif action=="visibility":
			info["visibility"]=data[1]
			visible=data[1]
			result=self.client.EasySitesManager.change_site_visibility(info,visible)
			self._debug("Change visibility: ",result)

		elif action=="sync":
			siteId=data[0]
			syncFrom=data[1]
			info["sync_folder"]=data[1]
			result=self.syncContent(siteId,syncFrom)

			if result['status']:
				resultWrite=self.client.EasySitesManager.write_conf(info)
				if not resultWrite['status']:
					result=resultWrite
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
		siteId=re.sub(r'[-\s]+', '-', siteId)

		return siteId

	#def getSiteId

	def copySiteIconFile(self,siteIconPath):
		
		result={}
		result['status']=True
		
		try:
			copyPixBuf=self.localClient.ScpManager.send_file(self.credentials[0],self.credentials[1],self.serverIP,siteIconPath,"/tmp/")
			return result
		except n4d.client.CallFailedError as e:
			result['status']=False
			result['msg']=e
			result['code']=SiteManager.SCP_FILE_TOSERVER_ERROR
			return result

	#def copySiteIconFile	

	def removeTmpFiles(self,siteIconPath):
	
		if os.path.exists(siteIconPath):
			os.remove(siteIconPath)
	
	#def removeTmpFiles		

	def syncContent(self,siteId,sync_from):
		
		destSite="easy-"+siteId
		destSitePath=os.path.join(self.netFolder,destSite)
		result={}
		result['status']=True
		result['code']=SiteManager.SYNC_CONTENT_CORRECT

		try:
			syncContent=self.localClient.ScpManager.send_dir(self.credentials[0],self.credentials[1],self.serverIP,sync_from,destSitePath,True)
			return result
		except n4d.client.CallFailedError as e:
			result['status']=False
			result['msg']=e
			result['code']=SiteManager.SCP_CONTENT_TOSERVER_ERROR
			return result
		
	#def syncContent

	def copyImageFile(self,siteId,copy_image):

		imageName=os.path.basename(copy_image)
		if not os.path.exists(os.path.join(self.imageDir,imageName)):
			shutil.copy(copy_image,self.imageDir)
		tmpImage="."+imageName
		destSite="easy-"+siteId
		destSitePath=os.path.join(self.netFolder,destSite)
		destPath=os.path.join(destSitePath,tmpImage)
		try:
			ret=self.localClient.ScpManager.send_file(self.credentials[0],self.credentials[1],self.serverIP,copy_image,destPath)
		except n4d.client.CallFailedError as e:
			pass
	
	#def copyImageFile

	def _formatData(self,data,action):

		tmp={}
		tmp["url"]="%s%s"%(self.urlSite,data["id"])
		tmp["site_folder"]="%s/easy-%s"%(self.netFolder,data["id"])
		tmp["updated_by"]=self.credentials[0]
		tmp["last_updated"]=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

		if data["image"]["option"]=="custom":
			imgBasename=os.path.basename(data["image"]["img_path"])
			tmp["image"]={}
			tmp["image"]["option"]=data["image"]["option"]
			if "no_disp" in imgBasename:
				tmp["image"]["img_path"]=self.origImagePath
			else:
				tmp["image"]["img_path"]="%s/.%s"%(tmp["url"],imgBasename)

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

		imgFile=imgPath.split("/.")[1]
		localImgPath=os.path.join(self.imageDir,imgFile)

		if os.path.exists(localImgPath):
			return localImgPath
		else:
			try:
				req=urllib2.Request(imagePath)
				res=urllib2.urlopen(req)
				f=open(localImgPath,"wb")
				f.write(res.read())
				f.close()
				return localImgPath
			except Exception as e:
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


#class SiteManager

#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, GLib
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

from jinja2 import Environment
from jinja2.loaders import FileSystemLoader
from jinja2 import Template



class SiteManager(object):

	SITE_NAME_MISSING_ERROR=-1
	SITE_NAME_DUPLICATE_ERROR=-2
	IMAGE_FORMART_ERROR=-3
	IMAGE_FILE_MISSING_ERROR=-4
	FOLDER_TOSYNC_MISSING_ERROR=-5
	SCP_CONTENT_TOSERVER_ERROR=-13
	SCP_FILE_TOSERVER_ERROR=-17

	ALL_CORRECT_CODE=0

	def __init__(self,server=None):

		super(SiteManager, self).__init__()

		self.dbg=0
		self.userValidated=False
		self.credentials=[]
		self.sitesConfigData=[]
		self.netFolder="/net/server-sync/easy-sites"
		self.imageDir=os.path.expanduser("~/.cache/")+"easy-sites"
		self.urlSite="http://server/easy-sites/easy-"
		self.adiClient="/usr/bin/natfree-client"
		self.stockImagesFolder="/usr/share/lliurex-easy-sites/images"
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

		print(ticket)
		print(passwd)
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
		self.currentSiteConfig["name"]=self.siteName
		self.currentSiteConfig["description"]=self.siteDescription
		self.currentSiteConfig["image"]={}
		self.currentSiteConfig["image"]["option"]=self.siteImage[0]
		self.currentSiteConfig["image"]["path"]=self.siteImage[1]
		self.currentSiteConfig["folder"]=self.siteFolder
		self.currentSiteConfig["url"]=self.siteUrl
		self.currentSiteConfig["isVisible"]=self.isSiteVisible
	
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

		print(self.sitesConfigData)
		
	#def _getSitesConfig

	def loadSiteConfig(self,siteToLoad):

		self.siteToLoad=siteToLoad
		self.currentSiteConfig=self.sitesConfig[siteToLoad]
		
		self.siteName=self.currentSiteConfig["name"]
		if self.currentSiteConfig["image"]["option"]=="stock":
			imgPath=self.currentSiteConfig["image"]["img_path"]
		else:
			imgName=self.currentSiteConfig["image"]["img_path"].split("/.")[1]
			if os.path.exists(os.path.join(self.imageDir,imgName)):
				imgPath=os.path.join(self.imageDir,imgName)
			else:
				imgPath=os.path.join(self.stockImagesFolder,"no_disp.png")
		
		self.siteImage=[self.currentSiteConfig["image"]["option"],imgPath]

		self.siteFolder=self.currentSiteConfig["sync_folder"]
		self.isSiteVisible=self.currentSiteConfig["visibility"]
		
	#def loadSiteConfig

	def save_conf(self,args):

		action=args[0]
		error=False

		if action=="add" or action=="edit":
			info=args[1]
			pixbuf=args[2]
			copy_image=args[4]
			pixbuf_path="/tmp/easy-"+info["id"]+".png"
			pixbuf.savev(pixbuf_path, 'png', [], [])

			copy_image_client=False
			if self._searchMeta('client'):
				copy_image_client=True
			elif self._searchMeta('desktop'):
				if os.path.exists(self.adiClient):
					copy_image_client=True

			if copy_image_client:
				result=self.copyPixBufFile(pixbuf_path)
				if not result['status']:
					error=True
			
			if not error:
				if action=="add":			
					result=self.client.EasySitesManager.create_new_site(info,pixbuf_path)
					if result['status']:
						result=self.syncContent(info["id"],info["sync_folder"])
						if result['status']:
							if copy_image!="":
								self.copyImageFile(info["id"],copy_image)
							#self.n4d.write_conf(self.credentials,'EasySitesManager',info)
						else:
							self.client.EasySitesManager.delete_site(info["id"])	

					self.removeTmpFiles(pixbuf_path)		
					
					self._debug("Create new site: ",result)

				elif action=="edit":	
					confirm_edit=True
					origId=args[5]
					require_sync=args[3]			
					result=self.client.EasySitesManager.edit_site(info,pixbuf_path,origId)
					if result['status']:
						if require_sync:
							result=self.syncContent(info["id"],info["sync_folder"])
							if not result['status']:
								confirm_edit=False
						if confirm_edit:
							if copy_image!="":
								self.copyImageFile(info["id"],copy_image)

							#self.n4d.write_conf(self.credentials,'EasySitesManager',info)		
					
					self.removeTmpFiles(pixbuf_path)
					self._debug("Edit new site: ",result)

	
		elif action=="delete":
			siteId=args[1]
			result=self.client.EasySitesManager.delete_site(siteId)
			self._debug("Delete site: ",result)

		elif action=="visibility":
			info=args[1]
			visible=args[2]
			result=self.client.EasySitesManager.change_site_visibility(info,visible)
			'''
			if result['status']:
				info["visible"]=visible
				self.n4d.write_conf(self.credentials,'EasySitesManager',info)
			'''
			self._debug("Change visibility: ",result)

		elif action=="sync":
			info=args[1]
			siteId=info["id"]
			sync_from=args[2]
			result=self.syncContent(siteId,sync_from)
			if result['status']:
				info["sync_folder"]=sync_from
				info["updated_by"]=args[3]
				info["last_updated"]=args[4]
				result_write=self.client.EasySitesManager.write_conf(info)
				if not result_write['status']:
					result=result_write
			self._debug("Sync new content: ",result)
		
		return result	
	
	#def save_conf		

	def checkData(self,data,edit,orig_id=None):

		checkImage=None
		sitesKeys=self.sitesConfig.keys()
		
		if data["name"]=="":
			return {"result":False,"code":SiteManager.SITE_NAME_MISSING_ERROR,"data":""}

		else:
			checkDuplicates=True
			if edit:
				if data["id"]==orig_id:
					checkDuplicates=False

			if checkDuplicates:		
				if data["id"] in sitesKeys:
					return {"result":False,"code":SiteManager.SITE_NAME_DUPLICATE_ERROR,"data":""}
			 			
							
		if not edit:
			if data["sync_folder"]==None:
				return {"result":False,"code":SiteManager.FOLDER_TOSYNC_MISSING_ERROR,"data":""}

		if data["image"]["option"]=="custom":						
			if data["image"]["path"]!=None:
				checkImage=self.checkMimeTypes(data["image"]["path"])
				
			else:
				return {"result":False,"code":SiteManager.IMAGE_FILE_MISSING_ERROR,"data":""}
		
		if checkImage==None:
			return {"result":True,"code":SiteManager.ALL_CORRECT_CODE,"data":""}
						
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
		
	#def checkMimeTypes			
				
	def getSiteId(self,name):

		siteId= ''.join((c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn'))
		siteId=siteId.lower().replace(" ","_")
		siteId=re.sub('[^\w\s-]', '', siteId).strip()
		siteId=re.sub('[-\s]+', '-', siteId)

		return siteId

	#def getSiteId

	def copyPixBufFile(self,pixbuf_path):
		
		result={}
		result['status']=True
		
		try:
			copyPixBuf=self.localClient.ScpManager.send_file(self.credentials[0],self.credentials[1],self.serverIP,pixbuf_path,"/tmp/")
			return result
		except n4d.client.CallFailedError as e:
			result['status']=False
			result['msg']=e
			result['code']=SiteManager.SCP_FILE_TOSERVER_ERROR
			return result

	#def copyPixBufFile	

	def removeTmpFiles(self,pixbuf_path):
	
		if os.path.exists(pixbuf_path):
			os.remove(pixbuf_path)
	
	#def removeTmpFiles		

	def syncContent(self,siteId,sync_from):
		
		destSite="easy-"+siteId
		destSitePath=os.path.join(self.netFolder,destSite)
		result={}
		result['status']=True

		try:
			syncContent=self.localClient.ScpManager.send_dir(self.credentials[0],self.credentials[1],"server",sync_from,destSitePath,True)
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
				print(str(e))
				return os.path.join(self.stockImagesFolder,"custom.png")


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

	#def checkChangeStatusBellsOption


#class SiteManager

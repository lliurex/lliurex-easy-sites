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
		self.user_validated=False
		self.credentials=[]
		self.net_folder="/net/server-sync/easy-sites"
		self.image_dir=os.path.expanduser("~/.cache/")+"easy-sites"
		self.url_site="http://server/easy-sites/easy-"
		self.detect_flavour()	
	
	#def __init__	
	
	def detect_flavour(self):
		
		cmd='lliurex-version -v'
		p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
		result=p.communicate()[0]

		if type(result) is bytes:
			result=result.decode()
		self.flavours = [ x.strip() for x in result.split(',') ]

	#def detect_flavour

	def create_n4dClient(self,ticket,passwd):

		ticket=ticket.replace('##U+0020##',' ')
		self.server_ip=ticket.split(' ')[1].split(":")[1].split("//")[1]
		self.credentials.append(ticket.split(' ')[2])
		self.credentials.append(passwd)

		self.tk=n4d.client.Ticket(ticket)
		self.client=n4d.client.Client(ticket=self.tk)

		self.local_client=n4d.client.Client("https://localhost:9779",self.credentials[0],self.credentials[1])
		local_t=self.local_client.get_ticket()
		if local_t.valid():
			self.local_client=n4d.client.Client(ticket=local_t)
			self.user_validated=True
		else:
			self.user_validated=False

	#def create_n4dClient

	def _debug(self,function,msg):

		if self.dbg==1:
			print("[EASY_SITES]: "+ str(function) + str(msg))

	#def _debug		

	def read_conf(self):
		
		result=self.client.EasySitesManager.read_conf()
		self._debug("Read configuration file: ",result)
		self.sites_config=result["data"]
		return result
		
	#def read_conf	

	def save_conf(self,args):

		action=args[0]
		error=False

		if action=="add" or action=="edit":
			info=args[1]
			pixbuf=args[2]
			copy_image=args[4]
			pixbuf_path="/tmp/easy-"+info["id"]+".png"
			pixbuf.savev(pixbuf_path, 'png', [], [])

			if self._searchMeta('client'):
				result=self.copy_pixbuf_file(pixbuf_path)
				if not result['status']:
					error=True
			
			if not error:
				if action=="add":			
					result=self.client.EasySitesManager.create_new_site(info,pixbuf_path)
					if result['status']:
						result=self.sync_content(info["id"],info["sync_folder"])
						if result['status']:
							if copy_image!="":
								self.copy_image_file(info["id"],copy_image)
							#self.n4d.write_conf(self.credentials,'EasySitesManager',info)
						else:
							self.client.EasySitesManager.delete_site(info["id"])	

					self.remove_tmp_files(pixbuf_path)		
					
					self._debug("Create new site: ",result)

				elif action=="edit":	
					confirm_edit=True
					origId=args[5]
					require_sync=args[3]			
					result=self.client.EasySitesManager.edit_site(info,pixbuf_path,origId)
					if result['status']:
						if require_sync:
							result=self.sync_content(info["id"],info["sync_folder"])
							if not result['status']:
								confirm_edit=False
						if confirm_edit:
							if copy_image!="":
								self.copy_image_file(info["id"],copy_image)

							#self.n4d.write_conf(self.credentials,'EasySitesManager',info)		
					
					self.remove_tmp_files(pixbuf_path)
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
			result=self.sync_content(siteId,sync_from)
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

	def check_data(self,data,edit,orig_id=None):

		check_image=None
		sites_keys=self.sites_config.keys()
		
		if data["name"]=="":
			return {"result":False,"code":SiteManager.SITE_NAME_MISSING_ERROR,"data":""}

		else:
			check_duplicates=True
			if edit:
				if data["id"]==orig_id:
					check_duplicates=False

			if check_duplicates:		
				if data["id"] in sites_keys:
					return {"result":False,"code":SiteManager.SITE_NAME_DUPLICATE_ERROR,"data":""}
			 			
							
		if not edit:
			if data["sync_folder"]==None:
				return {"result":False,"code":SiteManager.FOLDER_TOSYNC_MISSING_ERROR,"data":""}

		if data["image"]["option"]=="custom":						
			if data["image"]["path"]!=None:
				check_image=self.check_mimetypes(data["image"]["path"])
				
			else:
				return {"result":False,"code":SiteManager.IMAGE_FILE_MISSING_ERROR,"data":""}
		
		if check_image==None:
			return {"result":True,"code":SiteManager.ALL_CORRECT_CODE,"data":""}
						
		else:
			return check_image			
						
				
	
	#def check_data
	
	def check_mimetypes(self,file):

		mime = MimeTypes()
		file_mime_type= mime.guess_type(file)
		error=False
		if file_mime_type[0]!=None:
			if not 'image' in file_mime_type[0]: 
				error=True
		else:
			error=True

		if error:
			return {"result":False,"code":SiteManager.IMAGE_FORMART_ERROR,"data":""}				
		
	#def check_mimetypes			
				
	
	def get_siteId(self,name):

		siteId= ''.join((c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn'))
		siteId=siteId.lower().replace(" ","_")
		siteId=re.sub('[^\w\s-]', '', siteId).strip()
		siteId=re.sub('[-\s]+', '-', siteId)

		return siteId

	#def get_siteId


	def copy_pixbuf_file(self,pixbuf_path):
		
		result={}
		result['status']=True
		
		try:
			copy_pixbuf=self.local_client.ScpManager.send_file(self.credentials[0],self.credentials[1],self.server_ip,pixbuf_path,"/tmp/")
			return result
		except n4d.client.CallFailedError as e:
			result['status']=False
			result['msg']=e
			result['code']=SiteManager.SCP_FILE_TOSERVER_ERROR
			return result


	#def copy_pixbuf_file	

	def remove_tmp_files(self,pixbuf_path):
	
		if os.path.exists(pixbuf_path):
			os.remove(pixbuf_path)
	
	#def remove_tmp_files		

	def sync_content(self,siteId,sync_from):
		
		dest_site="easy-"+siteId
		dest_site_path=os.path.join(self.net_folder,dest_site)
		result={}
		result['status']=True

		try:
			sync_content=self.local_client.ScpManager.send_dir(self.credentials[0],self.credentials[1],"server",sync_from,dest_site_path,True)
			return result
		except n4d.client.CallFailedError as e:
			result['status']=False
			result['msg']=e
			result['code']=SiteManager.SCP_CONTENT_TOSERVER_ERROR
			return result
		
	#def sync_content

	def copy_image_file(self,siteId,copy_image):

		image_name=os.path.basename(copy_image)
		if not os.path.exists(os.path.join(self.image_dir,image_name)):
			shutil.copy(copy_image,self.image_dir)
		tmp_image="."+image_name
		dest_site="easy-"+siteId
		dest_site_path=os.path.join(self.net_folder,dest_site)
		dest_path=os.path.join(dest_site_path,tmp_image)
		try:
			ret=self.local_client.ScpManager.send_file(self.credentials[0],self.credentials[1],self.server_ip,copy_image,dest_path)
		except n4d.client.CallFailedError as e:
			pass
	
	#def copy_image_file

	def _searchMeta(self,meta):

		match=False
		for item in self.flavours:
			if meta in item:
				match=True
				break

		return match

	#def_ searchMeta


#class SiteManager

 
import os
import json
import codecs
import shutil
import xmlrpclib as n4dclient
import ssl
#from jinja2 import Environment
#from jinja2.loaders import FileSystemLoader
#from jinja2 import Template

class EasySitesManager(object):

	def __init__(self):

		self.config_dir=os.path.expanduser("/etc/easysites/")
		#self.tpl_env = Environment(loader=FileSystemLoader('/usr/share/lliurex-easy-sites/templates'))
		self.site_template="/usr/share/lliurex-www/templates/link.json"
		self.net_folder="/net/server-sync/easy-sites"
		self.var_folder="/var/www/easy-sites/"
		self.links_path="/var/lib/lliurex-www/links"
		self.icons_path="/usr/share/lliurex-www/srv/icons"
		#self.hide_folder=os.path.join(self.links_path,"hide_links")

		server='localhost'
		context=ssl._create_unverified_context()
		self.n4d = n4dclient.ServerProxy("https://"+server+":9779",context=context,allow_none=True)
		
		self._get_n4d_key()


	#def __init__	


	def _get_n4d_key(self):

		self.n4dkey=''
		with open('/etc/n4d/key') as file_data:
			self.n4dkey = file_data.readlines()[0].strip()

	#def _get_n4d_key


	def _create_dirs(self):


		if not os.path.isdir(self.net_folder):
			os.makedirs(self.net_folder)

		'''
		if not os.path.isdir(self.hide_folder):
			os.makedirs(self.hide_folder)
		'''
	#def _create_dirs			
	
	def _create_conf(self):

		var={}

		if not os.path.isdir(self.config_dir):
			os.makedirs(self.config_dir)

		
		return {"status":True,"msg":"Configuration folder created successfuly","code":"","data":""}

	#def create_conf		
	

	def read_conf(self):
		
		'''
		Result code:
			-21: Error reading configuration file
			-0: All correct 

		'''	

		self._create_dirs()	
		
		if not os.path.isdir(self.config_dir):
			self._create_conf()
	
		self.sites_config={}
		content=os.listdir(self.config_dir)
		cont_errors=0
		for element in content:
			element_path=os.path.join(self.config_dir,element)
			if os.path.isfile(element_path):
				f=open(element_path)
				try:
					content=json.load(f)
					siteId=element.split("-")[1].split(".")[0]
					self.sites_config[siteId]=content
					result=self._update_from_site_link(siteId)
					if result["status"]:
						self.sites_config[siteId]["visibility"]=result["visibility"]
						if result["url"]!="":
							self.sites_config[siteId]["url"]=result["url"]
						if "http://server/srv/" in self.sites_config[siteId]["image"]["img_path"]:
							self.sites_config[siteId]["image"]["img_path"]=self.sites_config[siteId]["image"]["img_path"].replace("http://server/srv/","http://server/easy-sites/")	
					else:
						cont_errors+=1	
					f.close()
				except:	
					cont_errors+=1
					pass	

		if cont_errors==0:
			result={"status":True,"msg":"Configurations files readed successfuly","code":0,"data":self.sites_config}
		else:				
			result={"status":False,"msg":"","code":21,"data":self.sites_config}

		return result	

	#def read_conf	

	def _update_from_site_link(self,siteId):

		site_link=os.path.join(self.links_path,"easy-"+siteId+".json")
		if os.path.exists(site_link):

			f=open(site_link)
			try:
				content=json.load(f)
				f.close()
				return {"status":True,"visibility":content["visibility"],"url":content["link"]}
			except:
				f.close()
				return {"status":False,"visibility":False,"url":""}
		else:
			return {"status":True,"visibility":False,"url":""}
	
	#def _get_site_visibility					

	def write_conf(self,info):

		new_file="easy-"+info["id"]+".json"		
		new_path=os.path.join(self.config_dir,new_file)	
		try:
			
			with codecs.open(new_path,'w',encoding="utf-8") as f:
				json.dump(info,f,ensure_ascii=False)
				f.close()
				status=True
				msg="Site config saved successfully"
				code=""
		except Exception as e:
			status=False
			msg="Unabled to saved site config: "+str(e)
			code=23

		return {"status":status,"msg":msg,"code":code}			

	#def _write_conf	


	def _delete_site_conf(self,siteId):

		conf_file="easy-"+siteId+".json"		
		conf_file_path=os.path.join(self.config_dir,conf_file)	


		try:
			if os.path.exists(conf_file_path):
				os.remove(conf_file_path)
			status=True
			msg="Conf site delete successfully"	

		except Exception as e:
			status=False
			msg="Unabled to delete site config: "+str(e)

		return {"status":status,"msg":msg}	

	#def _delete_site_conf	

	def create_new_site(self,info,pixbuf_path):

		result={'status':True,'msg':"Site created sucessfully"}
		result_create=self._create_new_site_folder(info["id"])
		error=False
		if result_create['status']:
			result_link=self._create_link_template(info)
			if result_link['status']:
				result_icon=self._create_site_icon(info["id"],pixbuf_path)
				if result_icon["status"]:
					result_symlink=self._create_symlink_folder(info["id"])
					if not result_symlink['status']:
						'''
						if not info["visibility"]:
							result_visible=self._hide_show_site(info["id"],False)
							if not result_visible['status']:
								error=True
								result=result_visible
						'''	
					#else:
						error=True
						result=result_symlink
				else:
					error=True
					result=result_icon
			else:
				error=True
				result=result_link
		else:
			error=True
			result=result_create	

		self._remove_tmp_site_backup(pixbuf_path)

		if error:
			self.delete_site(info["id"])
		else:
			result_write=self.write_conf(info)
			if result_write['status']:
				return result
			else:
				self.delete_site(info["id"])
				result=result_write
		return result
			
	
	#def create_new_site
	

	def edit_site(self,info,pixbuf_path,origId):

		'''
		Result code:
		-10: Site edit successfully
		-30: Unable to edit the site

		'''

		actions_todo=self.get_actions_todo(info,origId)
		result_backup=self._make_tmp_site_backup(origId)
		error=False
		icon_changed=False
		link_changed=False
		visible_changed=False
		rename=actions_todo		

		if result_backup['status']:
			if rename:
				result_rename=self._rename_site(info,pixbuf_path,origId)
				if not result_rename["status"]:
					error=True
					result=result_rename 
			
			else:
				if "icon" in actions_todo:
					result_icon=self._create_site_icon(info["id"],pixbuf_path,origId)	
					if not result_icon['status']:
						error=True
						result=result_icon
					else:
						icon_changed=True
				if not error:		
					if "link" in actions_todo:
						result_link=self._create_link_template(info,origId)	
						if not result_link['status']:
							self._undo_edit_changes(origId,info,rename,icon_changed,link_changed)
							error=True
							result=result_link
						else:
							link_changed=True
			if not error:	
				if "visible" in actions_todo:
					result_visible=self._hide_show_site(info["id"],info["visibility"])
					if not result_visible['status']:
						self._undo_edit_changes(origId,info,rename,icon_changed,link_changed)
						error=True
						result=result_visible
					else:
						visible_changed=True
			
			if error:
				self._remove_tmp_site_backup(pixbuf_path,True)
				return result
			else:
				result_write=self.write_conf(info)
				if result_write['status']:
					result={"status":True,"msg":"","code":10,"data":""}	
				else:
					self._undo_edit_changes(origId,info,rename,icon_changed,link_changed)
					if visible_changed:
						if info["visibility"]:
							self._hide_show_site(info["id"],False)
						else:
							self._hide_show_site(info["id"],True)	
					result=result_write
				self._remove_tmp_site_backup(pixbuf_path,True)
				return result
		else:
			self._remove_tmp_site_backup(pixbuf_path,True)
			result={"status":False,"msg":"","code":30,"data":""}				
			return result

	#def edit_site		

	def delete_site(self,siteId):

		'''
		Result code:
			-12:Unable to delete site
			-15:Site delete successfully
		'''

		try:
			link_file="easy-"+siteId+".json"
			link_file_path=os.path.join(self.links_path,link_file)
			if os.path.exists(link_file_path):
				os.remove(link_file_path)
			else:
				hide_path=os.path.join(self.hide_folder,link_file)
				if os.path.exists(hide_path):
					os.remove(hide_path)	
			
			icon_file="easy-"+siteId+".png"
			icon_file_path=os.path.join(self.icons_path,icon_file)
			if os.path.exists(icon_file_path):
				os.remove(icon_file_path)

			symlink="easy-"+siteId
			symlink_path=os.path.join(self.var_folder,symlink)		
			if os.path.exists(symlink_path):
				os.remove(symlink_path)

			site_folder="easy-"+siteId
			site_folder_path=os.path.join(self.net_folder,site_folder)	
			if os.path.exists(site_folder_path):
				shutil.rmtree(site_folder_path)

			return self._delete_site_conf(siteId)

		except Exception as e:
			result={"status":False,"msg":str(e),"code":12,"data":""}
			return result	

	#def delete_site	


	def change_site_visibility(self,info,visible):


		result=self._hide_show_site(info["id"],visible)
		if result['status']:
			info['visibility']=visible
			result_write=self.write_conf(info)
			if not result_write['status']:
				if visible:
					self._hide_show_site(info["id"],False)
				else:
					self._hide_show_site(info["id"],True)	
				result=result_write

		return result

	#def change_site_visibility		

	def _create_new_site_folder(self,siteId):

		'''		
		Result code:
			-13: Unable to sync content
		'''
		try:
			new_site="easy-"+siteId
			new_site_path=os.path.join(self.net_folder,new_site)
			
			if not os.path.isdir(new_site_path):
				os.makedirs(new_site_path)
		
			result={"status":True,"msg":"Site folder create successfully","code":"","data":""}
								
		except Exception as e:
			result={"status":False,"msg":str(e),"code":13,"data":""}

		return result	

	#_create_new_site_folder		


	def _rename_site(self,info,pixbuf_path,origId):

		error=False

		result_rename_folder=self._rename_site_folder(info["id"],origId)
		if result_rename_folder["status"]:
			result_link=self._create_link_template(info,origId)
			if result_link["status"]:
				result_icon=self._create_site_icon(info["id"],pixbuf_path,origId)
				if result_icon["status"]:
					result_symlink=self._create_symlink_folder(info["id"],origId)
					if result_symlink['status']:
						return self._delete_site_conf(origId)	
					else:
						error=True
						result=result_symlink	
				else:
					error=True
					result=result_icon
			else:
				error=True
				result=result_link
				
		else:
			return result_rename_folder

		if error:
			self._restore_site_backup(origId,info["id"])
			self._rename_site_folder(origId,info["id"])
			return result
				

	#def_rename_site


	def _rename_site_folder(self,siteId,origId):

		'''
		Result code:
			-14: Unable to rename. Old site not exists
			-15: Unable to rename. Problems in process
		'''
		orig_site=os.path.join(self.net_folder,"easy-"+origId)
		new_site=os.path.join(self.net_folder,"easy-"+siteId)

		try:
			if os.path.isdir(orig_site):
				os.rename(orig_site,new_site)
				result={"status":True,"msg":"Site rename successfully","code":"","data":""}
			else:
				result={"status":False,"msg":"","code":14,"data":""}
	
		except Exception as e:
			result={"status":False,"msg":str(e),"code":15,"data":""}
	

		return result	

	#def_rename_site_folder

	def _create_link_template(self,info,origId=None):


		'''
		Result code:
			-16:Unable to create link template
		'''
		try:
			new_site=True
			link_template=os.path.join(self.links_path,"easy-"+info["id"])+".json"
			'''		
			site_info={}
			site_info["ID"]=info["id"]
			site_info["ICON"]="easy-"+info["id"]+".png"
			site_info["NAME"]=info["name"]
			site_info["DESCR"]=info["description"]
						
			site_info["visibility"]=visible
			site_info["EDITABLE"]="false"
				
			template= self.tpl_env.get_template("custom.json")
			string_template = template.render(site_info).encode('UTF-8')
				
			if type(string_template) is not str:
				string_template=string_template.decode()

			file=open(link_template,"w")
			file.write(string_template)
			file.close()
			'''
			if origId!= None:
				current_link=os.path.join(self.links_path,"easy-"+origId)+".json"
				new_site=False
			else:
				current_link=self.site_template

			f=open(current_link)
			content=json.load(f)
			content["linkId"]=info["id"]
			content["link"]="http://server/easy-sites/"+"easy-"+info["id"]
			content["name"]["default"]=info["name"]
			content["icon"]="easy-"+info["id"]+".png"
			content["description"]["default"]=info["description"]
			content["visibility"]=info["visibility"]
			if new_site:
				content["editable"]=False
				content["order"]=666

			f.close()
			with codecs.open(link_template,'w',encoding="utf-8") as f:
				json.dump(content,f,ensure_ascii=False)
				f.close()

			cmd="chown www-data:www-data %s"%(link_template)
			os.system(cmd)
			
			if info["id"]!=origId and origId!=None:
				old_link_template=os.path.join(self.links_path,"easy-"+origId)+".json"
				if os.path.exists(old_link_template):
					os.remove(old_link_template)
					'''
					else:
						old_hide_link_template=os.path.join(self.hide_folder,"easy-"+origId)+".json"
						if os.path.exists(old_hide_link_template):
							os.remove(old_hide_link_template)	
					'''
			
			result={"status":True,"msg":"Link file create successfuly","code":"","data":""}
		
		except Exception as e:

			result={"status":False,"msg":str(e),"code":16,"data":""}

		return result
		
	#def_create_link_template	
	
	def _create_site_icon(self,siteId,pixbuf_path,origId=None):

		'''
		Result code:
			-17:Unable to create icon site
		'''


		try:
			new_icon="easy-"+siteId+".png"
			new_icon_path=os.path.join(self.icons_path,new_icon)
			
			shutil.copy2(pixbuf_path,new_icon_path)
			if origId !=None:
				if siteId!=origId:
					old_icon="easy-"+origId+".png"
					old_icon_path=os.path.join(self.icons_path,old_icon)
					if os.path.exists(old_icon_path):
						os.remove(old_icon_path)
			result={"status":True,"msg":"icon site create successfully","code":"","data":""}
		except Exception as e:
			result={"status":False,"msg":str(e),"code":17,"data":""}
	
		return result

	#def create_site_icon	

	def _create_symlink_folder(self,siteId,origId=None):


		'''
		Result code:
			-18:Unable to create symbolic link
		'''
		try:
			if siteId==origId:
				pass
			else:
				new_symlink="easy-"+siteId	
				new_symlink_path=os.path.join(self.var_folder,new_symlink)
				source_symlink_path=os.path.join(self.net_folder,new_symlink)
				os.symlink(source_symlink_path,new_symlink_path)
				if origId!=None:
					old_symlink="easy-"+origId
					old_symlink_path=os.path.join(self.var_folder,old_symlink)
					os.unlink(old_symlink_path)

			result={"status":True,"msg":"link to /net create successfully","code":"","data":""}

		except Exception as e:
			result={"status":False,"msg":str(e),"code":18,"data":""}

		return result
		
	#def _create_symlink_folder	

	def _hide_show_site(self,siteId,visible):

		'''
		Result code:
			-19:Unable to execute action
		'''
		show_site=visible
		link_site="easy-"+siteId+".json"
		#hide_site_path=os.path.join(self.hide_folder,link_site)
		link_site_path=os.path.join(self.links_path,link_site)

		try:
			
			if show_site:
				action="show"
				'''
				if os.path.exists(hide_site_path):
					shutil.move(hide_site_path,link_site_path)
				'''
			else:
				action="hide"
				'''
				if os.path.exists(link_site_path):
					shutil.move(link_site_path,hide_site_path)	
				'''
			
			f=open(link_site_path)
			content=json.load(f)
			content["visibility"]=visible
			f.close()

			with codecs.open(link_site_path,'w',encoding="utf-8") as f:
				json.dump(content,f,ensure_ascii=False)
				f.close()
			
			cmd="chown www-data:www-data %s"%(link_site_path)
			os.system(cmd)
				
			result={"status":True,"msg":"Action execute successfully: "+action,"code":"","data":""}		

		except Exception as e:
			result={"status":False,"msg":str(e),"code":19,"data":""}

		return result

	#def hide_show_site

	
	def _make_tmp_site_backup(self,origId):

		self.backup_path="/tmp/easy-site-"+origId
		self.backup_path_config="/tmp/easy-site-"+origId+"/config"

		try:
			if not os.path.exists(self.backup_path):
				os.mkdir(self.backup_path)
				os.mkdir(self.backup_path_config)

			if os.path.exists(os.path.join(self.links_path,"easy-"+origId+".json")):
				shutil.copy2(os.path.join(self.links_path,"easy-"+origId+".json"),os.path.join(self.backup_path,"easy-"+origId+".json"))
			if os.path.exists(os.path.join(self.icons_path,"easy-"+origId+".png")):		
				shutil.copy2(os.path.join(self.icons_path,"easy-"+origId+".png"),os.path.join(self.backup_path,"easy-"+origId+".png"))
			if os.path.exists(os.path.join(self.config_dir,"easy-"+origId+".json")):
				shutil.copy2(os.path.join(self.config_dir,"easy-"+origId+".json"),os.path.join(self.backup_path_config,"easy-"+origId+".jon"))

			result={"status":True,"msg":"Backup successfully","code":"","data":""}	

		except Exception as e:
			result={"status":False,"msg":str(e),"code":"",data:""}

		return result	

	#def _make_tmp_site_backup	
			
	def _remove_tmp_site_backup(self,pixbuf_path,removebackup=None):
	
		if removebackup:
			if os.path.exists(self.backup_path):
				shutil.rmtree(self.backup_path)

		if os.path.exists(pixbuf_path):
			os.remove(pixbuf_path)	

	#def _remove_tmp_site_backup					

	def _restore_site_backup(self,origId,siteId):

		if not os.path.exists(os.path.join(self.links_path,"easy-"+origId+".json")):
			shutil.copy2(os.path.join(self.backup_path,"easy-"+origId+".json"),os.path.join(self.links_path,"easy-"+origId+".json"))
			if os.path.exists(os.path.join(self.links_path,"easy-"+siteId+".json")):
				os.remove(os.path.join(self.links_path,"easy-"+siteId+".json"))


		if not os.path.exists(os.path.join(self.icons_path,"easy-"+origId+".png")):
			shutil.copy2(os.path.join(self.backup_path,"easy-"+origId+".png"),os.path.join(self.icons_path,"easy-"+origId+".png"))
			if os.path.exists(os.path.join(self.icons_path,"easy-"+siteId+".png")):
				os.remove(os.path.join(self.icons_path,"easy-"+siteId+".png"))



	#def _restore_site_backup
	
	def _undo_edit_changes(self,origId,info,rename,icon,link):
		
		if rename:
			self._restore_site_backup(origId,info["id"])
			self._rename_site_folder(origId,info["id"])
			self._create_symlink_folder(origId,info["id"])
			shutil.copy2(os.path.join(self.backup_path_config,"easy-"+origId+".jon"),os.path.join(self.config_dir,"easy-"+origId+".json"))
		if icon:
			shutil.copy2(os.path.join(self.backup_path,"easy-"+origId+".png"),os.path.join(self.icons_path,"easy-"+origId+".png"))
		if link:
			shutil.copy2(os.path.join(self.backup_path,"easy-"+origId+".json"),os.path.join(self.links_path,"easy-"+origId+".json"))
		
	
	#def _undo_edit_changes
				
	def get_actions_todo(self,info,origId):

		actions=[]
		
		icon=False
		link=False

		if info["id"]!=origId:
			actions.append("rename")

		if info["visibility"]!=self.sites_config[origId]["visibility"]:
			actions.append("visible")

		if info["name"]!=self.sites_config[origId]["name"]:
			link=True
			icon=True

		if info["description"]!=self.sites_config[origId]["description"]:
			link=True

		if info["image"]["img_path"]!=self.sites_config[origId]["image"]["img_path"]:
			icon=True

		if info["image"]["font"]!=self.sites_config[origId]["image"]["font"]:
			icon=True

		if info["image"]["color"]!=self.sites_config[origId]["image"]["color"]:
			icon=True

		if icon:
			actions.append("icon")

		if link:
			actions.append("link")	

		return actions	

	#def get_actions_todo	
#class SiteManager					
	

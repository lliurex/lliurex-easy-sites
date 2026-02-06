 
import os
import subprocess
import json
import codecs
import shutil
import n4d.responses
import configparser

class EasySitesManager:

	DELETE_SITE_ERROR=-1
	SYNC_CONTENT_ERROR=-2
	RENAME_SITE_OLD_NOT_EXISTS_ERROR=-3
	RENAME_SITE_PROBLEMS_ERROR=-4
	CREATE_SITE_ICON_ERROR=-5
	CREATE_SYMLINK_FOLDER_ERROR=-6
	READING_CONFIGURATION_FILE_ERROR=-7
	SAVING_SITE_ERROR=-8
	EDIT_SITE_ERROR=-9
	ALL_SITES_REMOVED_ERROR=-10
	ALL_SITE_SHOW_ERROR=-11
	ALL_SITE_HIDE_ERROR=-12
	MOUNT_CONTENT_ERROR=-13
	UNMOUNT_CONTENT_ERROR=-14
	AUTOMOUNT_ENABLE_ERROR=-15
	AUTOMOUNT_DISABLE_ERROR=-16
	SHOW_SITE_ERROR=-17
	HIDE_SITE_ERROR=-18

	ALL_SUCCESSFULL_CODE=0
	EDIT_SITE_SUCCESSFUL=1
	SITE_CREATED_SUCCESSFUL=2
	DELETE_SITE_SUCCESSFUL=3
	ALL_SITES_REMOVED_SUCCESSFUL=4
	ALL_SITES_SHOW_SUCCESSFUL=5
	ALL_SITES_HIDE_SUCCESSFUL=6
	SYNC_CONTENT_SUCCESSFULL=7
	MOUNT_CONTENT_SUCCESSFULL=8
	UNMOUNT_CONTENT_SUCCESSFULL=9
	AUTOMOUNT_ENABLE_SUCCESSFULL=10
	AUTOMOUNT_DISABLE_SUCCESSFULL=11
	SHOW_SITE_SUCCESSFULL=12
	HIDE_SITE_SUCCESSFULL=13

	def __init__(self):

		self.config_dir=os.path.expanduser("/etc/easysites/")
		self.net_folder="/net/server-sync/easy-sites"
		self.var_folder="/var/www/easy-sites/"
		self.icons_path="/var/www/easy-sites/icons"
		self.site_folder="/usr/share/lliurex-easy-sites/easy-sites"
		self.sites_template="/usr/share/lliurex-easy-sites/templates/sites_template.html"
		self.sites_html_template="/usr/share/lliurex-easy-sites/templates/sites.html"
		self.sites_html="/var/www/easy-sites/sites.html"
		self.systemdUnit_template="/usr/share/lliurex-easy-sites/templates/systemd_mount.template"
		self.systemdDest="/etc/systemd/system"
		self.index_mount_template="/usr/share/lliurex-easy-sites/templates/index_mount_template.html"
		
	def read_conf(self):
		
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
					f.close()
				except:	
					cont_errors+=1
					pass	

		if cont_errors==0:
			result={"status":True,"msg":"Configurations files readed successfuly","code":EasySitesManager.ALL_SUCCESSFULL_CODE,"data":self.sites_config}
		else:				
			result={"status":False,"msg":"","code":EasySitesManager.READING_CONFIGURATION_FILE_ERROR,"data":self.sites_config}

		return n4d.responses.build_successful_call_response(result)	

	#def read_conf	
	
	def write_conf(self,info):

		new_file="easy-"+info["id"]+".json"		
		new_path=os.path.join(self.config_dir,new_file)	
		try:
			
			with codecs.open(new_path,'w') as f:
				json.dump(info,f,ensure_ascii=False)
				f.close()
				status=True
				msg="Site config saved successfully"
				code=EasySitesManager.EDIT_SITE_SUCCESSFUL
		except Exception as e:
			status=False
			msg="Unabled to saved site config: "+str(e)
			code=EasySitesManager.SAVING_SITE_ERROR

		result={"status":status,"msg":msg,"code":code}
		return n4d.responses.build_successful_call_response(result)			

	#def _write_conf	

	def create_new_site(self,info,pixbuf_path):

		result_create=self._create_new_site_folder(info["id"],info["mountUnit"])
		error=False
		if result_create['status']:
			result_icon=self._create_site_icon(info["id"],pixbuf_path)
			if result_icon["status"]:
				result_symlink=self._create_symlink_folder(info["id"])
				if not result_symlink['status']:
					error=True
					result=result_symlink
			else:
				error=True
				result=result_icon
			
		else:
			error=True
			result=result_create	

		self._remove_tmp_site_backup(pixbuf_path)

		if error:
			self.delete_site(info["id"],info["systemdUnit"])
		else:
			if info["mountUnit"]:
				result=self._mount_site_content(info["sync_folder"],info["site_folder"],info["systemdUnit"],info["auto_mount"])
			else:
				result=self._sync_site_content(info["sync_folder"],info["site_folder"])

			if result["status"]:
				result=self.write_conf(info).get('return',None)
				if not result['status']:
					self.delete_site(info["id"],info["systemdUnit"])
		
		if result["status"]:
			ret=self._create_sites_html()
			result={'status':True,'msg':"Site created sucessfully","code":EasySitesManager.SITE_CREATED_SUCCESSFUL,"data":""}
		
		return n4d.responses.build_successful_call_response(result)
			
	#def create_new_site
	
	def edit_site(self,info,pixbuf_path,origId,requiredSync=False):

		actions_todo=self._get_actions_todo(info,origId,requiredSync,pixbuf_path)
		result_backup=self._make_tmp_site_backup(origId)
		error=False
		icon_changed=False
		visible_changed=False
		rename_changed=False
		tmpsystemdUnit=info["systemdUnit"]
		must_write_conf=True		

		if result_backup['status']:
			if "rename" in actions_todo:
				result_rename=self._rename_site(info,pixbuf_path,origId,requiredSync)
				if not result_rename["status"]:
					error=True
					result=result_rename 
				else:
					rename_changed=True
			else:
				if 'sync_content' in actions_todo:
					if info["mountUnit"]:
						result_sync=self._mount_site_content(info["sync_folder"],info["site_folder"],info["systemdUnit"],info["auto_mount"])
					else:
						result_sync=self._sync_site_content(info["sync_folder"],info["site_folder"])	
					if not result_sync["status"]:
						error=True
						result=result_sync
				else:
					if 'manage_auto_mount' in actions_todo:
						result_auto_mount=self.manage_auto_mount(info["systemdUnit"],info["auto_mount"]).get('return',None)
						if not result_auto_mount["status"]:
							error=True
							result=result_auto_mount

					else:
						if 'visibility' in actions_todo:
							must_write_conf=False
							result_visibility=self.change_site_visibility(info).get('return',None)
							result=result_visibility
							if not result["status"]:
								error=True
									
				if not error:
					if "site_config" in actions_todo:
						error=False
					if "icon" in actions_todo:
						result_icon=self._create_site_icon(info["id"],pixbuf_path,origId)	
						if not result_icon['status']:
							error=True
							result=result_icon
						else:
							icon_changed=True
			if error:
				self._remove_tmp_site_backup(pixbuf_path,True)
			else:
				if must_write_conf:
					result_write=self.write_conf(info).get('return',None)
					if result_write['status']:
						result={"status":True,"msg":"","code":EasySitesManager.EDIT_SITE_SUCCESSFUL,"data":""}	
					else:
						self._undo_edit_changes(origId,info,rename_changed,icon_changed,link_changed,info["systemdUnit"])
						result=result_write
		
				self._remove_tmp_site_backup(pixbuf_path,True)

		else:
			self._remove_tmp_site_backup(pixbuf_path,True)
			result={"status":False,"msg":"","code":EasySitesManager.EDIT_SITE_ERROR,"data":""}				

		if result["status"]:
			ret=self._create_sites_html()

		return n4d.responses.build_successful_call_response(result)

	#def edit_site		

	def delete_site(self,siteId,systemdUnit,createHtml=True):

		try:
			abort=False
			if systemdUnit!=None:
				ret=self._delete_systemd_unit(systemdUnit)
				abort=not ret["status"]
			if not abort:
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

				return self._delete_site_conf(siteId,createHtml)
			else:
				return n4d.responses.build_successful_call_response(ret)

		except Exception as e:
			print(str(e))
			result={"status":False,"msg":str(e),"code":EasySitesManager.DELETE_SITE_ERROR,"data":""}
			return n4d.responses.build_successful_call_response(result)

	#def delete_site	

	def change_site_visibility(self,info,createHtml=True):

		if info["visibility"]:
			code_ok=EasySitesManager.SHOW_SITE_SUCCESSFULL
			code_error=EasySitesManager.SHOW_SITE_ERROR
		else:
			code_ok=EasySitesManager.HIDE_SITE_SUCCESSFULL
			code_error=EasySitesManager.HIDE_SITE_ERROR

		result=self.write_conf(info).get('return',None)
		
		if result['status']:
			result['code']=code_ok
			if createHtml:
				ret=self._create_sites_html()
		else:
			result['code']=code_error

		return n4d.responses.build_successful_call_response(result)

	#def change_site_visibility

	def delete_all_sites(self):

		countErrors=0

		for item in self.sites_config:
			ret=self.delete_site(self.sites_config[item]["id"],self.sites_config[item]["systemdUnit"],False)
			if not ret["return"]["status"]:
				countErrors+=1

		if countErrors==0:
			result={"status":True,"msg":"All sites removed successfully","code":EasySitesManager.ALL_SITES_REMOVED_SUCCESSFUL,"data":""}
		else:
			result={"status":False,"msg":"All sites removed with errors","code":EasySitesManager.ALL_SITES_REMOVED_ERROR,"data":""}

		ret=self._create_sites_html()

		return n4d.responses.build_successful_call_response(result)

	#def delete_all_sites

	def change_all_sites_visibility(self,visible):

		countErrors=0
		
		for item in self.sites_config:
			info=self.sites_config[item]
			info['visibility']=visible
			result_write=self.write_conf(info).get('return',None)
			if not result_write['status']:
				countErrors+=1
	
		if countErrors==0:
			if visible:
				msgCode=EasySitesManager.ALL_SITES_SHOW_SUCCESSFUL
			else:
				msgCode=EasySitesManager.ALL_SITES_HIDE_SUCCESSFUL
			result={"status":True,"msg":"Changed visibilty of all sites","code":msgCode,"data":""}
		else:
			if visible:
				msgCode=EasySitesManager.ALL_SITE_SHOW_ERROR
			else:
				msgCode=EasySitesManager.ALL_SITE_HIDE_ERROR
			result={"status":False,"msg":"All sites removed with errors","code":msgCode,"data":""}

		ret=self._create_sites_html()

		return n4d.responses.build_successful_call_response(result)

	#def change_all_sites_visibility

	def sync_content(self,siteId,syncFrom):

		if self.sites_config[siteId]["mountUnit"]:
			result=self._mount_site_content(syncFrom,self.sites_config[siteId]["site_folder"],self.sites_config[siteId]["systemdUnit"],self.sites_config[siteId]["auto_mount"])
		else:
			result=self._sync_site_content(syncFrom,self.sites_config[siteId]["site_folder"])

		if syncFrom!=self.sites_config[siteId]["sync_folder"]:
			if result["status"]:
				info=self.sites_config[siteId]
				info["sync_folder"]=syncFrom
				result_write=self.write_conf(info).get("return",None)
				if not result_write["status"]:
					result=result_write

		return n4d.responses.build_successful_call_response(result)


	#def sync_content

	def manage_systemd_status(self,systemdUnit,action):

		if action=="start":
			code_ok=EasySitesManager.MOUNT_CONTENT_SUCCESSFULL
			code_error=EasySitesManager.MOUNT_CONTENT_ERROR
		else:
			code_ok=EasySitesManager.UNMOUNT_CONTENT_SUCCESSFULL
			code_error=EasySitesManager.UNMOUNT_CONTENT_ERROR
		
		if os.path.exists(os.path.join(self.systemdDest,systemdUnit)):
			tmpSystemdUnit="'%s'"%systemdUnit
			cmd="systemctl %s %s"%(action,tmpSystemdUnit)
			try:
				p=subprocess.run(cmd,shell=True,check=True)
				result={"status":True,"msg":"%s systemdUnit successfully"%action,"code":code_ok,"data":""}
			except subprocess.CalledProcessError as e:
				result={"status":False,"msg":"%s systemdUnit error:%s"%(action,str(e)),"code":code_error,"data":""}
		else:
			result={"status":False,"msg":"%s systemdUnit error: Unit not exists%s"%action,"code":code_error,"data":""}

		return n4d.responses.build_successful_call_response(result)
	
	#def manage_systemd_status

	def manage_auto_mount(self,systemdUnit,auto_mount):

		if auto_mount=="enable":
			code_ok=EasySitesManager.AUTOMOUNT_ENABLE_SUCCESSFULL
			code_error=EasySitesManager.AUTOMOUNT_ENABLE_ERROR
		else:
			code_ok=EasySitesManager.AUTOMOUNT_DISABLE_SUCCESSFULL
			code_error=EasySitesManager.AUTOMOUNT_DISABLE_ERROR

		if os.path.exists(os.path.join(self.systemdDest,systemdUnit)):
			tmpSystemdUnit="'%s'"%systemdUnit
			cmd="systemctl %s %s"%(auto_mount,tmpSystemdUnit)
			try:
				p=subprocess.run(cmd,shell=True,check=True)
				result={"status":True,"msg":"%s systemdUnit successfully"%auto_mount,"code":code_ok,"data":""}
			except subprocess.CalledProcessError as e:
				result={"status":False,"msg":"%s systemdUnit error:%s"%(auto_mount,str(e)),"code":code_error,"data":""}
		else:
			result={"status":False,"msg":"%s systemdUnit error: Unit not exits%s"%autoRunr,"code":code_error,"data":""}

		return n4d.responses.build_successful_call_response(result)

	#def manage_auto_mount

	def _create_dirs(self):

		if not os.path.isdir(self.net_folder):
			os.makedirs(self.net_folder)
			self._fix_folder_perm()

	#def _create_dirs			
	
	def _create_conf(self):

		var={}

		if not os.path.isdir(self.config_dir):
			os.makedirs(self.config_dir)

		return {"status":True,"msg":"Configuration folder created successfuly","code":"","data":""}

	#def create_conf

	def _delete_site_conf(self,siteId,createHtml=True):

		conf_file="easy-"+siteId+".json"		
		conf_file_path=os.path.join(self.config_dir,conf_file)	

		try:
			if os.path.exists(conf_file_path):
				os.remove(conf_file_path)
			status=True
			msg="Conf site delete successfully"
			code=EasySitesManager.DELETE_SITE_SUCCESSFUL	

		except Exception as e:
			status=False
			msg="Unabled to delete site config: "+str(e)
			code=EasySitesManager.DELETE_SITE_ERROR

		result={"status":status,"msg":msg,"code":code}

		if result["status"]:
			if createHtml:
				ret=self._create_sites_html()

		return n4d.responses.build_successful_call_response(result)	
	
	#def _delete_site_conf

	def _create_new_site_folder(self,siteId,mountUnit):

		try:
			new_site="easy-"+siteId
			new_site_path=os.path.join(self.net_folder,new_site)
			
			if not os.path.isdir(new_site_path):
				os.makedirs(new_site_path)

			if mountUnit:
				if os.path.exists(new_site_path):
					shutil.copy2(self.index_mount_template,os.path.join(new_site_path,"index.html"))
		
			result={"status":True,"msg":"Site folder create successfully","code":"","data":""}
								
		except Exception as e:
			result={"status":False,"msg":str(e),"code":EasySitesManager.SYNC_CONTENT_ERROR,"data":""}

		return result	

	#_create_new_site_folder		

	def _rename_site(self,info,pixbuf_path,origId,requiredSync):

		error=False
		if self.sites_config[origId]["systemdUnit"]!=None:
			result_unmount=self._delete_systemd_unit(self.sites_config[origId]["systemdUnit"])
			if not result_unmount["status"]:
				return result_unmount
			else:
				error=False
		if not error:
			result_rename_folder=self._rename_site_folder(info["id"],origId)
			if result_rename_folder["status"]:
				result_icon=self._create_site_icon(info["id"],pixbuf_path,origId)
				if result_icon["status"]:
					result_symlink=self._create_symlink_folder(info["id"],origId)
					if result_symlink['status']:
						if info["mountUnit"]:
							result_mount=self._mount_site_content(info["sync_folder"],info["site_folder"],info["systemdUnit"],info["auto_mount"])
							if not result_mount["status"]:
								error=True
								result=result_mount
						else:
							if requiredSync:
								result_sync=self._sync_site_content(info["sync_folder"],info["site_folder"])
								if not result_sync["status"]:
									error=True
									result=result_sync
						if not error:
							return self._delete_site_conf(origId).get('return',None)	
					else:
						error=True
						result=result_symlink	
				else:
					error=True
					result=result_icon
			else:
				return result_rename_folder

		if error:
			self._undo_edit_changes(origId,info["id"],True,False,False,info["systemdUnit"])
			return result
				
	#def_rename_site

	def _rename_site_folder(self,siteId,origId):

		orig_site=os.path.join(self.net_folder,"easy-"+origId)
		new_site=os.path.join(self.net_folder,"easy-"+siteId)

		try:
			if os.path.isdir(orig_site):
				os.rename(orig_site,new_site)
				result={"status":True,"msg":"Site rename successfully","code":"","data":""}
			else:
				result={"status":False,"msg":"","code":EasySitesManager.RENAME_SITE_OLD_NOT_EXISTS_ERROR,"data":""}
	
		except Exception as e:
			result={"status":False,"msg":str(e),"code":EasySitesManager.RENAME_SITE_PROBLEMS_ERROR,"data":""}

		return result	

	#def_rename_site_folder

	def _create_site_icon(self,siteId,pixbuf_path,origId=None):

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
			result={"status":False,"msg":str(e),"code":EasySitesManager.CREATE_SITE_ICON_ERROR,"data":""}
	
		return result

	#def create_site_icon	

	def _create_symlink_folder(self,siteId,origId=None):

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
			result={"status":False,"msg":str(e),"code":EasySitesManager.CREATE_SYMLINK_FOLDER_ERROR,"data":""}

		return result
		
	#def _create_symlink_folder

	def _make_tmp_site_backup(self,origId):

		self.backup_path="/tmp/easy-site-"+origId
		self.backup_path_config="/tmp/easy-site-"+origId+"/config"

		try:
			if not os.path.exists(self.backup_path):
				os.mkdir(self.backup_path)
				os.mkdir(self.backup_path_config)
			
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

		if pixbuf_path!=None:
			if os.path.exists(pixbuf_path):
				os.remove(pixbuf_path)	

	#def _remove_tmp_site_backup					

	def _restore_site_backup(self,origId,siteId):

		if not os.path.exists(os.path.join(self.icons_path,"easy-"+origId+".png")):
			shutil.copy2(os.path.join(self.backup_path,"easy-"+origId+".png"),os.path.join(self.icons_path,"easy-"+origId+".png"))
			if os.path.exists(os.path.join(self.icons_path,"easy-"+siteId+".png")):
				os.remove(os.path.join(self.icons_path,"easy-"+siteId+".png"))

	#def _restore_site_backup
	
	def _undo_edit_changes(self,origId,newId,rename,icon,link,systemdUnit=None):
		
		if rename:
			self._restore_site_backup(origId,newId)
			self._rename_site_folder(origId,newId)
			shutil.copy2(os.path.join(self.backup_path_config,"easy-"+origId+".jon"),os.path.join(self.config_dir,"easy-"+origId+".json"))
			if self.sites_config[origId]["systemdUnit"]!=None:
				self._delete_systemd_unit(systemdUnit)
				self._mount_site_content(self.sites_config[origId]["sync_folder"],self.sites_config[origId]["site_folder"],self.sites_config[origId]["systemdUnit"],self.sites_config[origId]["auto_mount"])

		if icon:
			shutil.copy2(os.path.join(self.backup_path,"easy-"+origId+".png"),os.path.join(self.icons_path,"easy-"+origId+".png"))
		if link:
			shutil.copy2(os.path.join(self.backup_path,"easy-"+origId+".json"),os.path.join(self.links_path,"easy-"+origId+".json"))
			
	#def _undo_edit_changes
				
	def _get_actions_todo(self,info,origId,requiredSync,pixbuf_path):

		actions=[]
		
		icon=False

		if info["id"]!=origId:
			actions.append("rename")
		else:
			if info["visibility"]!=self.sites_config[origId]["visibility"]:
				actions.append("visibility")
			
			if info["description"]!=self.sites_config[origId]["description"]:
				actions.append("site_config")

			if pixbuf_path != None:
				icon=True
				actions.append("icon")

			if info["sync_folder"]!=self.sites_config[origId]["sync_folder"]:
				actions.append("sync_content")
			else:
				if not info["mountUnit"] and requiredSync:
					actions.append("sync_content")
				else:
					if info["auto_mount"]!=self.sites_config[origId]["auto_mount"]:
						actions.append("manage_auto_mount")
		
		return actions	

	#def get_actions_todo

	def _create_sites_html(self):

		available_sites=os.listdir(self.config_dir)
		sites_content=""

		if len(available_sites)>0:
			for item in available_sites:
				item_path=os.path.join(self.config_dir,item)

				if os.path.isfile(item_path) and 'easy-' in item_path:
					try:
						with open(item_path,'r') as fd:
							data=json.load(fd)

						if data["visibility"]:
							sites_content+='  <a href="%s" title="%s">\n'%(data["url"],data["name"])
							sites_content+='     <div class="cardlink">\n'
							sites_content+='         <img class="cardicon" src="icons/%s" alt="">\n'%data["icon"]
							sites_content+='         <div class="cardname">%s</div>\n'%data["name"]
							sites_content+='     </div>\n'
							sites_content+='  </a>\n'
					except Exception as e:
						pass

			try:
				with open(self.sites_template,'r') as fd:
					content=fd.read()

				content=content.replace("{{SITES}}",sites_content)

				with open(self.sites_html,'w') as fd:
					fd.write(content)

				return True
			except Exception as e:
				return False
		else:
			if os.path.exists(self.sites_html):
				os.remove(self.sites_html)

			return True

	#def _create_sites_html
	
	def _fix_folder_perm(self):
		
		try:
			cmd="chown -R nobody:nogroup %s"%self.net_folder
			os.system(cmd)
			
			cmd="chmod -R 2775 %s"%self.net_folder
			os.system(cmd)
			
			acl_folders=[["-d -m","g:www-data:r-x"],["-d -m","g:sudo:rwx"],["-d -m","g:10003:rwx"],["-d -m","g:10001:rwx"],["-d -m","g:10004:---"],["-d -m","u::rwx"],["-d -m","o::---"],["-d -m","m::rwx"],["-m","g:10003:rwx"],["-m","g:10001:rwx"],["-m","g:10004:---"],["-m","g:www-data:r-x"]]
			for item in acl_folders:
				acl1=item[0].replace('-','').replace(' ','')
				acl2=item[1]
				cmd="setfacl -R%s %s %s"%(str(acl1),str(acl2),self.net_folder)
				os.system(cmd)
		
		except:
			pass
		
	#def _fix_folder_perm

	def _sync_site_content(self,syncFrom,destPath):

		try:
			shutil.copytree(syncFrom,destPath,dirs_exist_ok=True)
			result={"status":True,"msg":"Content synchronized successfully","code":EasySitesManager.SYNC_CONTENT_SUCCESSFULL,"data":""}	
		except Exception as e:
			result={"status":False,"msg":str(e),"code":EasySitesManager.SYNC_CONTENT_ERROR,"data":""}

		return result

	#def _sync_site_content

	def _mount_site_content(self,syncFrom,destPath,systemdUnit,auto_mount):

		ret=self._create_systemd_unit(syncFrom,destPath,systemdUnit)
		if ret["status"]:
			ret=self.manage_auto_mount(systemdUnit,auto_mount).get('return',None)
			if ret["status"]:
				ret=self.manage_systemd_status(systemdUnit,"start").get('return',None)

		if ret["status"]:
			result={"status":True,"msg":"Mount unit successfully","code":EasySitesManager.MOUNT_CONTENT_SUCCESSFULL,"data":""}
		else:
			result={"status":False,"msg":ret["msg"],"code":EasySitesManager.MOUNT_CONTENT_ERROR,"data":""}

		return result

	#def mount_site_content

	def _create_systemd_unit(self,syncFrom,destPath,systemdUnit):

		if systemdUnit !=None:
			tmpFile=os.path.join(self.systemdDest,systemdUnit)
			abort=False
			if os.path.exists(tmpFile):
				result=self._delete_systemd_unit(systemdUnit)
				abort=not result["status"]
			
			if not abort:
				shutil.copy(self.systemdUnit_template,tmpFile)
				configFile=configparser.ConfigParser()
				configFile.optionxform=str
				configFile.read(tmpFile)
				tmpCommand=configFile.get("Mount","What")
				tmpCommand=tmpCommand.replace("{{ORIG_FOLDER}}",syncFrom)
				configFile.set("Mount","What",tmpCommand)
				tmpCommand=configFile.get("Mount","Where")
				tmpCommand=tmpCommand.replace("{{DEST_FOLDER}}",destPath)
				configFile.set("Mount","Where",tmpCommand)
				with open(tmpFile,'w') as fd:
					configFile.write(fd)
				
				result={"status":True,"msg":"Mount unit defined successfully","code":"","data":""}	
		else:
			result={"status":False,"msg":"Unable to create mount unit","code":EasySitesManager.SYNC_CONTENT_ERROR,"data":""}
			
		return result

	#def _create_sytemd_unit

	def _delete_systemd_unit(self,systemdUnit):

		if systemdUnit!=None:
			tmpFile=os.path.join(self.systemdDest,systemdUnit)
			if os.path.exists(tmpFile):
				ret=self.manage_systemd_status(systemdUnit,"stop").get('return',None)
				if ret["status"]:
					ret=self.manage_auto_mount(systemdUnit,"disable").get('return',None)
					if ret["status"]:
						os.remove(tmpFile)
					else:
						return ret
				else:
					return ret
	
		result={"status":True,"msg":"Delete unit successfully","code":"","data":""}

		return result
	
	#def _delete_systemd_unit

#class SiteManager					
	

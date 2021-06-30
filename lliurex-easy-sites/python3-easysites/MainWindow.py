#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango, GdkPixbuf, Gdk, Gio, GObject,GLib



import signal
import os
import subprocess
import json
import sys
import time
import threading

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

from . import settings
import gettext
_ = gettext.gettext

class MainWindow:
	
	def __init__(self,sync_folder=None):

		self.core=Core.Core.get_core()
		self.config_dir=os.path.expanduser("/etc/easy-sites/")
		self.right_folder=sync_folder
		#self.core.sitesmanager.set_server(args_dic["server"])

	#def init

	
	def load_gui(self):
		
		gettext.textdomain(settings.TEXT_DOMAIN)
		builder=Gtk.Builder()
		builder.set_translation_domain(settings.TEXT_DOMAIN)
		ui_path=self.core.ui_path
		builder.add_from_file(ui_path)

		self.css_file=self.core.rsrc_dir+"easy-sites.css"
				
		self.stack_window= Gtk.Stack()
		self.stack_window.set_transition_duration(750)
		self.stack_window.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
		self.stack_window.set_margin_top(0)
		self.stack_window.set_margin_bottom(0)
		
		self.main_window=builder.get_object("main_window")
		self.main_window.set_title("Easy Sites")
		self.main_window.resize(870,755)
		self.main_box=builder.get_object("main_box")
		self.login_box=builder.get_object("login_box")
		self.login_button=builder.get_object("login_button")
		self.user_entry=builder.get_object("user_entry")
		self.password_entry=builder.get_object("password_entry")
		self.server_ip_entry=builder.get_object("server_ip_entry")
		self.login_msg_box=builder.get_object("login_msg_box")
		self.login_error_img=builder.get_object("login_error_img")
		self.login_msg_label=builder.get_object("login_msg_label")

		self.option_box=builder.get_object("options_box")
		self.image_banner=builder.get_object("image_banner")
		self.toolbar=builder.get_object("toolbar")
		self.option_separator=builder.get_object("option_separator")
		self.add_button=builder.get_object("add_button")
		self.help_button=builder.get_object("help_button")
		self.search_entry=builder.get_object("search_entry")
		self.msg_label_box=builder.get_object("msg_box")
		self.msg_error_img=builder.get_object("msg_error_img")
		self.msg_ok_img=builder.get_object("msg_ok_img")
		self.msg_label=builder.get_object("msg_label")
		
		self.edit_waiting_box=builder.get_object("edit_waiting_box")
		self.edit_spinner=builder.get_object("edit_spinner")
		self.edit_waiting_label=builder.get_object("edit_spinner_label")

		self.main_waiting_box=builder.get_object("main_waiting_box")
		self.main_spinner=builder.get_object("main_spinner")
		self.main_waiting_label=builder.get_object("main_spinner_label")
		
		'''
		self.waiting_window=builder.get_object("waiting_window")
		self.waiting_label=builder.get_object("waiting_plabel")
		self.waiting_pbar=builder.get_object("waiting_pbar")
		self.waiting_window.set_transient_for(self.main_window)
		'''
		self.stack_window.add_titled(self.edit_waiting_box,"waitingBox","Waiting Box")
		self.stack_window.add_titled(self.core.editBox, "editBox", "Edit Box")
		self.stack_window.add_titled(self.option_box,"optionBox", "Option Box")
		self.stack_window.show_all()
		self.main_box.pack_start(self.stack_window,True,True,0)

		self.stack_opt= Gtk.Stack()
		self.stack_opt.set_transition_duration(750)
		self.stack_opt.set_halign(Gtk.Align.FILL)
		self.stack_opt.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)

		
		self.stack_opt.add_titled(self.core.siteBox,"siteBox", "Site Box")
		self.stack_opt.add_titled(self.login_box,"loginBox", "Login Box")
		self.stack_opt.add_titled(self.main_waiting_box,"mainWaitingBox","Main Waiting Box")

		self.stack_opt.show_all()

		self.option_box.pack_start(self.stack_opt,True,True,5)
		
		self.set_css_info()
		self.init_threads()
		self.connect_signals()
		self.main_window.connect("key-press-event",self.on_key_press_event)
		self.toolbar.hide()
		self.option_separator.hide()
		self.search_entry.hide()
		self.main_window.show()
		self.login_error_img.hide()
		self.manage_message(True,False)		
		self.login_button.grab_focus()
		self.stack_window.set_transition_type(Gtk.StackTransitionType.NONE)
		self.stack_window.set_visible_child_name("optionBox")

		
	#def load_gui


	def init_threads(self):

		
		self.open_help_t=threading.Thread(target=self.open_help)
		self.open_help_t.daemon=True

		GObject.threads_init()

	#def init_threads	

	def set_css_info(self):
		
		self.style_provider=Gtk.CssProvider()
		f=Gio.File.new_for_path(self.css_file)
		self.style_provider.load_from_file(f)
		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),self.style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		#self.main_window.set_name("WINDOW")
		self.user_entry.set_name("CUSTOM-ENTRY")
		self.password_entry.set_name("CUSTOM-ENTRY")
		self.server_ip_entry.set_name("CUSTOM-ENTRY")
		self.search_entry.set_name("CUSTOM-ENTRY")
		self.login_msg_label.set_name("FEEDBACK_LABEL")
		self.main_waiting_label.set_name("FEEDBACK_LABEL")
		self.edit_waiting_label.set_name("FEEDBACK_LABEL")

		#self.waiting_label.set_name("WAITING_LABEL")

		self.image_banner.set_name("BANNER-BOX")

	#def set_css_info	
				
			
	def connect_signals(self):
		
		self.main_window.connect("destroy",self.quit)
		self.login_button.connect("clicked",self.login_clicked)
		self.user_entry.connect("activate",self.entries_press_event)
		self.password_entry.connect("activate",self.entries_press_event)
		self.server_ip_entry.connect("activate",self.entries_press_event)
		self.add_button.connect("clicked",self.add_site)
		self.search_entry.connect("changed",self.search_entry_changed)
		self.help_button.connect("clicked",self.help_clicked)

	#def connect_signals

	def entries_press_event(self,widget):
		
		self.login_clicked(None)
		
	#def entries_press_event
	
	
	def login_clicked(self,widget):
		
		self.login_msg_box.set_name("HIDE_BOX")
		self.login_error_img.hide()
		user=self.user_entry.get_text()
		password=self.password_entry.get_text()
		server=self.server_ip_entry.get_text()
	
		if server=="":
			server='server'
		
		self.login_msg_label.set_text(_("Validating user..."))
		self.login_msg_label.set_halign(Gtk.Align.CENTER)
		
		self.login_button.set_sensitive(False)
		self.validate_user(server,user,password)	

	#def login_clicked

	def validate_user(self,server,user,password):
		
		
		t=threading.Thread(target=self.core.sitesmanager.validate_user,args=(server,user,password,))
		t.daemon=True
		t.start()
		GLib.timeout_add(500,self.validate_user_listener,t)
		
	#def validate_user
	
	
	def validate_user_listener(self,thread):
			
		error=False
		if thread.is_alive():
			return True
				
		self.login_button.set_sensitive(True)
		if not self.core.sitesmanager.user_validated:
			error=True
			#self.login_msg_label.set_markup("<span foreground='red'>"+_("Invalid user")+"</span>")
		else:
			group_found=False
			for g in ["sudo","admins","teachers"]:
				if g in self.core.sitesmanager.user_groups:
					group_found=True
					break
					
			if group_found:
				self.login_msg_label.set_text("")
				
				self.load_info()
				#self.core.sitesmanager.cached_images()
				self.core.siteBox.draw_site(False)
				if self.read_conf['status']:
						if self.right_folder !=None:
							if os.path.isdir(self.right_folder):
								self.stack_opt.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
								self.msg_label.set_text("")
								self.core.editBox.init_form()
								self.core.editBox.render_form()
								self.core.editBox.sync_folder_dc.set_filename(self.right_folder)
								self.stack_window.set_visible_child_name("editBox")
							else:	
								self.stack_opt.set_visible_child_name("siteBox")
						else:
							self.stack_opt.set_visible_child_name("siteBox")
				else:
					self.stack_opt.set_visible_child_name("siteBox")			
		
					
			else:
				error=True
				#self.login_msg_label.set_markup("<span foreground='red'>"+_("Invalid user")+"</span>")
		
		if error:
			self.login_msg_box.set_name("ERROR_BOX")
			self.login_error_img.show()
			self.login_msg_label.set_halign(Gtk.Align.START)
			self.login_msg_label.set_text(_("Invalid user"))		
		return False
			
	#def validate_user_listener
		
				
	def on_key_press_event(self,window,event):
		
		ctrl=(event.state & Gdk.ModifierType.CONTROL_MASK)
		if ctrl and event.keyval == Gdk.KEY_f:
			self.search_entry.grab_focus()
		
	#def on_key_press_event

	def load_info(self):
	
		self.toolbar.show()
		self.option_separator.show()
		self.search_entry.show()	
		self.read_conf=self.core.sitesmanager.read_conf()
		self.sites_info=self.core.sitesmanager.sites_config.copy()
		if not self.read_conf['status']:
			self.add_button.set_sensitive(False)
			self.manage_message(False,True,self.read_conf['code'])

	#def load_info	

	def add_site(self,widget):

		self.manage_message(True,False)
		self.msg_label.set_text("")
		self.core.editBox.init_form()
		self.core.editBox.render_form()
		self.stack_window.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
		self.stack_window.set_visible_child_name("editBox")

	#def add_site	

	def search_entry_changed(self,widget):

	
		self.core.siteBox.init_sites_list() 
		self.load_info()
		self.search_list=self.sites_info.copy()
		self.msg_label.set_text("")

		search=self.search_entry.get_text().lower()
		if search=="":
			self.core.siteBox.draw_site(False)
		else:
			self.manage_message(True,False)
			for item in self.sites_info:
				name=self.sites_info[item]["name"].lower()
				if search in name:
					pass
				else:
					self.search_list.pop(item)

			if len(self.search_list)>0:
					self.core.siteBox.draw_site(True)
					
			
	#def search_entry_changed				

		
	def manage_message(self,hide,error,code=None,data=None):

		
		if hide:
			self.msg_label_box.set_name("HIDE_BOX")
			self.msg_error_img.hide()
			self.msg_ok_img.hide()
			self.msg_label.set_text(" ")
		else:
			msg=self.get_msg(code)
			if data!=None:
				msg=msg+data
			if error:
				self.msg_label_box.set_name("ERROR_BOX")
				self.msg_error_img.show()
				self.msg_ok_img.hide()
				self.msg_label.set_name("FEEDBACK_LABEL")
			else:
				self.msg_label_box.set_name("SUCCESS_BOX")
				self.msg_error_img.hide()
				self.msg_ok_img.show()
				self.msg_label.set_name("FEEDBACK_LABEL")

			self.msg_label.set_text(msg)

	#def manage_message		


	def get_msg(self,code):

		if 	code==-1:
			msg_text=_("You must indicate a name for the site")
		elif code==-2:
			msg_text=_("The name site is duplicate")
		elif code==-3:
			msg_text=_("Image file is not correct")
		elif code==-4:
			msg_text=_("You must indicate a image file")
		elif code==-5:
			msg_text=_("You must indicate a folder to sync content")
		elif code==6:
			msg_text=_("Site is now visible again")
		elif code==7:
			msg_text=_("Site has been hideen")	
		elif code==8:
			msg_text=_("The content has been synchronized successfully")
		elif code==9:
			msg_text=_("Site has been successfully deleted")
		elif code==10:
			msg_text=_("Site has been successfully edited")
		elif code==11:
			msg_text=_("Site has been successfully created")
		elif code==-12:
			msg_text=_("Unable to delete the site")	
		elif code==-13:
			msg_text=_("Unable to sync the content")	
		elif code==-14:
			msg_text=_("Unable to rename the site. Old site not exists")	
		elif code==-15:
			msg_text=_("Unable to rename the site due to problems in process")
		elif code==-16:
			msg_text=_("Unable to create the link template for the site")
		elif code==-17:
			msg_text=_("Unable to create the icon for the site")
		elif code==-18:
			msg_text=_("Unable to create the symbolic link for the site")		
		elif code==-19:
			msg_text=_("Unabled to change the visibility of the site")	
		elif code==20:
			msg_text=_("Unabled to copy the image for the site")
		elif code==-21:
			msg_text=_("Error reading configuration files of the sites")
		elif code==22:
			msg_text=_("Sync the content. Wait a moment...")
		elif code==-23:
			msg_text=_("Error writing changes in the site configuration file")
		elif code==24:
			msg_text=_("Validating the data entered...")
		elif code==25:
			msg_text=_("Deleting site. Wait a moment...")	
		elif code==26:
			msg_text=_("Executing actions to show the site. Wait a moment...")
		elif code==27:
			msg_text=_("Executin actions to hide the site. Wait a moment ...")		
		elif code==28:
			msg_text=_("Applying changes in the image. Wait a moment...")	
		elif code==29:
			msg_text=_("Saving changes. Wait a moment...")	
		elif code==-30:
			msg_text=_("Unabled to edit the site")	
			
		return msg_text

	#def get_msg

	def manage_waiting_stack(self,show,msg_code=None):

		self.stack_opt.set_transition_duration(700)
		self.stack_opt.set_transition_type(Gtk.StackTransitionType.CROSSFADE)

		if show:
			self.toolbar.set_sensitive(False)
			self.search_entry.set_sensitive(False)
			self.main_waiting_label.set_text(self.get_msg(msg_code))
			self.main_spinner.start()
			self.stack_opt.set_visible_child_name("mainWaitingBox")
		else:
			self.toolbar.set_sensitive(True)
			self.search_entry.set_sensitive(True)
			self.main_spinner.stop()
			self.stack_opt.set_visible_child_name("siteBox")
	
	#def manage_waiting_stack

	def help_clicked(self,widget):

		lang=os.environ["LANG"]

		if 'ca_ES' in lang:
			self.help_cmd='xdg-open https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Easy+Sites.'
		else:
			self.help_cmd='xdg-open https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Easy-Sites'

		self.init_threads()
		self.open_help_t.start()

	#def help_clicked	

	def open_help(self):

		os.system(self.help_cmd)

	#def open_help	
	
	
	def quit(self,widget):

		Gtk.main_quit()	

	#def quit	

	def start_gui(self):
		
		GObject.threads_init()
		Gtk.main()
		
	#def start_gui


	
#class MainWindow

from . import Core

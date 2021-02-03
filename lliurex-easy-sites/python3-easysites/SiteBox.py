#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango, GdkPixbuf, Gdk, Gio, GObject,GLib

import sys
import os

from . import settings
import gettext
import threading
import datetime
from . import Screenshot

gettext.textdomain(settings.TEXT_DOMAIN)
_ = gettext.gettext


class SiteBox(Gtk.VBox):

	SYNC_CONTENT_WAITING_CODE=22
	DELETING_SITE_WAITING_CODE=25
	ACTIONS_SHOW_SITE_WAITING_CODE=26
	ACTIONS_HIDE_SITE_WATIING_CODE=27

	def __init__(self):
		
		Gtk.VBox.__init__(self)
		
		self.core=Core.Core.get_core()
		
		builder=Gtk.Builder()
		builder.set_translation_domain(settings.TEXT_DOMAIN)
		ui_path=self.core.ui_path
		builder.add_from_file(ui_path)

		self.css_file=self.core.rsrc_dir+"easy-sites.css"
		self.manage_site_image=self.core.rsrc_dir+"manage_site.svg"
		self.image_nodisp=self.core.rsrc_dir+"no_disp.png"
		self.main_box=builder.get_object("sites_data_box")
		self.sites_box=builder.get_object("sites_box")
		self.scrolledwindow=builder.get_object("scrolledwindow")
		self.sites_list_box=builder.get_object("sites_list_box")
		self.sites_list_vp=builder.get_object("sites_list_viewport")
		self.pack_start(self.main_box,True,True,0)
		self.set_css_info()
		self.init_threads()
				
	#def __init__

	def set_css_info(self):
		
		self.style_provider=Gtk.CssProvider()

		f=Gio.File.new_for_path(self.css_file)
		self.style_provider.load_from_file(f)

		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),self.style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
				
	#def set_css_info	

	def init_threads(self):

		self.sync_folder_t=threading.Thread(target=self.sync_folder)
		self.open_site_browser_t=threading.Thread(target=self.open_site_browser)
		self.open_folder_t=threading.Thread(target=self.open_site_folder)
		self.delete_folder_t=threading.Thread(target=self.delete_site)
		self.manage_visibility_t=threading.Thread(target=self.manage_visibility)
		self.sync_folder_t.daemon=True
		self.open_site_browser_t.daemon=True
		self.open_folder_t.daemon=True
		self.delete_folder_t.daemon=True
		self.manage_visibility_t.daemon=True

		GObject.threads_init()	

	#def init_threads		
			
	def init_sites_list(self):
	
		tmp=self.core.siteBox.sites_list_box.get_children()
		for item in tmp:
			self.sites_list_box.remove(item)

	#def init_sites_list
			

	def draw_site(self,search,args=None):

		self.init_sites_list()
		self.search_box=search
		if not self.search_box:
			self.sites_list=self.core.mainWindow.sites_info 
			
		else:
			self.sites_list=self.core.mainWindow.search_list

		cont=len(self.sites_list)
		for item in self.sites_list:
			self.new_site_box(item,cont)
			cont-=1
		
	#def draw_site		

	def new_site_box(self,siteId,cont,args=None):

		hbox=Gtk.HBox()
		
		image=Gtk.HBox()
		custom=False
		if self.sites_list[siteId]["image"]["option"]=="custom":
			image_name=self.sites_list[siteId]["image"]["img_path"].split("/.")[1]
			#image_path=os.path.join(self.core.image_dir,image_name)
			image_path=self.sites_list[siteId]["image"]["img_path"]
			custom=True
		else:
			image_path=self.sites_list[siteId]["image"]["img_path"]
			image_name=os.path.basename(image_path)	
			
		image_info={}
		image_info["x"]=110
		image_info["y"]=110
		image_info["image_id"]=image_name
		image_info["image_url"]=image_path
		image_info["image_path"]=image_path
		image_info["aspect_ratio"]=False

		ss=Screenshot.ScreenshotNeo()
		if custom:
			ss.download_image(image_info)
		else:
			ss.set_from_file(image_info)
		
		image.set_margin_left(15)
		image.set_margin_bottom(15)
		image.set_halign(Gtk.Align.CENTER)
		image.set_valign(Gtk.Align.CENTER)
		image.id=siteId
		image.pack_start(ss,True,True,5)
		
		vbox_site=Gtk.VBox()
		hbox_site_data=Gtk.HBox()
		hbox_site_description=Gtk.VBox()
		site_name=Gtk.Label()
		site_name.set_text(self.sites_list[siteId]["name"])
		site_name.set_margin_left(10)
		site_name.set_margin_right(5)
		site_name.set_margin_top(25)
		site_name.set_margin_bottom(1)
		site_name.set_width_chars(15)
		site_name.set_max_width_chars(15)
		site_name.set_xalign(-1)
		site_name.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
		site_name.set_name("SITE_NAME")
		site_name.set_valign(Gtk.Align.START)

		hbox_site_author=Gtk.HBox()
		site_author=Gtk.Label()
		author=self.sites_list[siteId]["author"]
		site_author.set_text(_("Created by: ")+author)
		site_author.set_margin_left(10)
		site_author.set_margin_right(0)
		site_author.set_margin_bottom(15)
		site_author.set_width_chars(22)
		site_author.set_max_width_chars(22)
		site_author.set_xalign(-1)
		site_author.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
		site_author.set_name("SITE_AUTHOR")
		site_author.set_valign(Gtk.Align.START)

		site_updatedby=Gtk.Label()
		updatedby=self.sites_list[siteId]["updated_by"]
		site_updatedby.set_text(_("Updated by: ")+updatedby)
		site_updatedby.set_margin_left(8)
		site_updatedby.set_margin_right(5)
		site_updatedby.set_margin_bottom(15)
		site_updatedby.set_width_chars(25)
		site_updatedby.set_max_width_chars(25)
		site_updatedby.set_xalign(-1)
		site_updatedby.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
		site_updatedby.set_name("SITE_AUTHOR")
		site_updatedby.set_valign(Gtk.Align.END)

		hbox_site_author.pack_start(site_author,False,False,1)
		hbox_site_author.pack_end(site_updatedby,False,False,1)

		hbox_site_description.pack_start(site_name,False,False,10)
		hbox_site_description.pack_start(hbox_site_author,False,False,1)
		
		manage_site=Gtk.Button()
		manage_site_image=Gtk.Image.new_from_file(self.manage_site_image)
		manage_site.add(manage_site_image)
		manage_site.set_margin_top(25)
		manage_site.set_margin_right(15)
		manage_site.set_halign(Gtk.Align.CENTER)
		manage_site.set_valign(Gtk.Align.CENTER)
		manage_site.set_name("EDIT_ITEM_BUTTON")
		manage_site.connect("clicked",self.manage_site_options,hbox)
		manage_site.set_tooltip_text(_("Manage site"))

		popover = Gtk.Popover()
		manage_site.popover=popover
		vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		
		browser_box=Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		browser_box.set_margin_left(10)
		browser_box.set_margin_right(10)
		browser_eb=Gtk.EventBox()
		browser_eb.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK)
		browser_eb.connect("button-press-event", self.open_site,hbox)
		browser_eb.connect("motion-notify-event", self.mouse_over_popover)
		browser_eb.connect("leave-notify-event", self.mouse_exit_popover)
		browser_label=Gtk.Label()
		browser_label.set_text(_("Open site in browser"))
		browser_eb.add(browser_label)
		browser_eb.set_name("POPOVER_OFF")
		browser_box.add(browser_eb)

		folder_box=Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		folder_box.set_margin_left(10)
		folder_box.set_margin_right(10)
		folder_eb=Gtk.EventBox()
		folder_eb.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK)
		folder_eb.connect("button-press-event", self.open_folder,hbox)
		folder_eb.connect("motion-notify-event", self.mouse_over_popover)
		folder_eb.connect("leave-notify-event", self.mouse_exit_popover)
		folder_label=Gtk.Label()
		folder_label.set_text(_("Open folder"))
		folder_eb.add(folder_label)
		folder_eb.set_name("POPOVER_OFF")
		folder_box.add(folder_eb)

		sync_box=Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		sync_box.set_margin_left(10)
		sync_box.set_margin_right(10)
		sync_eb=Gtk.EventBox()
		sync_eb.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK)
		sync_eb.connect("button-press-event", self.sync_site_clicked,hbox)
		sync_eb.connect("motion-notify-event", self.mouse_over_popover)
		sync_eb.connect("leave-notify-event", self.mouse_exit_popover)
		sync_label=Gtk.Label()
		sync_label.set_text(_("Sync new content"))
		sync_eb.add(sync_label)
		sync_eb.set_name("POPOVER_OFF")
		sync_box.add(sync_eb)

		edit_box=Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		edit_box.set_margin_left(10)
		edit_box.set_margin_right(10)
		edit_eb=Gtk.EventBox()
		edit_eb.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK)
		edit_eb.connect("button-press-event", self.edit_site_clicked,hbox)
		edit_eb.connect("motion-notify-event", self.mouse_over_popover)
		edit_eb.connect("leave-notify-event", self.mouse_exit_popover)
		edit_label=Gtk.Label()
		edit_label.set_text(_("Edit site"))
		edit_eb.add(edit_label)
		edit_eb.set_name("POPOVER_OFF")
		edit_box.add(edit_eb)
		
		delete_box=Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		delete_box.set_margin_left(10)
		delete_box.set_margin_right(10)
		delete_eb=Gtk.EventBox()
		delete_eb.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK)
		delete_eb.connect("button-press-event", self.delete_site_clicked,hbox)
		delete_eb.connect("motion-notify-event", self.mouse_over_popover)
		delete_eb.connect("leave-notify-event", self.mouse_exit_popover)
		delete_label=Gtk.Label()
		delete_label.set_text(_("Delete site"))
		delete_eb.add(delete_label)
		delete_eb.set_name("POPOVER_OFF")
		delete_box.add(delete_eb)

		vbox.pack_start(browser_box, True, True,8)
		vbox.pack_start(folder_box,True,True,8)
		vbox.pack_start(sync_box, True, True,8)
		vbox.pack_start(edit_box, True, True,8)
		vbox.pack_start(delete_box,True,True,8)
		
		vbox.show_all()
		if 'client' in self.core.sitesmanager.flavours:
			folder_box.hide()

		popover.add(vbox)
		popover.set_position(Gtk.PositionType.BOTTOM)
		popover.set_relative_to(manage_site)


		switch_button=Gtk.Switch()
		switch_button.set_halign(Gtk.Align.CENTER)
		switch_button.set_valign(Gtk.Align.CENTER)
		switch_button.set_margin_top(25)
		

		if self.sites_list[siteId]["visibility"]:
			switch_button.set_active(True)
			switch_button.set_tooltip_text(_("Click to hide the site in the server main page"))
		else:
			switch_button.set_active(False)
			switch_button.set_tooltip_text(_("Click to show the site in the server main page"))

		
		switch_button.connect("notify::active",self.on_switch_activaded,hbox)
		hbox_site_data.pack_start(hbox_site_description,False,False,5)
		hbox_site_data.pack_end(manage_site,False,False,5)
		hbox_site_data.pack_end(switch_button,False,False,5)

		site_separator=Gtk.Separator()
		site_separator.set_margin_top(15)
		site_separator.set_margin_left(10)
		site_separator.set_margin_right(15)
		if cont!=1:
			site_separator.set_name("SEPARATOR")
		else:
			site_separator.set_name("WHITE_SEPARATOR")	

		vbox_site.pack_start(hbox_site_data,False,False,5)
		vbox_site.pack_end(site_separator,False,False,5)

		hbox.pack_start(image,False,False,5)
		hbox.pack_start(vbox_site,True,True,5)
		hbox.show_all()
		hbox.set_halign(Gtk.Align.FILL)

		self.sites_list_box.pack_start(hbox,False,False,1)
		self.sites_list_box.queue_draw()
		self.sites_list_box.set_valign(Gtk.Align.FILL)
		hbox.queue_draw()	

	#def new_site_box	
		
	def on_switch_activaded (self,switch,gparam,hbox):

		self.core.mainWindow.msg_label.set_text("")
		site_to_edit=hbox		
		siteId=site_to_edit.get_children()[0].id
		turn_on=False

		if switch.get_active():
			turn_on=True
			msg_switch=self.core.mainWindow.get_msg(SiteBox.ACTIONS_SHOW_SITE_WAITING_CODE)
			visible=True
			
		else:
			msg_switch=self.core.mainWindow.get_msg(SiteBox.ACTIONS_HIDE_SITE_WATIING_CODE)
			visible=False

		self.args_visibility=["visibility",self.sites_list[siteId],visible]
		self.core.mainWindow.waiting_label.set_text(msg_switch)			
		self.core.mainWindow.waiting_window.show_all()
		self.init_threads()
		self.manage_visibility_t.start()
		GLib.timeout_add(100,self.pulsate_manage_visibiliy,turn_on,siteId,hbox)
			

	#def on_switch_activaded

	def pulsate_manage_visibiliy(self,turn_on,siteId,hbox):

		if self.manage_visibility_t.is_alive():
			self.core.mainWindow.waiting_pbar.pulse()
			return True

		else:
			self.core.mainWindow.waiting_window.hide()
			if self.result_visibiliy['status']:
				self.core.mainWindow.sites_info[siteId]["visible"]=turn_on
				self.sites_list[siteId]["visibility"]=turn_on
				self.core.sitesmanager.read_conf()
				if turn_on:
					hbox.get_children()[1].get_children()[0].get_children()[1].set_tooltip_text(_("Click to hide the site in the server main page"))
					self.core.mainWindow.manage_message(False,6)
				else:
					hbox.get_children()[1].get_children()[0].get_children()[1].set_tooltip_text(_("Click to show the site in the server main page"))
					self.core.mainWindow.manage_message(False,7)
			else:
				self.core.mainWindow.manage_message(True,self.result_visibiliy['code'])	

	#def pulsate_manage_visibiliy
	
	def	manage_visibility(self):

		self.result_visibiliy=self.core.sitesmanager.save_conf(self.args_visibility)

	#def manage_visibility			


	def sync_site_clicked(self,widget,event,hbox):

		self.core.mainWindow.msg_label.set_text("")
		popover=hbox.get_children()[1].get_children()[0].get_children()[2].popover.hide()
		site_to_edit=hbox		
		siteId=site_to_edit.get_children()[0].id
		sync=False	

		dialog = Gtk.FileChooserDialog(_("Please choose a folder to sync content"), None,
			Gtk.FileChooserAction.SELECT_FOLDER,(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
			Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			folder_to_sync=dialog.get_filename()
			sync=True
		dialog.destroy()

		if sync:
			now = datetime.datetime.now()
			updated_by=self.core.sitesmanager.validation[0]
			last_updated=now.strftime("%Y-%m-%d %H:%M")
			self.args_sync=["sync",self.sites_list[siteId],folder_to_sync,updated_by,last_updated]
			self.core.mainWindow.waiting_label.set_text(self.core.mainWindow.get_msg(SiteBox.SYNC_CONTENT_WAITING_CODE))			
			self.core.mainWindow.waiting_window.show_all()
			self.init_threads()
			self.sync_folder_t.start()
			GLib.timeout_add(100,self.pulsate_sync_folder)

	#def sync_site_clicked
	
	def pulsate_sync_folder(self):

		if self.sync_folder_t.is_alive():
			self.core.mainWindow.waiting_pbar.pulse()
			return True

		else:
			self.core.mainWindow.waiting_window.hide()
			if self.result_sync['status']:
				self.core.mainWindow.sites_info[self.args_sync[1]["id"]]["sync_folder"]=self.args_sync[2]
				self.core.mainWindow.sites_info[self.args_sync[1]["id"]]["updated_by"]=self.args_sync[3]
				self.core.mainWindow.sites_info[self.args_sync[1]["id"]]["last_updated"]=self.args_sync[4]
				self.sites_list[self.args_sync[1]["id"]]["sync_folder"]=self.args_sync[2]
				self.sites_list[self.args_sync[1]["id"]]["updated_by"]=self.args_sync[3]
				self.sites_list[self.args_sync[1]["id"]]["last_updated"]=self.args_sync[4]
				self.core.sitesmanager.read_conf()
				self.core.mainWindow.manage_message(False,8)
			else:
				self.core.mainWindow.manage_message(True,self.result_sync['code'])	


	#def pulsate_sync_folder
	

	def sync_folder(self):

		self.result_sync=self.core.sitesmanager.save_conf(self.args_sync)

	#def sync_folder

	def open_site(self,widget,event,hbox):

		popover=hbox.get_children()[1].get_children()[0].get_children()[2].popover.hide()
		site_to_edit=hbox		
		siteId=site_to_edit.get_children()[0].id

		url=self.sites_list[siteId]["url"]

		self.fcmd='xdg-open '+url
		self.init_threads()
		self.open_site_browser_t.start()

	#def open_site	

	def open_site_browser(self):	

		os.system(self.fcmd)

	#def open_site_browser	

	def open_folder(self,widget,event,hbox):	

		popover=hbox.get_children()[1].get_children()[0].get_children()[2].popover.hide()
		site_to_edit=hbox		
		siteId=site_to_edit.get_children()[0].id

		folder=self.sites_list[siteId]["site_folder"]
		self.dcmd='xdg-open '+ folder
		self.init_threads()
		self.open_folder_t.start()

	#def open_folder
	
	def open_site_folder(self):

		os.system(self.dcmd) 

	#def open_site_folder 		

	def edit_site_clicked(self,widget,event,hbox):

		self.core.mainWindow.msg_label.set_text("")
		popover=hbox.get_children()[1].get_children()[0].get_children()[2].popover.hide()
		site_to_edit=hbox		
		site_to_edit=site_to_edit.get_children()[0].id
		self.core.editBox.init_form()
		self.core.editBox.render_form()
		self.core.editBox.load_values(site_to_edit)
		self.core.mainWindow.stack_window.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
		self.core.mainWindow.stack_window.set_visible_child_name("editBox")		

	#def edit_site_clicked		

	def delete_site_clicked(self,widget,event,hbox):

		self.core.mainWindow.msg_label.set_text("")
		popover=hbox.get_children()[1].get_children()[0].get_children()[2].popover.hide()
		dialog = Gtk.MessageDialog(None,0,Gtk.MessageType.WARNING, Gtk.ButtonsType.YES_NO, "EASY SITE")
		dialog.format_secondary_text(_("Do you want delete the site?"))
		response=dialog.run()
		dialog.destroy()
		
		if response==Gtk.ResponseType.YES:
			site_to_remove=hbox.get_children()[0].id
			self.args_delete=["delete",site_to_remove]
			self.core.mainWindow.waiting_label.set_text(self.core.mainWindow.get_msg(SiteBox.DELETING_SITE_WAITING_CODE))			
			self.core.mainWindow.waiting_window.show_all()
			self.init_threads()
			self.delete_folder_t.start()
			GLib.timeout_add(100,self.pulsate_delete_site,hbox)

	#def delete_site_clicked
	
	def pulsate_delete_site(self,hbox):	

		if self.delete_folder_t.is_alive():
			self.core.mainWindow.waiting_pbar.pulse()
			return True

		else:
			self.core.mainWindow.waiting_window.hide()
			if self.result_delete['status']:
				self.sites_list_box.remove(hbox)
				self.core.mainWindow.sites_info.pop(self.args_delete[1])
				self.core.sitesmanager.read_conf()
				self.core.mainWindow.manage_message(False,9)
			else:
				self.core.mainWindow.manage_message(True,self.result_delete['code'])	


	#def pulsate_delete_site
	

	def delete_site(self):

		self.result_delete=self.core.sitesmanager.save_conf(self.args_delete)

	#def delete_site			

		
	def manage_sites_buttons(self,sensitive):
	
		for item in self.sites_list_box:
			item.get_children()[1].get_children()[0].get_children()[2].set_sensitive(sensitive)
			item.get_children()[1].get_children()[0].get_children()[1].set_sensitive(sensitive)

	#def manage_sites_buttons
	
	def manage_site_options(self,button,hbox,event=None):
	
		button.popover.show()

	#def manage_site_options	

	def mouse_over_popover(self,widget,event=None):

		widget.set_name("POPOVER_ON")

	#def mouser_over_popover	

	def mouse_exit_popover(self,widget,event=None):

		widget.set_name("POPOVER_OFF")		
	

#class SiteBox

from . import Core
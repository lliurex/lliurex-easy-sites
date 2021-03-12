#!/usr/bin/env python3


import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Pango', '1.0')
gi.require_version('PangoCairo', '1.0')

from gi.repository import Gtk, Pango,PangoCairo,GdkPixbuf, Gdk, Gio, GObject,GLib


from . import settings
import gettext
#gettext.textdomain(settings.TEXT_DOMAIN)
_ = gettext.gettext

import os
import json
import codecs
import io
import glob
import cairo
import threading
import datetime


class EditBox(Gtk.VBox):

	VALIDATION_DATA_WAITING_CODE=24
	SAVIG_CHANGES_WAITING_CODE=29
	APPLYNG_CHANGES_TOIMAGE_WAITING_CODE=28
	
	def __init__(self):
		
		Gtk.VBox.__init__(self)
		
		self.core=Core.Core.get_core()
	
	#def __init__	
		
	def init_form(self):

		try:
			self.editBox.remove(self.editBox.main_box)
		except:
			pass

	#def init_form		

	def render_form(self):	

		builder=Gtk.Builder()
		builder.set_translation_domain(settings.TEXT_DOMAIN)

		ui_path=self.core.ui_path
		builder.add_from_file(ui_path)

		self.css_file=self.core.rsrc_dir+"easy-sites.css"
		self.main_box=builder.get_object("sites_edit_box")
		self.header_label=builder.get_object("header_label")
		self.header_separator=builder.get_object("header_separator")

		site_name_label=builder.get_object("site_name_label")
		self.site_name_entry=builder.get_object("site_name_entry")
		site_description_label=builder.get_object("site_description_label")
		self.site_description_entry=builder.get_object("site_description_entry")
		site_sync_label=builder.get_object("site_sync_label")
		self.sync_folder_dc=builder.get_object("sync_folder_chosser")
		label=self.sync_folder_dc.get_children()[0].get_children()[0].get_children()[1]
		label.set_max_width_chars(30)
		label.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
		site_visible_label=builder.get_object("site_visible_label")
		self.site_visible_checkbt=builder.get_object("site_visible_check")
		self.content_separator=builder.get_object("content_separator")

		image_info_label=builder.get_object("image_info_label")
		self.image_popover=builder.get_object("image_popover")
		self.image_popover_msg=builder.get_object("image_popover_msg")
		self.image_popover_cancel_bt=builder.get_object("image_popover_cancel_bt")
		self.image_popover_apply_bt=builder.get_object("image_popover_apply_bt")
		self.stock_rb=builder.get_object("stock_radiobutton")
		self.custom_rb=builder.get_object("custom_radiobutton")
		self.image_fc=builder.get_object("image_filechosser")
		label=self.image_fc.get_children()[0].get_children()[0].get_children()[1]
		label.set_max_width_chars(30)
		label.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
		self.image_box=builder.get_object("image_box")
		self.image_eb=builder.get_object("image_eb")
		self.image_da=builder.get_object("image_da")

		img_font_label=builder.get_object("img_font_label")
		self.img_font_chosser=builder.get_object("img_font_chosser")
		img_font_color_label=builder.get_object("img_font_color_label")
		self.img_font_color_chosser=builder.get_object("img_font_color_chosser")
		
		self.edit_msg_label=builder.get_object("edit_msg_label")
		self.apply_btn=builder.get_object("apply_btn")
		self.cancel_btn=builder.get_object("cancel_btn")
	
		self.label_list=[site_name_label,site_description_label,site_sync_label,site_visible_label,image_info_label,img_font_label,img_font_color_label,self.custom_rb,self.stock_rb]
		self.edit=False
		self.header_label.set_text(_("New site"))
		self.origId=None
		self.require_sync=False
		self.waiting_draw=False
		self.custom_image=self.core.custom_image
		self.nodisp_image=self.core.nodisp_image
		self.pack_start(self.main_box,True,True,0)
		self.set_css_info()
		self.connect_signals()
		self.init_data_form()
				
	#def render_form_

	def set_css_info(self):
		
		self.style_provider=Gtk.CssProvider()

		f=Gio.File.new_for_path(self.css_file)
		self.style_provider.load_from_file(f)

		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),self.style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

		self.site_name_entry.set_name("CUSTOM-ENTRY")
		self.site_description_entry.set_name("CUSTOM-ENTRY")

		for item in self.label_list:
			item.set_name("OPTION_LABEL")

		self.header_separator.set_name("SEPARATOR")
		self.content_separator.set_name("CONTENT-SEPARATOR")
		self.header_label.set_name("HEADER-LABEL")	


	#def set_css_info

	def connect_signals(self):

		
		self.site_name_entry.connect("changed",self.detect_changes)
		self.site_visible_checkbt.connect("toggled",self.change_checkbt_tooltip,"1")
		self.stock_rb.connect("toggled",self.image_toggled_button,"stock")
		self.custom_rb.connect("toggled",self.image_toggled_button,"custom")
		self.image_fc.connect("file-set",self.check_mimetype_image)
		self.sync_folder_dc.connect("file-set",self.change_sync)

		self.image_eb.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK)
		self.image_eb.connect("button-press-event", self.edit_image_clicked)
		self.image_eb.connect("motion-notify-event", self.mouse_over_image)
		self.image_eb.connect("leave-notify-event", self.mouse_exit_image)
		self.image_popover_cancel_bt.connect("clicked",self.image_popover_cancel_bt_clicked)
		self.image_popover_apply_bt.connect("clicked",self.image_popover_apply_bt_clicked)
		self.image_popover.connect("closed",self.image_popover_closed)

		self.img_font_chosser.connect("font-set",self.update_banner)
		self.img_font_color_chosser.connect("color-set",self.update_banner)

		self.apply_btn.connect("clicked",self.gather_values)
		self.cancel_btn.connect("clicked",self.cancel_clicked)
		
	#def connect_signals	

	def init_threads(self):

		self.checking_data_t=threading.Thread(target=self.checking_data)
		self.saving_data_t=threading.Thread(target=self.saving_data)
		self.checking_data_t.daemon=True
		self.saving_data_t.daemon=True

		GObject.threads_init()
		
	#def init_threads	

	def init_data_form(self):

		self.image_op="stock"
		self.image_da.show()
		self.image_da.connect("draw",self.drawing_banner_event)
		self.image_fc.set_sensitive(False)
		color=Gdk.RGBA()
		color.red=0.000000
		color.green=0.000000
		color.blue=0.000000
		color.alpha=1.000000
		self.img_font_color_chosser.set_rgba(color)
		self.init_threads()

	#def init_data_form	


	def image_toggled_button(self,button,name):

		if button.get_active():
			if name=="stock":
				self.image_fc.set_sensitive(False)
				self.image_popover_apply_bt.set_sensitive(True)
				self.image_op="stock"

			else:
				self.image_fc.set_sensitive(True)	
				self.image_popover_apply_bt.set_sensitive(False)

				self.image_op="custom"

	#def image_toggled_button			

	def load_values(self,site):
	
		self.header_label.set_text(_("Edit site"))
		site_to_edit=self.core.mainWindow.sites_info[site]

		self.site_name_entry.set_text(site_to_edit["name"])
		self.site_description_entry.set_text(site_to_edit["description"])

		self.site_visible_checkbt.set_active(site_to_edit["visibility"])

		self.image_op=site_to_edit["image"]["option"]

		if self.image_op=="stock":
			self.stock_rb.set_active(True)
			img_name=os.path.basename(site_to_edit["image"]["img_path"])
		else:
			self.custom_rb.set_active(True)
			img_name=site_to_edit["image"]["img_path"].split("/.")[1]
			img_path=os.path.join(self.core.image_dir,img_name)
			if os.path.exists(img_path):
				self.image_fc.set_filename(img_path)

		self.image_da.show()
		self.image_da.connect("draw",self.drawing_banner_event)
		self.img_font_chosser.set_font(site_to_edit["image"]["font"])
		color=Gdk.RGBA()
		color.red=site_to_edit["image"]["color"][0]
		color.green=site_to_edit["image"]["color"][1]
		color.blue=site_to_edit["image"]["color"][2]
		color.alpha=site_to_edit["image"]["color"][3]
		self.img_font_color_chosser.set_rgba(color)

		self.edit=True
		self.origId=site
		self.author=site_to_edit["author"]
		self.date_creation=site_to_edit["date_creation"]
		self.orig_sync_folder=site_to_edit["sync_folder"]
		self.orig_image=img_name
		

	#def load_values	


	def drawing_banner_event(self,widget,ctx):
		
		if self.image_op=="stock":
			path=self.custom_image
		else:
			path=self.image_fc.get_filename()

		pixbuf,no_disp=self.format_image_size(path)
		img = Gdk.cairo_surface_create_from_pixbuf(pixbuf,0)
		font_size=10

		ctx.set_source_surface(img,0,0)
		ctx.paint()
		'''
		if not no_disp:
			color=self.get_color_rgba()
			font=Pango.font_description_from_string(self.img_font_chosser.get_font())
			font_size=font.get_size()
			pctx = PangoCairo.create_layout(ctx)
			pctx.set_font_description(font)
			pctx.set_alignment(Pango.Alignment.CENTER)
			pctx.set_justify(True)
			pctx.set_width(110000)
			pctx.set_height(1000)
			if font_size>10:
				font_size=font_size/1000
			else:
				font_size=font_size/100

			#ctx.select_font_face("Courier New",cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_BOLD)
			#ctx.set_font_description(Pango.font_description_from_string('Courier New Italic'))
			#ctx.set_font_size(24)
			ctx.set_source_rgba(color[0],color[1],color[2],color[3])
			text=self.site_name_entry.get_text()
			width=ctx.text_extents(text).width
			text_x,text_y=pctx.get_pixel_size()
			#ctx.move_to(0,65-font_size)
			ctx.move_to(text_x/2,110/2-text_y/2)
			pctx.set_text(text,-1)
			PangoCairo.show_layout(ctx,pctx)
			#ctx.show_text(text)
			#ctx.stroke()
		'''	
		
	#def drawing_event

	def format_image_size(self,path):

		image=Gtk.Image()
		no_disp=False
		if path==None:
			path=self.nodisp_image
			no_disp=True
		image.set_from_file(path)
		pixbuf=image.get_pixbuf()
		pixbuf=pixbuf.scale_simple(110,110,GdkPixbuf.InterpType.BILINEAR)
		
		return pixbuf,no_disp

	#def format_image_size	
	
	def gather_values(self,widget):

		self.edit_msg_label.set_text("")
		self.data_tocheck={}
		self.data_tocheck["id"]=self.core.sitesmanager.get_siteId(self.site_name_entry.get_text())
		self.data_tocheck["name"]=self.site_name_entry.get_text()
		self.data_tocheck["description"]=self.site_description_entry.get_text()
		self.data_tocheck["sync_folder"]=self.sync_folder_dc.get_filename()
		self.data_tocheck["image"]={}
		self.data_tocheck["image"]["option"]=self.image_op

		self.apply_btn.set_sensitive(False)
		self.cancel_btn.set_sensitive(False)
	
		
		if self.image_op=="stock":
			self.image_path=self.custom_image
		else:
			self.image_path=self.image_fc.get_filename()
			
		self.data_tocheck["image"]["path"]=self.image_path

		self.core.mainWindow.waiting_label.set_text(self.core.mainWindow.get_msg(EditBox.VALIDATION_DATA_WAITING_CODE))			
		self.core.mainWindow.waiting_label.set_name("WAITING_LABEL")
		self.core.mainWindow.waiting_window.show_all()
		self.manage_form_control(False)
		self.init_threads()
		self.checking_data_t.start()
		GLib.timeout_add(100,self.pulsate_checking_data)
		
	#def gather_values	

	def pulsate_checking_data(self):
		
		if self.checking_data_t.is_alive():
			self.core.mainWindow.waiting_pbar.pulse()
			return True
			
		else:
			
			if not self.check["result"]:
				self.core.mainWindow.waiting_window.hide()
				self.manage_form_control(True)
				self.apply_btn.set_sensitive(True)
				self.cancel_btn.set_sensitive(True)
				msg_text=self.core.mainWindow.get_msg(self.check["code"])
				self.edit_msg_label.set_name("MSG_ERROR_LABEL")
				self.edit_msg_label.set_text(msg_text)
			else:	
				self.save_values()
		
		return False
		
	#def pulsate_checking_data	
		
	def checking_data(self):
		
		self.check=self.core.sitesmanager.check_data(self.data_tocheck,self.edit,self.origId)
	
	#def checking_data
		
	def save_values(self):		
		
		now = datetime.datetime.now()
		site_info={}
		copy_image=""
		site_info["id"]=self.data_tocheck["id"]
		site_info["name"]=self.data_tocheck["name"]
		site_info["description"]=self.data_tocheck["description"]
		site_info["visibility"]=self.site_visible_checkbt.get_active()
		site_info["image"]={}
		site_info["image"]["option"]=self.image_op

		if self.image_op=="stock":
			orig_img_path=self.custom_image
		else:
			orig_img_path=self.core.sitesmanager.url_site+self.data_tocheck["id"]+"/."+os.path.basename(self.data_tocheck["image"]["path"])
			if self.edit:
				if os.path.basename(self.data_tocheck["image"]["path"])!=self.orig_image:
					copy_image=self.data_tocheck["image"]["path"]
			else:
				copy_image=self.data_tocheck["image"]["path"]		

		site_info["image"]["img_path"]=orig_img_path
		site_info["image"]["font"]=self.img_font_chosser.get_font()
		color=self.get_color_rgba()
		site_info["image"]["color"]=color
		site_info["url"]=self.core.sitesmanager.url_site+self.data_tocheck["id"]
		site_info["site_folder"]=self.core.sitesmanager.net_folder+"/easy-"+self.data_tocheck["id"]

		if self.edit:
			action="edit"
			if self.data_tocheck["sync_folder"]==None:
				site_info["sync_folder"]=self.orig_sync_folder
			else:
				site_info["sync_folder"]=self.sync_folder_dc.get_filename()
			site_info["author"]=self.author
			site_info["date_creation"]=self.date_creation
			site_info["updated_by"]=self.core.sitesmanager.credentials[0]
			site_info["last_update"]=now.strftime("%Y-%m-%d %H:%M")

		else:		
			action="add"	
			site_info["sync_folder"]=self.sync_folder_dc.get_filename()	
			site_info["author"]=self.core.sitesmanager.credentials[0]
			site_info["updated_by"]=site_info["author"]
			site_info["date_creation"]=now.strftime("%Y-%m-%d %H:%M")
			site_info["last_update"]=site_info["date_creation"]


		window=self.image_da.get_window()
		pixbuf=Gdk.pixbuf_get_from_window(window,0,0,110,110)
		self.args=[action,site_info,pixbuf,self.require_sync,copy_image,self.origId]

		self.core.mainWindow.waiting_label.set_text(self.core.mainWindow.get_msg(EditBox.SAVIG_CHANGES_WAITING_CODE))			
		self.core.mainWindow.waiting_label.set_name("WAITING_LABEL")
		self.init_threads()
		self.saving_data_t.start()
		GLib.timeout_add(100,self.pulsate_saving_data)

	#def save_values
	
	def pulsate_saving_data(self):

		if self.saving_data_t.is_alive():
			self.core.mainWindow.waiting_pbar.pulse()
			return True
			
		else:
			self.core.mainWindow.waiting_window.hide()
			self.manage_form_control(True)
			if self.saving['status']:
				self.core.mainWindow.load_info()
				self.core.siteBox.draw_site(False)
			else:
				self.core.siteBox.draw_site(False)

			self.core.mainWindow.search_entry.set_text("")
			self.core.mainWindow.stack_window.set_transition_type(Gtk.StackTransitionType.SLIDE_RIGHT)
			self.core.mainWindow.stack_window.set_visible_child_name("optionBox")
			self.core.mainWindow.stack_opt.set_visible_child_name("siteBox")

			self.core.editBox.remove(self.core.editBox.main_box)

			if self.saving['status']:
				if self.edit:
					self.core.mainWindow.manage_message(False,10)
				else:
					self.core.mainWindow.manage_message(False,11)	
			else:
					self.core.mainWindow.manage_message(True,self.saving['code'])	
		return False
		
	#def pulsate_saving_data
	
	def saving_data(self):

		self.saving=self.core.sitesmanager.save_conf(self.args)
		print(self.saving)
	#def saving_data	

	
	def check_mimetype_image(self,widget):
	

		check=self.core.sitesmanager.check_mimetypes(self.image_fc.get_filename())
		if check !=None:
			msg=self.core.mainWindow.get_msg(check["code"])
			self.image_popover_msg.set_text(msg)
			self.image_popover_msg.set_name("MSG_ERROR_LABEL")
			self.image_popover_apply_bt.set_sensitive(False)
		else:
			self.image_popover_msg.set_text("")
			self.image_popover_apply_bt.set_sensitive(True)

	#def check_mimetype_image		

	def manage_form_control(self,sensitive):

		self.site_name_entry.set_sensitive(sensitive)
		self.site_description_entry.set_sensitive(sensitive)
		self.sync_folder_dc.set_sensitive(sensitive)
		self.site_visible_checkbt.set_sensitive(sensitive)
		self.image_eb.set_sensitive(sensitive)
		self.img_font_chosser.set_sensitive(sensitive)
		self.img_font_color_chosser.set_sensitive(sensitive)

	#def manage_form_control	

	def edit_image_clicked(self,widget,event=None):

		self.previous_image_op=self.image_op
		self.restore_img=True
		
		if self.image_op=="stock":
			self.previous_image_path=self.custom_image
		
		else:
			self.previous_image_path=self.image_fc.get_filename()
			if self.previous_image_path==None:
				self.image_popover_apply_bt.set_sensitive(False)
		
		self.image_popover.show_all()	

	#def edit_image_clicked	
	

	def image_popover_cancel_bt_clicked(self,widget):

		self.restore_img=True
		self.image_popover.hide()

	#def image_popover_cancel_bt_clicked	

	
	def image_popover_apply_bt_clicked(self,widget):	

		self.restore_img=False
		
		if self.image_op=="stock":
			path=self.custom_image
		else:
			path=self.image_fc.get_filename()
		
		self.image_da.queue_draw()
		self.image_da.connect("draw",self.drawing_banner_event)
		
		self.image_popover.hide()

	#def image_popover_apply_bt_clicked(self,widget)		


	def image_popover_closed(self,widget,event=None):

		self.restore_image_popover()
			
	#def image_popover_closed		

	def restore_image_popover(self):
	
		try:
			if self.restore_img:
				if self.previous_image_op=="stock":
					self.stock_rb.set_active(True)
					
				else:
					self.custom_rb.set_active(True)	
					self.image_fc.set_filename(self.previous_image_path)

				self.image_path=self.previous_image_path
		except:
			pass		

	#def restore_image_popover		


	def mouse_over_image(self,widget,event=None):

		self.image_box.set_name("IMAGE_BOX_HOVER")

	#def mouse_over_image

	def mouse_exit_image(self,widget,event=None):

		self.image_box.set_name("IMAGE_BOX")

	#def mouse_exit_image

	def detect_changes(self,widget,event=None):

		self.waiting=0
		if not self.waiting_draw:
			self.apply_btn.set_sensitive(False)
			self.cancel_btn.set_sensitive(False)
			self.edit_msg_label.set_text(self.core.mainWindow.get_msg(EditBox.APPLYNG_CHANGES_TOIMAGE_WAITING_CODE))
			self.edit_msg_label.set_name("WAITING_LABEL")
			self.waiting_draw=True
			GLib.timeout_add_seconds(1,self.pulsate_waiting_draw)

	#def detect_changes
	
	def pulsate_waiting_draw(self):

		 if self.waiting<3:
		 	self.waiting+=1
		 	return True

		 else:
		 	self.waiting_draw=False
		 	self.apply_btn.set_sensitive(True)
		 	self.cancel_btn.set_sensitive(True)
		 	self.edit_msg_label.set_text("")
		 	self.image_da.queue_draw()
		 	self.image_da.connect("draw",self.drawing_banner_event)
		 	return False

	#def pulsate_waiting_draw			


	def update_banner(self,widget,event=None):

		self.image_da.queue_draw()
		self.image_da.connect("draw",self.drawing_banner_event)
		
	#def update_banner	

	def cancel_clicked(self,widget):

		self.core.editBox.remove(self.core.editBox.main_box)
		self.core.mainWindow.stack_window.set_transition_type(Gtk.StackTransitionType.SLIDE_RIGHT)
		self.core.mainWindow.stack_window.set_visible_child_name("optionBox")
		self.core.mainWindow.stack_opt.set_visible_child_name("siteBox")

	#def cancel_clicked	
	
	def change_sync(self,widget):

		self.require_sync=True

	#def change_sync	

	def get_color_rgba(self):

		color=[]
		rgba=self.img_font_color_chosser.get_rgba()
		color=[rgba.red,rgba.green,rgba.blue,rgba.alpha]

		return color

	#def get_color_rgba	

	def change_checkbt_tooltip(self,button,name):

		if self.site_visible_checkbt.get_active():
			self.site_visible_checkbt.set_tooltip_text(_("Click to hide the site in the server main page"))
		else:
			self.site_visible_checkbt.set_tooltip_text(_("Click to show the site in the server main page"))

	#def change_checkbt_tooltip		

#class EditBox

from . import Core

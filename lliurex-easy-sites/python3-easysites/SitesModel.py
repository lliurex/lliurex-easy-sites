#!/usr/bin/python3
import os
import sys
from PySide6 import QtCore, QtGui, QtQml

class SitesModel(QtCore.QAbstractListModel):

	IdRole= QtCore.Qt.UserRole + 1000
	ImgRole = QtCore.Qt.UserRole+1001
	NameRole= QtCore.Qt.UserRole + 1002
	CreatedByRole = QtCore.Qt.UserRole+1003
	UpdatedByRole = QtCore.Qt.UserRole+1004
	IsVisibleRole = QtCore.Qt.UserRole+1005
	UrlRole = QtCore.Qt.UserRole+1006
	FolderRole = QtCore.Qt.UserRole+1007
	MountUnitRole = QtCore.Qt.UserRole+1008
	CanMountRole = QtCore.Qt.UserRole+1009
	IsActiveRole = QtCore.Qt.UserRole+1010
	
	def __init__(self,parent=None):
		
		super(SitesModel, self).__init__(parent)
		self._entries =[]
	
	#def __init__

	def rowCount(self, parent=QtCore.QModelIndex()):
		
		if parent.isValid():
			return 0
		return len(self._entries)

	#def rowCount

	def data(self, index, role=QtCore.Qt.DisplayRole):
		
		if 0 <= index.row() < self.rowCount() and index.isValid():
			item = self._entries[index.row()]
			if role == SitesModel.IdRole:
				return item["id"]
			elif role == SitesModel.ImgRole:
				return item["img"]
			elif role == SitesModel.NameRole:
				return item["name"]
			elif role == SitesModel.CreatedByRole:
				return item["createdBy"]
			elif role == SitesModel.UpdatedByRole:
				return item["updatedBy"]
			elif role == SitesModel.IsVisibleRole:
				return item["isVisible"]			
			elif role == SitesModel.UrlRole:
				return item["url"]			
			elif role == SitesModel.FolderRole:
				return item["folder"]
			elif role == SitesModel.MountUnitRole:
				return item["mountUnit"]
			elif role == SitesModel.CanMountRole:
				return item["canMount"]
			elif role == SitesModel.IsActiveRole:
				return item["isActive"]			

	#def data

	def roleNames(self):
		
		roles = dict()
		roles[SitesModel.IdRole] = b"id"
		roles[SitesModel.ImgRole]= b"img"
		roles[SitesModel.NameRole] = b"name"
		roles[SitesModel.CreatedByRole] = b"createdBy"
		roles[SitesModel.UpdatedByRole] = b"updatedBy"
		roles[SitesModel.IsVisibleRole]=b"isVisible"
		roles[SitesModel.UrlRole]=b"url"
		roles[SitesModel.FolderRole]=b"folder"
		roles[SitesModel.MountUnitRole]=b"mountUnit"
		roles[SitesModel.CanMountRole]=b"canMount"
		roles[SitesModel.IsActiveRole]=b"isActive"


		return roles

	#def roleNames

	def appendRow(self,i,im,na,cb,ub,vi,u,f,mu,cm,ia):
		
		tmpId=[]
		for item in self._entries:
			tmpId.append(item["id"])
		tmpN=na.strip()
		if i not in tmpId and na !="" and len(tmpN)>0:
			self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(),self.rowCount())
			self._entries.append(dict(id=i,img=im,name=na,createdBy=cb,updatedBy=ub,isVisible=vi,url=u,folder=f,mountUnit=mu,canMount=cm,isActive=ia))
			self.endInsertRows()

	#def appendRow

	def removeRow(self,index):
		self.beginRemoveRows(QtCore.QModelIndex(),index,index)
		self._entries.pop(index)
		self.endRemoveRows()
	
	#def removeRow

	def setData(self, index, param, value, role=QtCore.Qt.EditRole):
		
		if role == QtCore.Qt.EditRole:
			row = index.row()
			if param in ["isVisible","isActive"]:
				if self._entries[row][param]!=value:
					self._entries[row][param]=value
					self.dataChanged.emit(index,index)
					return True
				else:
					return False
			else:
				return False
	
	#def setData

	def clear(self):
		
		count=self.rowCount()
		self.beginRemoveRows(QtCore.QModelIndex(), 0, count)
		self._entries.clear()
		self.endRemoveRows()
	
	#def clear
	
#class SitesModel

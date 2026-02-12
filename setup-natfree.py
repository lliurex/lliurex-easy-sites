#!/usr/bin/env python3
#
# $Id: setup.py,v 1.32 2010/10/17 15:47:21 ghantoos Exp $
#
#    Copyright (C) 2008-2009  Ignace Mouzannar (ghantoos) <ghantoos@ghantoos.org>
#
#    This file is part of lshell
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from distutils.core import setup
from edupals.i18n import poinstaller
import sys
import os

if __name__ == '__main__':
	
	pinstaller = poinstaller.PoInstaller('translations/lliurex-easy-sites-natfree','lliurex-easy-sites','')
	pinstaller.build()
	polist = pinstaller.setup_install()
	listdir_images=map(lambda x:os.path.join('lliurex-easy-sites-natfree','data-files','images',x),os.listdir('lliurex-easy-sites-natfree/data-files/images'))
	listdir_templates=map(lambda x:os.path.join('lliurex-easy-sites-natfree','data-files','templates',x),os.listdir('lliurex-easy-sites-natfree/data-files/templates'))


	setup(name='lliurex-easysites-natfree',
		version='0.1',
		description='Easy Sites',
		long_description="""""",
		author='Lliurex Team',
		author_email='juapesai@hotmail.com',
		maintainer='Juan Ramon Pelegrina',
		maintainer_email='juapesai@hotmail.com',
		keywords=['software','server','sites'],
		url='http://www.lliurex.net',
		license='GPL',
		platforms='UNIX',
		packages = ['easysites'],
		package_dir = {'easysites':'lliurex-easy-sites-natfree/python3-easysites'},
		package_data = {'easysites':['rsrc/*']},
		data_files = [('sbin',['lliurex-easy-sites-natfree/lliurex-easy-sites']),('sbin',['lliurex-easy-sites-natfree/lliurex-easy-sites-gui']),
			      ('share/kservices5/ServiceMenus',['lliurex-easy-sites-natfree/data-files/create-easy-site.desktop']),
			      ('share/lliurex-easy-sites/images',listdir_images),('share/lliurex-easy-sites/templates',listdir_templates)
			      ] + polist ,
		classifiers=[
			'Development Status :: 4 - Beta',
			'Environment :: Console'
			'Intended Audience :: End Users',
			'License :: OSI Approved :: GNU General Public License v3',
			'Operating System :: POSIX',
			'Programming Language :: Python',
			'Topic :: Software',
			'Topic :: Install apps',
			],
	)
	pinstaller.clean()


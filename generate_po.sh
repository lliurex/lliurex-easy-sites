#!/bin/bash

xgettext --join-existing ./lliurex-easy-sites/python3-easysites/MainWindow.py -o ./translations/lliurex-easy-sites/lliurex-easy-sites.pot
xgettext --join-existing ./lliurex-easy-sites/python3-easysites/SiteBox.py -o ./translations/lliurex-easy-sites/lliurex-easy-sites.pot
xgettext --join-existing ./lliurex-easy-sites/python3-easysites/EditBox.py -o ./translations/lliurex-easy-sites/lliurex-easy-sites.pot
xgettext --join-existing ./lliurex-easy-sites/python3-easysites/rsrc/easy-sites.ui -o ./translations/lliurex-easy-sites/lliurex-easy-sites.pot



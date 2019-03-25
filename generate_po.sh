#!/bin/bash

xgettext --join-existing ./lliurex-easy-sites/python3-lliurex-easy-sites/MainWindow.py -o ./translations/lliurex-easy-sites.pot
xgettext --join-existing ./lliurex-easy-sites/python3-lliurex-easy-sites/SiteBox.py -o ./translations/lliurex-easy-sites.pot
xgettext --join-existing ./lliurex-easy-sites/python3-lliurex-easy-sites/EditBox.py -o ./translations/lliurex-easy-sites.pot
xgettext --join-existing ./lliurex-easy-sites/python3-lliurex-easy-sites/rsrc/easy-sites.ui -o ./translations/lliurex-easy-sites.pot



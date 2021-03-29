#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
    script.skin.helper.backgrounds
    Background service for rotating background images
'''

from resources.lib.backgrounds_updater import BackgroundsUpdater
from resources.lib.utils import log_msg
import xbmc

kodimonitor = xbmc.Monitor()

# run the background service
backgrounds_updater = BackgroundsUpdater(kodimonitor=kodimonitor)
backgrounds_updater.start()

# keep thread alive and send signal when we need to exit
while not kodimonitor.abortRequested():
    kodimonitor.waitForAbort(10)

# stop requested
log_msg("Abort requested !", xbmc.LOGNOTICE)
backgrounds_updater.stop()
log_msg("Stopped", xbmc.LOGNOTICE)
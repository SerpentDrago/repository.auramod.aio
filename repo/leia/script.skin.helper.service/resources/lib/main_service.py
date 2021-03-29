#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    script.skin.helper.service
    Helper service and scripts for Kodi skins
    main_service.py
    Background service running the various threads
"""

from utils import log_msg, ADDON_ID, log_exception
from skinsettings import SkinSettings
from listitem_monitor import ListItemMonitor
from kodi_monitor import KodiMonitor
from metadatautils import MetadataUtils
import xbmc
import xbmcaddon
import xbmcgui
from webservice import WebService


class MainService:
    """our main background service running the various threads"""
    last_skin = ""

    def __init__(self):
        self.win = xbmcgui.Window(10000)
        self.addon = xbmcaddon.Addon(ADDON_ID)
        self.metadatautils = MetadataUtils()
        self.addonname = self.addon.getAddonInfo('name').decode("utf-8")
        self.addonversion = self.addon.getAddonInfo('version').decode("utf-8")
        self.kodimonitor = KodiMonitor(metadatautils=self.metadatautils, win=self.win)
        self.listitem_monitor = ListItemMonitor(
            metadatautils=self.metadatautils, win=self.win, monitor=self.kodimonitor)
        self.webservice = WebService(self.metadatautils)
        self.win.clearProperty("SkinHelperShutdownRequested")

        # start the extra threads
        self.listitem_monitor.start()
        self.webservice.start()
        
        log_msg('%s version %s started' % (self.addonname, self.addonversion), xbmc.LOGNOTICE)

        # run as service, check skin every 10 seconds and keep the other threads alive
        while not self.kodimonitor.abortRequested():

            # check skin version info
            self.check_skin_version()

            # sleep for 10 seconds
            self.kodimonitor.waitForAbort(10)

        # Abort was requested while waiting. We should exit
        self.close()

    def close(self):
        """Cleanup Kodi Cpython instances"""
        self.webservice.stop()
        self.win.setProperty("SkinHelperShutdownRequested", "shutdown")
        log_msg('Shutdown requested !', xbmc.LOGNOTICE)
        self.listitem_monitor.stop()
        self.metadatautils.close()
        del self.win
        del self.kodimonitor
        # del self.metadatautils
        # del self.webservice
        log_msg('%s version %s stopped' % (self.addonname, self.addonversion), xbmc.LOGNOTICE)

    def check_skin_version(self):
        """check if skin changed"""
        try:
            skin = xbmc.getSkinDir()
            skin_addon = xbmcaddon.Addon(id=skin)
            skin_label = skin_addon.getAddonInfo('name').decode("utf-8")
            skin_version = skin_addon.getAddonInfo('version').decode("utf-8")
            this_skin = "%s-%s" % (skin_label, skin_version)
            del skin_addon
            if self.last_skin != this_skin:
                # auto correct skin settings if needed
                self.last_skin = this_skin
                self.win.setProperty("SkinHelper.skinTitle", "%s - %s: %s"
                                     % (skin_label, xbmc.getLocalizedString(19114), skin_version))
                self.win.setProperty("SkinHelper.skin_version", "%s: %s"
                                     % (xbmc.getLocalizedString(19114), skin_version))
                self.win.setProperty("SkinHelper.Version", self.addonversion.replace(".", ""))
                SkinSettings().correct_skin_settings()
        except Exception as exc:
            log_exception(__name__, exc)

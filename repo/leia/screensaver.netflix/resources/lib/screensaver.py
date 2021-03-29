# -*- coding: utf-8 -*-
import xbmc
import xbmcaddon
import xbmcgui

import random
import os

from resources.lib import utils

_addon = xbmcaddon.Addon()


class Screensaver(xbmcgui.WindowXMLDialog):
    
    class ExitMonitor(xbmc.Monitor):
        
        def __init__(self, exit_callback):
            self.exit_callback = exit_callback
            
        def onScreensaverActivated(self):
            utils.log('Screensaver Activated')
            
        def onScreensaverDeactivated(self):
            utils.log('Screensaver Deactivated')
            
            try:
                self.exit_callback()
            except AttributeError:
                utils.log('Callback method not yet available.')
    
    
    def __init__(self, *args, **kwargs):
        self.exit_monitor = None
        self.path = _addon.getSettingString('screensaver.netflix.path')
        utils.log(self.path)
    
    def onInit(self):
        self.character = self.getControl(1298)
        self.exit_monitor = self.ExitMonitor(self.exit)
        
        if self.path and self.exit_monitor:
            self.setProperty('screensaver.netflix.path', self.path)
            
            while not self.exit_monitor.abortRequested():
                factor = random.randrange(80) / 100.0
                x = 160 + int(400 * factor)
                y = int(self.character.getY())
                self.character.setPosition(x, y)
                
                xbmc.sleep(20000)

    def exit(self):
        if self.exit_monitor:
            del self.exit_monitor
            
        self.close()

# -*- coding: utf-8 -*-
import xbmc
import xbmcaddon

import os
import sys
import time

_addon = xbmcaddon.Addon()
_id = _addon.getAddonInfo('id').decode('utf-8')
_path = _addon.getAddonInfo('path').decode('utf-8')
_skin = os.path.basename(
            os.path.normpath(xbmc.translatePath('special://skin/')))
_xml = 'Custom_Screensaver_1166.xml'


def wait_for_string(string, shortcut):
    path = xbmc.getInfoLabel('Skin.String({})'.format(string))
    xbmc.executebuiltin(shortcut, wait=True)
        
    while path == xbmc.getInfoLabel('Skin.String({})'.format(string)):
        time.sleep(1)
        
    return xbmc.getInfoLabel('Skin.String({})'.format(string))


def get_params():
    for arg in [x for x in sys.argv if 'script.py' not in x]:
        if '=' in arg:
            arg_split = arg.split('=', 1)
            
            if arg_split[0] and arg_split[1]:
                return arg_split


if __name__ == '__main__':
    if get_params() == ['mode', 'choose']:
        call = ('RunScript(script.skinshortcuts,'
                'type=widgets'
                '&showNone=False'
                '&skinWidgetName=screensaver.auramod.name'
                '&skinWidgetPath=screensaver.auramod.path)')
        
        name = wait_for_string('screensaver.auramod.name', call)
        _addon.setSettingString('screensaver.auramod.name', name)
        
    elif get_params() == ['mode', 'tvchoose']:
        call = ('RunScript(script.skinshortcuts,'
                'type=widgets'
                '&showNone=False'
                '&skinWidgetName=screensaver.auramod.tvname'
                '&skinWidgetPath=screensaver.auramod.tvpath)')

        tvname = wait_for_string('screensaver.auramod.tvname', call)
        _addon.setSettingString('screensaver.auramod.tvname', tvname)

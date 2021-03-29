# -*- coding: utf-8 -*-
import xbmc
import xbmcaddon

import os
import sys

_addon = xbmcaddon.Addon()
_id = _addon.getAddonInfo('id')

def get_params():
    for arg in sys.argv:
        if arg == 'script.py':
            pass
        elif '=' in arg:
            arg_split = arg.split('=', 1)
            if arg_split[0] and arg_split[1]:
                return arg_split


if __name__ == '__main__':
    if get_params() == ['mode', 'choose']:
        call = ('RunScript(script.skinshortcuts,'
                'type=widgets'
                '&showNone=False'
                '&skinWidgetName={0}.name'
                '&skinWidgetPath={0}.path)'.format(_id))
        xbmc.executebuiltin(call, wait=True)
        
        name = xbmc.getInfoLabel('Skin.String({}.name)'.format(_id))
        path = xbmc.getInfoLabel('Skin.String({}.path)'.format(_id))
        _addon.setSettingString('{}.name'.format(_id), name)
        _addon.setSettingString('{}.path'.format(_id), path)

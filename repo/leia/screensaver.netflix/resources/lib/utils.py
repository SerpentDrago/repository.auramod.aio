# -*- coding: utf-8 -*-
import xbmc
import xbmcaddon

_addon = xbmcaddon.Addon()
_id = _addon.getAddonInfo('id').decode('utf-8')

def log(msg, level=xbmc.LOGDEBUG):
    message = '{}: {}'.format(_id, msg)
    xbmc.log(msg=msg, level=level)

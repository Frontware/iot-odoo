# -*- coding: utf-8 -*-
import logging
import requests
import json
from datetime import datetime

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from odoo.tools import float_round

_logger = logging.getLogger(__name__)

class FWIOT_device_remote_433(models.Model):
    _name = 'fwiot_device_remote_433'
    _inherit = 'fwiot_device_generic'
    _description = "Frontware IOT device: door open, button press"

    door_open = fields.Boolean(string='door open', required=True)
    button_press = fields.Boolean(string='button press', required=True)
    button_long_press  = fields.Boolean(string='button long press', required=True)

    def insert_record(self, device, data):
        """
        insert record with data
         - token
         - date
         - [door_open]
         - [button_press]
         - [long]
        """
        if not data.get('ts', False):
           return
        if '/status' in data['topic']:
           return

        d = datetime.fromtimestamp(data['ts'])
        
        r = self.search([('device_id','=', device.id),('date','=', d)])
        if not r.id:
           return self.create({
               "device_id": device.id,
               "date": d,
               "door_open": data.get('door_open', False),
               "button_press": data.get('button_pressed', False),
               "button_long_press": data.get('long', False),
           }) 

    def alert_record(self, device, data):
        """
        alert record
        """ 
        door_open = (data or {}).get('door_open', False)
        button_press = (data or {}).get('button_pressed', False)

        alerts = self.env['fwiot_device_alert'].search([('device_id','=', device.id),('active','=',True)])
        for each in alerts:
            if each.condition_fields == 'last_time':
               each.alert_record(device.last_online, 'last_time')
            elif each.condition_fields == 'door_open' and data:
               each.alert_record(door_open, 'door_open')
            elif each.condition_fields == 'button_press' and data:
               each.alert_record(button_press, 'button_press')               
            elif each.condition_fields == 'button_long_press' and data:
               each.alert_record(button_press, 'button_long_press')                              
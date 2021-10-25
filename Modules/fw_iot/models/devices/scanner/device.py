# -*- coding: utf-8 -*-
import logging
import requests
import json
from datetime import datetime

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from odoo.tools import float_round

_logger = logging.getLogger(__name__)

class FWIOT_device_scanner(models.Model):
    _name = 'fwiot_device_scanner'
    _inherit = 'fwiot_device_generic'
    _description = "Frontware IOT device: scanner"
    _order = 'date desc'

    mac = fields.Char('MAC')
    ssid = fields.Char('SSID')
    tx_power = fields.Integer('txPower')
    rssi  = fields.Integer('rssi')
    bluetooth = fields.Boolean('is bluetooth')
    type = fields.Selection([('in','In'), ('out','Out')], string='Type')

    def insert_record(self, device, data):
        """
        insert record with data
         - token
         - date
        """
        if not data.get('ts', False):
           return
        if '/status' in data['topic']:
           return

        d = datetime.fromtimestamp(data['ts'])
        if self.insert_history(device, data, d):
           return
        
        type = self._get_type(data)
        r = self.search([('device_id','=', device.id),('date','=', d),('type','=', type)])
        if not r.id:

           ble = False 
           if '/bluetooth/' in data['topic']:
              ble = True

           return self.create({
               "device_id": device.id,
               "date": d,
               "type": type,
               "bluetooth": ble,
               "mac": data.get('mac', False),
               "ssid": data.get('ssid', False),
               "tx_power": data.get('txPower', False),
               "rssi": data.get('rssi', False),
           }) 

    def _get_type(self, data):
        if 'wifi/out' in data['topic']:
           return 'out'
        if 'bluetooth/out' in data['topic']:
           return 'out'            
        return 'in' 

    @api.depends('date')
    def _compute_date_only(self):
        for each in self:
            each.date_only = each.date

    def alert_record(self, device, data):
        """
        alert record
        """ 
        alerts = self.env['fwiot_device_alert'].search([('device_id','=', device.id),('active','=',True)])
        for each in alerts:
            if each.condition_fields == 'last_time':
               each.alert_record(device.last_online, 'last_time')
            elif each.condition_fields == 'mac' and data:

               type = self._get_type(data)
               if (each.type == 'in' and type == 'in') or (each.type == 'out' and type == 'out'):
                  each.alert_record(data.get('mac', False), 'mac')

            elif each.condition_fields == 'ssid' and data:

               type = self._get_type(data)
               if (each.type == 'in' and type == 'in') or (each.type == 'out' and type == 'out'):
                   each.alert_record(data.get('ssid', False), 'ssid')

            elif each.condition_fields == 'tx_power' and data:
               each.alert_record(data.get('txPower', False), 'tx_power')
            elif each.condition_fields == 'rssi' and data:
               each.alert_record(data.get('rssi', False), 'rssi')               
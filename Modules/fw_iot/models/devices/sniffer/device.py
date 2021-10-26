# -*- coding: utf-8 -*-
import logging
import requests
import json
from datetime import datetime

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from odoo.tools import float_round

_logger = logging.getLogger(__name__)

class FWIOT_device_sniffer(models.Model):
    _name = 'fwiot_device_sniffer'
    _inherit = 'fwiot_device_generic'
    _description = "Frontware IOT device: sniffer"
    _order = 'date desc'

    mac = fields.Char(string="MAC")
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
        if not data.get('macs', False):
           return
        
        type = self._get_type(data)
        d = datetime.fromtimestamp(data['ts'])
        r = self.search([('device_id','=', device.id),('date','=', d),('type','=',type)],limit=1)
        if not r.id:
           mac_ids = []
           for m in data.get('macs', []):
               return self.create({
                     "device_id": device.id,
                     "date": d,
                     "type": type,
                     "mac": m,
               }) 

    def _get_type(self, data):
        if 'wifi/out' in data['topic']:
           return 'out'
        return 'in' 

    def alert_record(self, device, data):
        """
        alert record
        """ 
        alerts = self.env['fwiot_device_alert'].search([('device_id','=', device.id),('active','=',True)])
        for each in alerts:
            if each.condition_fields == 'last_time':
               each.alert_record(device.last_online, 'last_time')
            elif each.condition_fields == 'macs' and data:
               type = self._get_type(data)
               if (each.type == 'in' and type == 'in') or (each.type == 'out' and type == 'out'):
                  each.alert_record(data.get('mac', False), 'mac')

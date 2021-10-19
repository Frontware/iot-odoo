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

    macs = fields.Many2many('fwiot_device_mac', 'fwiot_device_sniffer_mac', 'device_id', 'mac_id', string='MACs')

    def insert_record(self, device, data):
        """
        insert record with data
         - token
         - date
        """
        if not data.get('ts', False):
           return

        d = datetime.fromtimestamp(data['ts'])
        if self.insert_history(device, data, d):
           return

        if not data.get('macs', False):
           return
        
        d = datetime.fromtimestamp(data['ts'])
        r = self.search([('device_id','=', device.id),('date','=', d)])
        if not r.id:
           mac_ids = []
           for m in data.get('macs', []):
               mmi = self.env['fwiot_device_mac'].search([('name','=', m)])
               if not mmi.id:
                  mmi = self.env['fwiot_device_mac'].create({'name':m})  
               
               mac_ids.append(mmi.id) 

           return self.create({
               "device_id": device.id,
               "date": d,
               "macs": [(6, 0, mac_ids)],
           }) 

    def alert_record(self, device, data):
        """
        alert record
        """ 
        alerts = self.env['fwiot_device_alert'].search([('device_id','=', device.id),('active','=',True)])
        for each in alerts:
            if each.condition_fields == 'last_time':
               each.alert_record(device.last_online, 'last_time')
            elif each.condition_fields == 'macs':
               each.alert_record(data.get('macs', False), 'macs')

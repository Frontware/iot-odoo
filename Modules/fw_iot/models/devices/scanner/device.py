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

    def insert_record(self, id, data):
        """
        insert record with data
         - token
         - date
        """
        if not data.get('ts', False):
           return
        
        d = datetime.fromtimestamp(data['ts'])
        r = self.search([('device_id','=', id),('date','=', d)])
        if not r.id:
           self.create({
               "device_id": id,
               "date": d,
               "bluetooth": data.get('rssi', False) != 0,
               "mac": data.get('mac', False),
               "ssid": data.get('ssid', False),
               "tx_power": data.get('txPower', False),
               "rssi": data.get('rssi', False),
           }) 

    @api.depends('date')
    def _compute_date_only(self):
        for each in self:
            each.date_only = each.date
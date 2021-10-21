# -*- coding: utf-8 -*-
import logging
import requests
import json
from datetime import datetime

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from odoo.tools import float_round

_logger = logging.getLogger(__name__)

class FWIOT_device_nfc_reader(models.Model):
    _name = 'fwiot_device_nfc_reader'
    _inherit = 'fwiot_device_generic'
    _description = "Frontware IOT device: nfc_reader"
    _order = 'date desc'

    rfid = fields.Char(string="RFID")

    def insert_record(self, device, data):
        """
        insert record with data
         - token
         - date
         - rfid
        """
        if not data.get('ts', False):
           return

        d = datetime.fromtimestamp(data['ts'])
        if self.insert_history(device, data, d):
           return

        if not data.get('rfid', False):
           return
        
        d = datetime.fromtimestamp(data['ts'])
        r = self.search([('device_id','=', device.id),('date','=', d)])
        if not r.id:
           return self.create({
               "device_id": device.id,
               "date": d,
               "rfid": data['rfid']
           }) 

    @api.depends('date')
    def _compute_date_only(self):
        for each in self:
            each.date_only = each.date

    def alert_record(self, device, data):
        """
        alert record
        """ 
        rfid = (data or {}).get('rfid', False)

        alerts = self.env['fwiot_device_alert'].search([('device_id','=', device.id),('active','=',True)])
        for each in alerts:
            if each.condition_fields == 'last_time':
               each.alert_record(device.last_online, 'last_time')
            elif each.condition_fields == 'rfid' and data:
               each.alert_record(rfid, 'rfid')            
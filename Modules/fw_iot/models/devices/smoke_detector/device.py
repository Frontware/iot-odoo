# -*- coding: utf-8 -*-
import logging
import requests
import json
from datetime import datetime

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from odoo.tools import float_round

_logger = logging.getLogger(__name__)

class FWIOT_device_smoke_detector(models.Model):
    _name = 'fwiot_device_smoke_detector'
    _inherit = 'fwiot_device_generic'
    _description = "Frontware IOT device: smoke detector"
    _order = 'date desc'

    def insert_record(self, device, data):
        """
        insert record with data
        """      
        if '/status' in data['topic']:
           return

        d = datetime.fromtimestamp(data)
        if self.insert_history(device, {"d":data}, d):
           return

        r = self.search([('device_id','=', device.id),('date','=', d)])
        if not r.id:
           return self.create({
               "device_id": device.id,
               "date": d,
           }) 

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

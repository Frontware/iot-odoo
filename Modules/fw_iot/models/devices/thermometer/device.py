# -*- coding: utf-8 -*-
import logging
import requests
import json
from datetime import datetime

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from odoo.tools import float_round

_logger = logging.getLogger(__name__)

class FWIOT_device_thermometer(models.Model):
    _name = 'fwiot_device_thermometer'
    _inherit = 'fwiot_device_generic'
    _description = "Frontware IOT device: thermometer"

    temperature = fields.Float(string='Temperature', required=True, digits=(4,4))

    def insert_record(self, token, data):
        """
        insert record with data
         - token
         - date
         - temperature
        """
        if not data.get('temp', False):
           return
        if not data.get('ts', False):
           return
        
        d = datetime.fromtimestamp(data['ts'])
        r = self.search([('device_id','=', id),('date','=', d)])
        if not r.id:
           self.create({
               "device_id": id,
               "date": d,
               "temperature": float_round(data['temp'], precision_digits=4)
           }) 
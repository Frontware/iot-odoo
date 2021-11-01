# -*- coding: utf-8 -*-
import logging
import requests
import json
from datetime import datetime

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from odoo.tools import float_round

_logger = logging.getLogger(__name__)

class FWIOT_device_thermo_humidity(models.Model):
    _name = 'fwiot_device_thermo_humidity'
    _inherit = 'fwiot_device_generic'
    _description = "Frontware IOT device: thermometer humidity"

    temperature = fields.Float(string='Temperature', required=True, digits=(4,4))
    humidity = fields.Float(string='Humidity', required=True, digits=(4,4))

    def insert_record(self, device, data):
        """
        insert record with data
         - token
         - date
         - temperature
         - humidity
        """
        if not data.get('ts', False):
           return
        if '/status' in data['topic']:
           return

        d = datetime.fromtimestamp(data['ts'])
        if not data.get('temp', False):
           return
        
        r = self.search([('device_id','=', device.id),('date','=', d)])
        if not r.id:
           return self.create({
               "device_id": device.id,
               "date": d,
               "temperature": float_round(data['temp'], precision_digits=4),
               "humidity": float_round(data['hum'], precision_digits=4)
           }) 

    def alert_record(self, device, data):
        """
        alert record
        """ 
        temp = (data or {}).get('temp', False)
        hum = (data or {}).get('hum', False)

        alerts = self.env['fwiot_device_alert'].search([('device_id','=', device.id),('active','=',True)])
        for each in alerts:
            if each.condition_fields == 'last_time':
               each.alert_record(device.last_online, 'last_time')
            elif each.condition_fields == 'temperature' and data:
               each.alert_record(temp, 'temperature')
            elif each.condition_fields == 'humidity' and data:
               each.alert_record(hum, 'humidity')               
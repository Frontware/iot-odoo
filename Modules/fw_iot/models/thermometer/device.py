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
    _description = "Frontware IOT device: thermometer"
    _order = 'date desc'

    temperature = fields.Float(string='Temperature', required=True, digits=(4,4))
    date = fields.Datetime(string="Date")
    token = fields.Char(string='Token')
    date_only = fields.Date(compute='_compute_date_only', string="Date", store=True, readonly=True)


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
        r = self.search([('token','=', token),('date','=', d)])
        if not r.id:
           self.create({
               "token": token,
               "date": d,
               "temperature": float_round(data['temp'], precision_digits=4)
           }) 

    @api.depends('date')
    def _compute_date_only(self):
        for each in self:
            each.date_only = each.date
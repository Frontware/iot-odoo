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
    _description = "Frontware IOT device: scanner"
    _order = 'date desc'

    date = fields.Datetime(string="Date")
    token = fields.Char(string='Token')
    date_only = fields.Date(compute='_compute_date_only', string="Date", store=True, readonly=True)

    def insert_record(self, token, data):
        """
        insert record with data
         - token
         - date
        """
        if not data.get('ts', False):
           return
        
        d = datetime.fromtimestamp(data['ts'])
        r = self.search([('token','=', token),('date','=', d)])
        if not r.id:
           self.create({
               "token": token,
               "date": d
           }) 

    @api.depends('date')
    def _compute_date_only(self):
        for each in self:
            each.date_only = each.date
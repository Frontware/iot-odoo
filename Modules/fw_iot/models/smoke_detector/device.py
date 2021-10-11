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
    _description = "Frontware IOT device: smoke detector"
    _order = 'date desc'

    date = fields.Datetime(string="Date")
    token = fields.Char(string='Token')
    date_only = fields.Date(compute='_compute_date_only', string="Date", store=True, readonly=True)


    def insert_record(self, token, data):
        """
        insert record with data
        """        
        d = datetime.fromtimestamp(data)
        r = self.search([('token','=', token),('date','=', d)])
        if not r.id:
           self.create({
               "token": token,
               "date": d,
           }) 

    @api.depends('date')
    def _compute_date_only(self):
        for each in self:
            each.date_only = each.date
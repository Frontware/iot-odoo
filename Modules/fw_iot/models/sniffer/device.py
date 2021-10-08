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
    _description = "Frontware IOT device: sniffer"
    _order = 'date desc'

    date = fields.Datetime(string="Date")
    token = fields.Char(string='Token')
    date_only = fields.Date(compute='_compute_date_only', string="Date", store=True, readonly=True)

    macs = fields.Many2many('fwiot_device_mac', 'fwiot_device_sniffer_mac', 'device_id', 'mac_id', string='MACs')

    def insert_record(self, token, data):
        """
        insert record with data
         - token
         - date
        """
        if not data.get('ts', False):
           return
        if not data.get('macs', False):
           return
        
        d = datetime.fromtimestamp(data['ts'])
        r = self.search([('token','=', token),('date','=', d)])
        if not r.id:
           mac_ids = []
           for m in data.get('macs', []):
               mmi = self.env['fwiot_device_mac'].search([('name','=', m)])
               if not mmi.id:
                  mmi = self.env['fwiot_device_mac'].create({'name':m})  
               
               mac_ids.append(mmi.id) 

           self.create({
               "token": token,
               "date": d,
               "macs": [(6, 0, mac_ids)],
           }) 

    @api.depends('date')
    def _compute_date_only(self):
        for each in self:
            each.date_only = each.date
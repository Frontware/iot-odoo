# -*- coding: utf-8 -*-
import logging
import requests
import json
from datetime import datetime

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from odoo.tools import float_round

_logger = logging.getLogger(__name__)


class FWIOT_device_generic(models.Model):
    _name = 'fwiot_device_generic'
    _description = "Frontware IOT device: generic"
    _order = 'date desc'

    date = fields.Datetime(string="Date")
    device_id = fields.Many2one('fwiot_device', string='Device')
    date_only = fields.Date(compute='_compute_date_only',
                            string="Date", store=True, readonly=True)

    @api.depends('date')
    def _compute_date_only(self):
        for each in self:
            each.date_only = each.date

    def insert_history(self, device, data, d):
        """
        insert status data
        """
        if not data.get('status', False):
            return

        his = self.env['fwiot_device_status']
        r = his.search([('device_id', '=', device.id), ('date', '=', d)])
        if not r.id:
            return his.create({
                "device_id": device.id,
                "date": d,
                "status": data.get('status')
            })

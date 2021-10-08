# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _

class FWIOT_device_mac(models.Model):
    _name = 'fwiot_device_mac'
    _description = "Frontware IOT device mac address"

    name = fields.Char(string="MAC", required=True)

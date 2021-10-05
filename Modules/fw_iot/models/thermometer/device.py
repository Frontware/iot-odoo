# -*- coding: utf-8 -*-
import logging
import requests
import json

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class FWIOT_device_thermometer(models.Model):
    _name = 'fwiot_device_thermometer'
    _description = "Frontware IOT device: thermometer"

    temperature = fields.Float(string='Temperature', required=True, digits=4)
    date = fields.Date(string="Date")
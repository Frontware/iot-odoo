# -*- coding: utf-8 -*-
import logging
import requests
import json
from datetime import datetime

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from odoo.tools import float_round

_logger = logging.getLogger(__name__)

class FWIOT_device_status(models.Model):
    _name = 'fwiot_device_status'
    _inherit = 'fwiot_device_generic'
    _description = "Frontware IOT device: status"
    _order = 'date desc'

    status = fields.Char(string='Status')
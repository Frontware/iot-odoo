# -*- coding: utf-8 -*-
import logging
import re

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class FWIOT_device_type(models.Model):
    _name = 'fwiot_device_type'
    _description = "Frontware IOT device type"
    _inherit = ['mail.thread']

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code", required=True)
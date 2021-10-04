# -*- coding: utf-8 -*-
import logging
import re

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class FWIOT_device(models.Model):
    _name = 'fwiot_device'
    _description = "Frontware IOT device"
    _inherit = ['mail.alias.mixin', 'mail.thread']

    active = fields.Boolean(string="Active")
    name = fields.Char(string="Name", required=True)
    type = fields.Many2one('fwiot_device_type',string="Type",required=True)
    guid = fields.Char(string="GUID")
    lock_code = fields.Char(string="Lock code")
    unlock_code = fields.Char(string="Unlock code")
    note = fields.Text(string="Note")
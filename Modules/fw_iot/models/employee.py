# -*- coding: utf-8 -*-
import logging
import re

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class FWIOTEmployee(models.Model):
    _inherit = 'hr.employee'

    telegram_id = fields.Char(string='Telegram ID')
    line_token = fields.Char(string='Line token')
    lang = fields.Char(compute='_get_user_lang',readonly=True,default=lambda self: self.env.user.lang)
    
    def _get_user_lang(self):
        for each in self:
            each.lang = self.env.user.lang
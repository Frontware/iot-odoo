# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _

class FWIOT_tg_chat(models.Model):
    _name = 'fwiot_tg_chat'
    _description = "Frontware IOT telegram chat"

    name = fields.Char(string="Name", required=True)
    chat_id = fields.Integer(string="Chat id", required=True)

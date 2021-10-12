# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime
import requests
import json

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class FWIOTDeviceCronkWizard(models.TransientModel):
    _name = 'fwiot_device_cron_wizard'
    _description = 'Frontware IOT: device\'s schedule setting'

    interval_active = fields.Boolean(string='Active')
    interval_number = fields.Integer(default=1, help="Repeat every x.")
    interval_type = fields.Selection([('minutes', 'Minutes'),
                                      ('hours', 'Hours'),
                                      ('days', 'Days'),
                                      ('weeks', 'Weeks'),
                                      ('months', 'Months')], string='Interval Unit', default='days')    
    schedule_id = fields.Many2one('ir.cron',string="Schedule")

    def action_confirm(self):
        """
        confirm and change status
        """   
        return self.schedule_id.write({
            'active': self.interval_active,
            'interval_number': self.interval_number,
            'interval_type': self.interval_type,
        })
        
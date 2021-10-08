# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime
import requests
import json

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class FWIOTDeviceLockWizard(models.TransientModel):
    _name = 'fwiot_device_lock_wizard'
    _description = 'Frontware IOT: confirm lock / unlock device'

    lock = fields.Boolean(string="Lock")
    code = fields.Char(string="Code")

    def action_confirm(self):
        """
        confirm and change status
        """        
        r = requests.get(self.code)
        t = _('lock')
        if not self.lock:
           t = _('unlock')
        
        if r.status_code != 200:
           raise UserError(_('Error while try to %s this device') % t)
        
        rr = json.loads(r.content)
        if rr.get('error'):
           raise UserError(_('Error while try to %s this device: %s') % (t, rr.get('error') )) 

        self.env['fwiot_device'].browse(self.env.context.get('active_id'))\
            .write({
                'locked': self.lock
            })

        return
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import requests
from requests.structures import CaseInsensitiveDict

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class FWIOTDeviceGenericSettingWizard(models.TransientModel):
    _name = 'fwiot_device_generic_setting_wizard'
    _description = 'Frontware IOT device: generic setting'

    device_id = fields.Many2one('fwiot_device', String='device', default=lambda self: self.env.context.get('device_id', False))
    device_locked = fields.Boolean(compute='_get_device')

    @api.depends('device_id')
    def _get_device(self):
        for each in self:
            each.device_locked = each.device_id.locked

    def get_action_data(self):
        return {}

    def action_update(self):
        """
        update setting
        """        
        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/json"

        data = self.get_action_data()

        resp = requests.post(self.env.context.get('code'), headers=headers, data=json.dumps(data))

        if resp.status_code != 200:
           raise UserError(_('Error while send new settings to device')) 

        j = json.loads(resp.content)
        
        if j.get('error',''):
           raise UserError(_('Error while send new settings to device : %s' % j.get('error', 'Unexpected error')))  

        return
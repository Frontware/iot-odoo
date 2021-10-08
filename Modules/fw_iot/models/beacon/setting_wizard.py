# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import requests
from requests.structures import CaseInsensitiveDict

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class FWIOTDeviceBeaconSettingWizard(models.TransientModel):
    _name = 'fwiot_device_beacon_setting_wizard'
    _description = 'Frontware IOT: show beacon setting'

    uuid = fields.Char(string='UUID', help='Proximity ID for iBeacon')
    major = fields.Integer(string='major', help='major (0 to 65535) for beacon')
    minor = fields.Integer(string='minor', help='minor (0 to 65535) for beacon')

    def action_update(self):
        """
        update setting
        """        
        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/json"

        data = {
            "uuid": self.uuid,
            "major": self.major,
            "minor": self.minor,
        }

        resp = requests.post(self.env.context.get('code'), headers=headers, data=json.dumps(data))

        if resp.status_code != 200:
           raise UserError(_('Error while send new settings to device')) 

        j = json.loads(resp.content)
        
        if j.get('error',''):
           raise UserError(_('Error while send new settings to device : %s' % j.get('error', 'Unexpected error')))  

        return
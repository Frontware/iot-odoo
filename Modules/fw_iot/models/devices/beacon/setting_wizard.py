# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import requests
from requests.structures import CaseInsensitiveDict

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class FWIOTDeviceBeaconSettingWizard(models.TransientModel):
    _name = 'fwiot_device_beacon_setting_wizard'
    _inherit = 'fwiot_device_generic_setting_wizard'
    _description = 'Frontware IOT: show beacon setting'

    uuid = fields.Char(string='UUID', help='Proximity ID for iBeacon')
    major = fields.Integer(string='major', help='major (0 to 65535) for beacon')
    minor = fields.Integer(string='minor', help='minor (0 to 65535) for beacon')

    def get_action_data(self):
        return {
            "uuid": self.uuid,
            "major": self.major,
            "minor": self.minor,
        }
        
    def save_setting(self, data):
        """
        save current setting
        """
        self.create({
            "uuid": data.get('uuid', ''),
            "major": data.get('major', False),
            "minor": data.get('minor', False),
        })

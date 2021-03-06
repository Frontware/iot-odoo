# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime

from odoo import api, fields, models

class FWIOTDeviceCreateWizard(models.TransientModel):
    _name = 'fwiot_device_create_wizard'
    _description = 'Frontware IOT: show device status from iot'

    type = fields.Char(string="Type")
    type_code = fields.Char(string="Type Code")
    serial = fields.Char(string="Serial")
    active = fields.Boolean(string="Active")
    locked = fields.Boolean(string="Locked")
    token = fields.Char(string="Token")
    settings = fields.Text(string="JSON settings")
    web_hook_url = fields.Char(string="Web Hook URL")
    web_hook_header = fields.Text(string="Web Hook header")
    csv_url = fields.Text(string="CSV URL")
    json_url = fields.Text(string="JSON URL")
    status = fields.Char(string="Status")
    last_online = fields.Datetime(string="Last online")
    firmware_version = fields.Char(string='Firmware version number')

    def action_confirm(self):
        """
        confirm and change status
        """
        # create new type if not exist.
        t = self.env['fwiot_device_type'].search([('code','=',self.type_code)])
        if not t.id:
           t = self.env['fwiot_device_type'].create({
               "code": self.type_code,
               "name": self.type
            }) 

        self.env['fwiot_device'].browse(self.env.context.get('active_id'))\
            .write({
                'state': 'confirm', 
                'active': self.active,
                'token': self.token,
                'serial': self.serial, 
                'status': self.status,
                'locked': self.locked,
                'last_online': self.last_online,
                'firmware_version': self.firmware_version,
                'last_fetch' : datetime.now(),
                'type': t.id})

        return
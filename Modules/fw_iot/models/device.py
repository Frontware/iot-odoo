# -*- coding: utf-8 -*-
import logging
import requests
import json
from datetime import datetime
from odoo.addons.fw_iot.models.device_implement import DEVICE_IMPLEMENT

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class FWIOT_device(models.Model):
    _name = 'fwiot_device'
    _description = "Frontware IOT device"
    _inherit = ['mail.thread']

    active = fields.Boolean(string="Active", default=True)
    name = fields.Char(string="Name", required=True)
    guid = fields.Char(string="API Key")
    unlock_code = fields.Char(string="Unlock code")
    note = fields.Text(string="Note")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm')
    ], string='Status', copy=False, index=True, readonly=True, default='draft', help="Status of the device.")

    token = fields.Char(string="Token")
    serial = fields.Integer(string="Serial")
    status = fields.Char(string="Status")
    type = fields.Many2one('fwiot_device_type',string="Type")
    last_fetch = fields.Datetime(string='Last updated')
    locked = fields.Boolean(string="Lock/Unlock")

    is_implement = fields.Boolean(compute='_compute_device_implement')
    has_action = fields.Boolean(compute='_compute_device_implement')
    has_data = fields.Boolean(compute='_compute_device_implement')
    has_setting = fields.Boolean(compute='_compute_device_implement')

    def _get_status(self):
        """
        get status
        """
        if not self.guid:
           raise UserError('You must enter API Key') 
        
        url = 'https://iot.frontware.com/status/%s' % self.guid
        r = requests.get(url)
        
        if r.status_code != 200:
           raise UserError('Error while try to check this device status') 

        return json.loads(r.content)

    def action_confirm(self):
        """
        confirm record
        """
        if not self.guid:
           raise UserError('You must enter API Key') 
        
        j = self._get_status()
       
        newid = self.env['fwiot_device_create_wizard'].create({
            "type": j.get('device_type_name', False),
            "type_code": j.get('device_type_code', False),
            "serial": j.get('serial', False),
            "active": j.get('active', False),
            "locked": j.get('locked', False),
            "token": j.get('token', False),
            "settings": j.get('json_settings', False),
            "web_hook_url": j.get('web_hook_url', False),
            "web_hook_header": j.get('web_hook_header', False),
            "csv_url": j.get('csv_url', False),
            "json_url": j.get('json_url', False),
            "status": j.get('status', False),
        })

        return {
                'type': 'ir.actions.act_window',
                'name': _('Device status'),
                'res_model': 'fwiot_device_create_wizard',
                'view_mode': 'form',
                'res_id': newid.id,
                'target': 'new',
                'context': {'active_id': self.id},
                'views': [[False, 'form']]
            }
    
    def action_fetch(self):
        """
        fetch record
        """
        j_status = self._get_status()
        self.write({
            'locked': j_status.get('locked', False),
            'status': j_status.get('status', False),
            'serial': j_status.get('serial', False),
            'last_fetch' : datetime.now()
        })

        if not self.is_implement:
           return 

        url = 'https://iot.frontware.com/json/%s.json' % self.guid
        r = requests.get(url)
        
        if r.status_code != 200:
           raise UserError('Error while try to get this device data') 
        
        if r.content:
           # list
           jj = json.loads(r.content)
           m = self._get_device_model()
           mctl = self.env[m]
           for j in jj:
               mctl.insert_record(self.token, json.loads(j['data']))

    def _get_device_implement(self):
        for d in DEVICE_IMPLEMENT:
            if self.type.code in d['code']:
               return d
        return {}

    def _get_device_data_action(self):
        """
        get device data action
        """
        return self._get_device_implement().get('action', {}).get('data', False)

    def _get_device_model(self):
        """
        get device model
        """
        return self._get_device_implement().get('model', False)

    def action_view_all_data(self):
        """
        show data
        """
        if not self.is_implement:
           return 

        ir_act = self._get_device_data_action()

        action = self.env["ir.actions.actions"]._for_xml_id(ir_act)
        action['context'] = {}
        action['domain'] = [('token', '=', self.token)]
        return action

    @api.depends('type')
    def _compute_device_implement(self):
        """
        compute field is_implement according type
        """
        for d in self:
            isimp = False
            h_data = False
            h_action = False
            h_set = False
            for dv in DEVICE_IMPLEMENT:
                 if d.type.code in dv['code']:
                    isimp = True
                    h_data = dv['action'].get('data', False)
                    h_action = dv['action'].get('action', False)
                    h_set = dv['action'].get('setting', False)
                    break
            d.is_implement = isimp     
            d.has_data = h_data
            d.has_setting = h_set
            d.has_action = h_action
    
    def action_lock(self):
        """
        click lock
        """
        return self._action_to_lock(True)

    def action_unlock(self):
        """
        click unlock
        """
        return self._action_to_lock(False)

    def _action_to_lock(self, lock):
        """
        lock/unlock record
        """       
        code = "lock/%s" % self.guid
        if not lock:
           code = "unlock/%s/%s" % (self.guid, self.unlock_code)
        
        newid = self.env['fwiot_device_lock_wizard'].create({
            "lock": lock,
            "code": "https://iot.frontware.com/%s" % code,
        })

        return {
                'type': 'ir.actions.act_window',
                'name': _('Device'),
                'res_model': 'fwiot_device_lock_wizard',
                'view_mode': 'form',
                'res_id': newid.id,
                'target': 'new',
                'context': {'active_id': self.id},
                'views': [[False, 'form']]
            }
    
    def action_command(self):
        """
        send action
        """
        if not self.is_implement:
           return 

        ir_act = self._get_device_implement().get('action', {}).get('action', False)

        action = self.env["ir.actions.actions"]._for_xml_id(ir_act)
        action['context'] = dict(self.env.context)

        action['context']['code'] = self.guid
        return action

    def action_setting(self):
        """
        update settings
        """
        if not self.is_implement:
           return 

        ir_act = self._get_device_implement().get('action', {}).get('setting', False)

        action = self.env["ir.actions.actions"]._for_xml_id(ir_act)
        action['context'] = dict(self.env.context)

        code = " https://iot.frontware.com/settings/%s" % self.guid
        action['context']['code'] = code
        
        last = self.env[self._get_device_implement().get('wizard-model')].search([], limit=1)
        print(last.id)
        action['res_id'] = last.id

        return action

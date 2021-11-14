# -*- coding: utf-8 -*-
import logging
import requests
import json
import base64
from datetime import datetime

from odoo.addons.fw_iot.models.device_implement import DEVICE_IMPLEMENT

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from odoo.modules.module import get_module_resource

_logger = logging.getLogger(__name__)

class FWIOT_device(models.Model):
    _name = 'fwiot_device'
    _description = "Frontware IOT device"
    _inherit = ['mail.thread', 'image.mixin']

    active = fields.Boolean(string="Active", default=True)
    name = fields.Char(string="Name", required=True)
    guid = fields.Char(string="API Key")
    unlock_code = fields.Char(string="Unlock code")
    note = fields.Text(string="Note")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm')
    ], string='State', copy=False, index=True, readonly=True, default='draft', help="Status of the device.")

    token = fields.Char(string="Token")
    serial = fields.Integer(string="Serial")
    status = fields.Char(string="Status")
    type = fields.Many2one('fwiot_device_type',string="Device type")
    last_fetch = fields.Datetime(string='Last updated')
    locked = fields.Boolean(string="Lock")
    last_online = fields.Datetime(string='Last online')
    firmware_version = fields.Char(string='Firmware version number')

    is_implement = fields.Boolean(compute='_compute_device_implement')
    has_action = fields.Boolean(compute='_compute_device_implement')
    has_data = fields.Boolean(compute='_compute_device_implement')
    has_setting = fields.Boolean(compute='_compute_device_implement')
    show_ribbon = fields.Char(compute='_compute_device_status',readonly=True)

    alerts = fields.One2many('fwiot_device_alert', 'device_id', string='Alert trigger')
    
    def _compute_device_status(self):
        for each in self:
            if each.state != 'confirm' or not each.last_online:
               each.show_ribbon = '' 

            elif (each.status == 'Online') and (each.state == 'confirm'):
               each.show_ribbon = 'green' 
            else:
                dt = (datetime.now() - each.last_online).total_seconds() / (60 * 60 * 24)
                if dt < 1:
                   each.show_ribbon = 'yellow' 
                else:
                   each.show_ribbon = 'red'                 

    def _get_status(self):
        """
        get status
        """
        if not self.guid:
           raise UserError(_('You must enter API Key')) 
        
        url = 'https://iot.frontware.com/status/%s' % self.guid
        r = requests.get(url)
        
        if r.status_code != 200:
           raise UserError(_('Error while try to check this device status')) 

        return json.loads(r.content)

    def action_confirm(self):
        """
        confirm record
        """
        if not self.guid:
           raise UserError(_('You must enter API Key'))
        
        j = self._get_status()

        jt = j.get('last_online', False)
        if jt:
           jt = datetime.fromtimestamp(jt) 
       
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
            "firmware_version": j.get('version', False),
            "last_online": jt,
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
        
        jt = j_status.get('last_online', False)
        if jt:
           jt = datetime.fromtimestamp(jt) 
        self.write({
            'locked': j_status.get('locked', False),
            'status': j_status.get('status', False),
            'serial': j_status.get('serial', False),
            'firmware_version': j_status.get('version', False),
            'last_online': jt,
            'last_fetch' : datetime.now()
        })
        
        # store last setting
        j_set = j_status.get('json_settings', False)
        if j_set:
           j_setting = json.loads(j_set)
           j_set_mod = self._get_device_implement().get('setting', {}).get('model', False)
           if j_set_mod:
              self.env[j_set_mod].save_setting(j_setting)

        if not self.is_implement:
           return 

        url = 'https://iot.frontware.com/json/%s.json' % self.guid
        r = requests.get(url)
        
        if r.status_code != 200:
           raise UserError(_('Error while try to get this device data'))
        
        if r.content:
           # list
           jj = json.loads(r.content)           
           m = self._get_device_model()
           mctl = False
           if self.has_data:
              mctl = self.env[m]
           last = False           
           for j in jj or []:
               jd = json.loads(j['data'])
               if not type(jd) is dict:
                  jd = {'data': jd} 
               jd['topic'] = j['topic']   
               
               if self.insert_history(jd):
                  # this is status record 
                  continue 

               if self.has_data and mctl.insert_record(self, jd):
                  last = jd
           if self.has_data:
              mctl.alert_record(self, last)

    def insert_history(self, data):
        """
        insert status data
        """
        if not data.get('status', False):
           return
        d = datetime.fromtimestamp(data.get('ts',False))

        his = self.env['fwiot_device_status']       
        r = his.search([('device_id','=', self.id),('date','=', d)])
        if not r.id:
           return his.create({
               "device_id": self.id,
               "date": d,
               "status": data.get('status')
           }) 
        else:
           return True 

    def _get_device_implement(self):
        """
        get device match with type.code
        """
        for d in DEVICE_IMPLEMENT:
            if self.type.code in d['code']:
               return d
        return {}

    def _get_device_data_action(self):
        """
        get device data action
        """
        return self._get_device_implement().get('data', {}).get('action', False)

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
        action['domain'] = [('device_id', '=', self.id)]
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
                    h_data = dv.get('data',{}).get('action', False)
                    h_action = dv.get('action', {}).get('action', False)
                    h_set = dv['setting'].get('action', False)
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
    
    def action_setting(self):
        """
        update settings
        """
        if not self.is_implement:
           return 

        ir_act = self._get_device_implement().get('setting', {}).get('action', False)

        action = self.env["ir.actions.actions"]._for_xml_id(ir_act)
        action['context'] = dict(self.env.context)

        code = " https://iot.frontware.com/settings/%s" % self.guid
        action['context']['code'] = code
        
        last = self.env[self._get_device_implement().get('setting', {}).get('model')].search([], limit=1, order='id desc')
        action['res_id'] = last.id
        action['device_id'] = self.id
        last.write({'device_id': self.id})

        return action

    @api.model
    def _cron_get_data(self, type0):
        """
        get data
        """
        ttype = type0
        for d in DEVICE_IMPLEMENT:
            if type0 in d['code']:
               ttype = d['code'][0]
        records = self.search([
            ('state', '=', 'confirm'),
            ('type.code','=', ttype)
        ])

        for ids in records:
            ids.action_fetch()            

    def get_schedule(self):
        sch_model = self._get_device_implement().get('data', {}).get('schedule_id', False)
        if not sch_model:
           return
                
        return self.env.ref(sch_model)

    def action_schedule(self):
        """
        update schedule settings
        """
        if not self.is_implement:
           return 
                        
        sch = self.get_schedule()
        if not sch:
           return
        
        sch_id = self.env['fwiot_device_cron_wizard'].create({
            'interval_active': sch.active,
            'interval_number': sch.interval_number,
            'interval_type': sch.interval_type,
            'schedule_id': sch.id,
        })

        action = self.env["ir.actions.actions"]._for_xml_id('fw_iot.fwiot_device_cron_wizard_action')
        action['context'] = dict(self.env.context)
        action['res_id'] = sch_id.id
        return action

    def action_notify(self):
        """
        setup alert trigger
        """        
        return {
                'type': 'ir.actions.act_window',
                'name': _('Device action'),
                'res_model': 'fwiot_device_alert',
                'view_mode': 'tree,form',
                'domain': [('device_id', '=', self.id)],
                'context': {'device_id': self.id},
            }

    @api.model
    def get_condition_fields(self, device_id):
        """
        get fields list from device
        """
        ff = []                
        langdb = self.env['ir.translation']
        fdb = self.env['ir.model.fields']
        dv = self.browse(device_id)._get_device_implement()
        
        for each in dv.get('alert', {}).get('fields', []):
            f = fdb._get(dv.get('model'), each)
            ff.append(
                (each, langdb._get_ids('ir.model.fields,field_description', 'model', self.env.user.lang, [f.id]).get(f.id) or each)
            )
        return ff
    
    def action_view_history(self):
        """
        show history data
        """
        if not self.is_implement:
           return 
        action = self.env["ir.actions.actions"]._for_xml_id('fw_iot.fwiot_device_status_action')
        action['context'] = {}
        action['domain'] = [('device_id', '=', self.id)]
        return action

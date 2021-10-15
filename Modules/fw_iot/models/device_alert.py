# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _

class FWIOT_device_alert(models.Model):
    _name = 'fwiot_device_alert'
    _description = "Frontware IOT device alert trigger"
    _inherit = ['mail.thread']

    device_id = fields.Many2one('fwiot_device', string='Device', default=lambda self: self.env.context.get('device_id'))
    name = fields.Char(string='Name')

    condition_fields = fields.Selection(selection='_get_condition_fields', string="if")
    condition_type = fields.Selection([('<>', '<>'),
                                       ('=', '='),
                                       ('<', '<'),
                                       ('>', '>')
                                       ], string="operator")
    condition_value = fields.Char(string='compare value')
    condition_last_min = fields.Integer(string='last seen')

    message_type = fields.Selection([('odoo','Odoo Bot')],string='Message type')
    message = fields.Text(string='Message')

    allow_partner_ids = fields.Many2many('res.partner', compute='_get_allow_partner',readonly=True,string="allowed partner",default=lambda self: self._get_allow_partners())

    odoo_recipient_ids = fields.Many2many('res.partner', string='To (Partners)',
        context={'active_test': False})

    @api.depends('message_type')
    def _get_allow_partners(self):
        no_type = 'inbox'
        if self.message_type == 'email':
           no_type = 'email' 
        return [x.partner_id.id for x in self.env['res.users'].search([
            ('active','=',True),
            ('id','!=', self.env.user.id),
            ('notification_type','=',no_type)])]

    def _get_allow_partner(self):
        """
        read current login's partner
        """
        pp = self._get_allow_partners()
        for each in self:
            each.allow_partner_ids = [(6, 0, pp)]
    
    @api.model
    def _get_condition_fields(self):
        return self.env['fwiot_device'].get_condition_fields(self.env.context.get('device_id')) + \
               [('last-time','a device is not active for ')] 

    def action_test(self):
        """
        test send message from odoo bot
        """
        self.ensure_one()

        odoobot = self.env.ref('base.partner_root')
        self.message_post(body=self.message % 12.0, 
                          partner_ids=[self.env.user.partner_id.id],author_id=odoobot.id)

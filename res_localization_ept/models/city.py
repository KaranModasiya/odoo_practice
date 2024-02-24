from odoo import models, fields

class LocalizationCity(models.Model):

	_name = 'res.city.ept'
	_description = 'Localization City Demo'

	name = fields.Char(string="Name", help="Name of the city")
	state_id = fields.Many2one(comodel_name='res.state.ept', string="State", help="State of the state")

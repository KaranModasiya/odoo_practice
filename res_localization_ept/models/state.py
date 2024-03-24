from odoo import models, fields, api
from odoo.exceptions import ValidationError

class LocalizationState(models.Model):

	_name = 'res.state.ept'
	_description = 'Localization State Demo'
	_rec_names_search = ['name', 'code']

	name = fields.Char(string="Name", help="Name of the state")
	code = fields.Char(string="Short Code", help="Short code of the state")
	country_id = fields.Many2one(comodel_name='res.country.ept', string="Country", help="Country of the state")
	city_ids = fields.One2many(comodel_name='res.city.ept', inverse_name='state_id', string="Cities", help="Cities of the state")

	@api.constrains('code')
	def check_code(self):
		if self.search([('id', '!=', self.id), ('code', '=', self.code)]):
			raise ValidationError('State code must be unique!')


	def _compute_display_name(self):
		for rec in self:
			rec.display_name = f"{rec.name} - {rec.code}"

from odoo import models, fields

class LocalizationCountry(models.Model):

	_name = 'res.country.ept'
	_description = 'Localization Country Demo'

	name = fields.Char(string="Name", help="Name of the country")
	code = fields.Char(string="Countery Code", help="Countery code of the country")
	state_ids = fields.One2many(comodel_name='res.state.ept', inverse_name='country_id', string="States", help="States code of the country")

	_sql_constraints = [
		('unique_country_code', 'unique(code)', 'The country code must be unique!'),
		]
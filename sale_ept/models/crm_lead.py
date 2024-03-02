from odoo import fields, models, api
from odoo.exceptions import ValidationError
from odoo.fields import Command

class CrmLead(models.Model):

	_name = 'crm.lead.ept'
	_description = 'CRM Leads'

	name = fields.Char(string="Id", help="Lead number", readonly=True, default='New')
	partner_id = fields.Many2one(comodel_name="res.partner.ept", string="Customer", help="Select customer")
	order_ids = fields.One2many(comodel_name="sale.order.ept", inverse_name="lead_id", string="Orderlist", help="Order list of the customer")
	team_id = fields.Many2one(comodel_name="crm.team.ept", string="CRM Team", help="CRM team of the lead")
	user_id = fields.Many2one(comodel_name="res.users", string="Saleperson", help="Saleperson of the lead")
	lead_line_ids = fields.One2many(comodel_name="crm.lead.line.ept", inverse_name="lead_id", string="Orderlist", help="Order list of the customer")
	state = fields.Selection(selection=[
		('New', 'New'),
		('Qualified', 'Qualified'),
		('Proposition', 'Proposition'),
		('Won', 'Won'),
		('Lost', 'Lost')], string="State", help="State of the lead", default="New")
	won_date = fields.Date(string="Won Date", help="Won date of the lead")
	lost_reason = fields.Text(string="Lost Reason", help="Lost reason of the lead")
	next_followup_date = fields.Date(string="Next Followup", help="Next follow-up date of the lead")
	partner_name = fields.Char(string="Customer Name", help="Name of the cusotmer")
	partner_email = fields.Char(string="Customer Email", help="Email of the cusotmer")
	partner_phone = fields.Char(string="Customer Phone No.", help="Phone number of the cusotmer")
	partner_country_id = fields.Many2one(comodel_name="res.country.ept", string="Country", help="Country of the cusotmer")
	partner_state_id = fields.Many2one(comodel_name="res.state.ept", string="State", help="State of the cusotmer")
	partner_city_id = fields.Many2one(comodel_name="res.city.ept", string="City", help="City of the cusotmer")


	@api.model
	def create(self, vals):
		vals['name'] = self.env['ir.sequence'].next_by_code('crm.lead.ept')
		return super(CrmLead, self).create(vals)

	def action_qualify_button(self):
		self.state = 'Qualified'

	def action_proposition_button(self):
		self.state = 'Proposition'

	def action_won_button(self):
		if self.lead_line_ids:
			self.state = 'Won'
			self.won_date = fields.Date.today()
		else:
			raise ValidationError('Please add some products to change state to Won.')

	def action_lost_button(self):
		self.state = 'Lost'

	def action_generate_sales_quotation_button(self):
		"""
		Generates sales order record and converts lead lines to order lines.
		:return: None
		"""
		if self.partner_id:
			orderline = []
			for line in self.lead_line_ids:
				orderline.append(Command.create({
					'product_id': line.product_id.id,
					'name': line.name,
					'quantity': line.expected_sell_qty,
					'unit_price': line.product_id.sale_price,
					'uom_id': line.uom_id.id,
					'tax_ids': line.product_id.tax_ids.ids,
					}))

			saleorder = self.env['sale.order.ept'].new({'partner_id': self.partner_id.id})
			saleorder.onchange_partner_id()

			self.env['sale.order.ept'].create({
				'partner_id': self.partner_id.id,
				'partner_shipping_id': saleorder.partner_shipping_id.id,
				'partner_invoice_id':  saleorder.partner_invoice_id.id,
				'order_date':fields.Date.today(),
				'saleperson_id': self.user_id.id,
				'state': 'Draft',
				'lead_id': self.id,
				'order_line_ids': orderline})
		else:
			raise ValidationError('Please select or create new customer.')


	def action_generate_new_customer_button(self):
		"""
		Create new record of partner.
		:return: None
		"""
		self.partner_id = self.env['res.partner.ept'].create({
			'name': self.partner_name,
			'email': self.partner_email,
			'mobile': self.partner_phone,
			'city': self.partner_city_id.id,
			'state': self.partner_state_id.id,
			'country': self.partner_country_id.id,
			})


from odoo import api, models, fields
from odoo.fields import Command

class CrmLrad(models.Model):
	_inherit = 'crm.lead'

	# REQUIREMENT 15 ----------------------------------------------------------------------
	@api.model
	def action_new_quotation(self):
		action = super(CrmLrad, self).action_new_quotation()
		action['context']['default_crm_lead_ept_id'] = self.id
		action['context']['default_tag_ids'].append(self.env.ref('sale_extended.custom_tag').id)
		return action


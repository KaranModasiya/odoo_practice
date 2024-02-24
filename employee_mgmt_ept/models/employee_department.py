from odoo import models, fields

class EmployeeDepartment(models.Model):

	_name = 'employee.department.ept'
	_description = 'Departments'

	name = fields.Char(string="Department Name", help="Department name of the employee", required=True)
	department_manager_id = fields.Many2one(comodel_name="res.users", string="Department Manager", help="Name of the department manager",)
	employee_ids = fields.One2many(comodel_name="employee.ept", inverse_name="department_name_id", string="Employees", help="Employee list of this department",)

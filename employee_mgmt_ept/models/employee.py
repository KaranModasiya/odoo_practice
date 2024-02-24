from odoo import models, fields

class Employee(models.Model):

	_name = 'employee.ept'
	_description = 'Employee'

	name = fields.Char(string="Employee Name", help="Name of the Employee", required=True)
	department_name_id = fields.Many2one(comodel_name="employee.department.ept", string="Department Name", help="Department of the Employee", required=True)
	shift_id = fields.Many2one(comodel_name="employee.department.shift.ept", string="Shift", help="Shift of the Employee", required=True)
	job_position = fields.Char(string="Job Position", help="Job position of the Employee")
	salary = fields.Float(string="Salary", help="Salary of the Employee", digits=(6, 2))
	hire_date = fields.Date(string="Hire Date", help="Hire date of the Employee")
	gender = fields.Selection(selection=[('Male', 'Male'), ('Female', 'Female'), ('Transgender', 'Transgender')], string="Gender", help="Gender of the Employee")
	job_type = fields.Selection(selection=[('Permanent', 'Permanent'), ('Ad Hoc', 'Ad Hoc')], string="Job Type", help="Job type of the Employee")
	is_manager = fields.Boolean(string="Is Manager?", help="Select whether the employee is manager or not?")
	manager_id = fields.Many2one(comodel_name="employee.ept", string="Manager", help="Manager of the employee")
	related_user_id = fields.Many2one(comodel_name="res.users", string="Related User", help="Related user of the Employee")
	employee_ids = fields.One2many(comodel_name="employee.ept", inverse_name="manager_id", string="Is Manager?", help="Select whether the employee is manager or not?")
	increment_percentage = fields.Float(string="Increment Percentage", help="Increment percentage of the Employee", digits=(2, 2))

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class GetPoFile(models.Model):
    _name = 'vpo_files'
    _description = 'Purchase Order Files'

    name = fields.Char(string='File Name')
    file_data = fields.Binary(string='File Data')
    file_type = fields.Selection([('excel', 'Excel')],
                                 string='File Type', default='excel')
    parent_id = fields.Many2one('get_vpo_mas', string='Parent PO', invisible='True')

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

# Header table
class SizeRange(models.Model):
    _name = "size_mapping_main"
    _rec_name = 'Size_Range'

    Size_Range = fields.Many2one('size_range_master', string='Size Range')
    Size_Range_uniq = fields.Char(string='Size Range', compute='_compute_size_range_uniq', store=True)
    Size_Range_01 = fields.Many2one(string='Size Range', related='size_lines.Size_Range')
    size_lines = fields.One2many('size_mapping_lines', 'size_main', string="Size Range")

    CustomerID = fields.Char(string='CUSTOMER ID', compute='_compute_c_id', store=True)

    @api.depends('Size_Range')
    def _compute_c_id(self):
        for record in self:
            record.CustomerID = record.Size_Range.customer_id if record.Size_Range else ''

    @api.depends('Size_Range')
    def _compute_size_range_uniq(self):
        for record in self:
            record.Size_Range_uniq = record.Size_Range.id if record.Size_Range else False

    _sql_constraints = [
        ('unique_size_in_range', 'UNIQUE(Size_Range_uniq)', 'Size Map for this Size Range already exists.'),
    ]

    @api.constrains('Size_Range_uniq')
    def _check_unique_size_in_range(self):
        for record in self:
            if record.Size_Range_uniq:
                size_map = self.search([
                    ('Size_Range_uniq', '=', record.Size_Range_uniq),
                    ('id', '!=', record.id),  # Exclude the current record from the search
                ])
                if size_map:
                    raise ValidationError(_("Size Map for this Size Range already exists."))

class SizeRangeline(models.Model):
    _name = "size_mapping_lines"
    _rec_name = 'Size_Range'

    size_main = fields.Many2one('size_mapping_main', string="Size Range")
    Size_Range = fields.Many2one(string='Size Range', related='size_main.Size_Range')
    Size = fields.Char(string='Size')
    Size_LV = fields.Char(string='Size Lv')

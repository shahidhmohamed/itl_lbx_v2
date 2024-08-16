from odoo import models, fields, api

class GetVpoLines(models.Model):
    _name = 'get_vpo_mas_lines'
    _description = 'Purchase Order Lines'

    header_table = fields.Many2one('get_vpo_mas', string='Purchase Order Reference')
    
    # Fields from PurchaseOrder
    po_number = fields.Char(string='PO Number', related='header_table.po_number', store=True)
    file_number = fields.Char(string='File Number')
    style = fields.Char(string='Style')
    cc = fields.Char(string='CC')
    size = fields.Char(string='Size')
    size_lv = fields.Char(string='Size Lv', compute='_compute_size_lv', store=True)
    retail_usd = fields.Char(string='Retail (USD)')
    retail_cad = fields.Char(string='Retail (CAD)')
    retail_gbp = fields.Char(string='Retail (GBP)')
    sku = fields.Char(string='SKU')
    desc = fields.Char(string='Description')
    article = fields.Char(string='Article')
    qty = fields.Char(string='Quantity')

    @api.depends('size')
    def _compute_size_lv(self):
        for record in self:
            size_master = self.env['size_master'].search([('size_id', '=', record.size)], limit=1)
            if size_master:
                record.size_lv = size_master.size
            else:
                record.size_lv = False

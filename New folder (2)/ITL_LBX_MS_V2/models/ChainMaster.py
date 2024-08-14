from odoo import models, fields, api, _

class SubChain(models.Model):
    _name = "chain_master"
    _description = "Submaster Chain Details"
    _rec_name = 'ChainName'

    ChainId = fields.Char(string='Chain Id')
    ChainName = fields.Char(string='Chain Name')
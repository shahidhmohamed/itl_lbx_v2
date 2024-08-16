from odoo import models, fields, api, _


class LbxMiCollectionmaster(models.Model):
    _name = "collection_master"
    _description = "COLLECTION MASTER"
    _rec_name = 'Collection'


    Collection = fields.Char (string = 'Collection')
    Collection_name = fields.Char (string = 'Collection Name')
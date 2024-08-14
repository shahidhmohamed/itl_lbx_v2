from odoo import models, fields, api, _

class RfidResponseWizard(models.TransientModel):
    _name = 'rfid.response.wizard'
    _description = 'RFID Response Wizard'

    response_content = fields.Text("Response Content", readonly=True)

    def action_close(self):
        return {'type': 'ir.actions.act_window_close'}
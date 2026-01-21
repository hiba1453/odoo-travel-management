from odoo import models, fields, api
from odoo.exceptions import ValidationError

class DeplacementRejetWizard(models.TransientModel):
    _name = 'gestion.deplacement.rejet.wizard'
    _description = 'Wizard pour le rejet de déplacement'

    deplacement_id = fields.Many2one('gestion.deplacement', string='Déplacement', required=True)
    motif_rejet = fields.Text(string='Motif de rejet', required=True)

    def action_confirm_rejet(self):
        """Confirmer le rejet avec le motif"""
        self.ensure_one()
        if not self.motif_rejet:
            raise ValidationError("Le motif de rejet est obligatoire.")
        self.deplacement_id.action_rejeter_confirm(self.motif_rejet)
        return {'type': 'ir.actions.act_window_close'}


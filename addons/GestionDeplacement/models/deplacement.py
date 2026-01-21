from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Deplacement(models.Model):
    _name = 'gestion.deplacement'
    _description = 'Demande de déplacement'

    employee_id = fields.Many2one('hr.employee', string='Employé', required=True, readonly=True, default=lambda self: self._default_employee_id())
    manager_id = fields.Many2one('hr.employee', string='Manager', related='employee_id.parent_id', store=True, readonly=True)
    objet_mission = fields.Char(string="Objet de la mission", required=True)
    ordre_mission = fields.Binary(string="Ordre de mission")
    ordre_mission_filename = fields.Char(string="Nom du fichier")
    date_debut = fields.Date(string="Date de début", required=True)
    date_fin = fields.Date(string="Date de fin", required=True)
    pays_id = fields.Many2one('res.country', string="Pays", required=True)
    ville_id = fields.Many2one('gestion.ville', string="Ville", required=True, domain="[('country_id', '=', pays_id)]")
    motif_rejet = fields.Text(string="Motif de rejet", readonly=True)
    distance_km = fields.Float(string="Distance (Km)", required=True)
    mode_transport = fields.Selection([
        ('train', 'Train'),
        ('autocar', 'Autocar'),
        ('avion', 'Avion'),
        ('vehicule_service', 'Véhicule de service')
    ], string="Mode de transport", required=True)
    vehicule_id = fields.Many2one('fleet.vehicle', string="Véhicule de service")
    classe = fields.Selection([
        ('eco', 'Économique'),
        ('business', 'Business')
    ], string="Classe (si avion)", compute="_compute_classe", store=True, readonly=True)
    montant_frais = fields.Float(string="Montant des frais", compute="_compute_montant", store=True, readonly=True)
    type_deplacement = fields.Selection([
        ('national', 'National'),
        ('international', 'International')
    ], string="Type de déplacement", compute="_compute_type_deplacement", store=True, readonly=True)

    state = fields.Selection([
        ('brouillon', 'Brouillon'),
        ('attente_validation', 'En attente de validation'),
        ('valide', 'Validé'),
        ('rejete', 'Rejeté')
    ], string="État", default='brouillon', readonly=True)
    
    is_current_user_manager = fields.Boolean(string="Est le manager", compute="_compute_is_current_user_manager", store=False)

    def _default_employee_id(self):
        """Remplir automatiquement l'employé depuis l'utilisateur connecté"""
        employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
        return employee.id if employee else False

    @api.depends('manager_id')
    def _compute_is_current_user_manager(self):
        """Vérifier si l'utilisateur connecté est le manager"""
        for rec in self:
            if rec.manager_id:
                current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
                rec.is_current_user_manager = current_employee and current_employee.id == rec.manager_id.id
            else:
                rec.is_current_user_manager = False

    @api.onchange('pays_id')
    def _onchange_pays_id(self):
        """Réinitialiser la ville lorsque le pays change"""
        if self.pays_id:
            self.ville_id = False

    @api.depends('pays_id')
    def _compute_type_deplacement(self):
        """Calculer automatiquement le type de déplacement selon le pays"""
        for rec in self:
            if rec.pays_id:
                # Comparer avec le pays de l'entreprise
                company_country = self.env.company.country_id
                if company_country and rec.pays_id.id == company_country.id:
                    rec.type_deplacement = 'national'
                else:
                    rec.type_deplacement = 'international'
            else:
                rec.type_deplacement = False

    @api.depends('distance_km', 'mode_transport')
    def _compute_classe(self):
        for rec in self:
            if rec.mode_transport == 'avion':
                if rec.distance_km >= 6000:
                    rec.classe = 'business'
                elif rec.distance_km >= 500:
                    rec.classe = 'eco'
                else:
                    rec.classe = False
            else:
                rec.classe = False

    @api.depends('date_debut', 'date_fin', 'type_deplacement')
    def _compute_montant(self):
        for rec in self:
            if rec.date_debut and rec.date_fin:
                nb_jours = (rec.date_fin - rec.date_debut).days + 1
                if rec.type_deplacement == 'national':
                    rec.montant_frais = nb_jours * 700
                elif rec.type_deplacement == 'international':
                    rec.montant_frais = nb_jours * 1500
                else:
                    rec.montant_frais = 0

    @api.constrains('date_debut', 'date_fin')
    def _check_dates(self):
        for rec in self:
            if rec.date_debut and rec.date_fin:
                if rec.date_fin < rec.date_debut:
                    raise ValidationError("La date de fin doit être supérieure ou égale à la date de début.")

    @api.constrains('mode_transport', 'distance_km')
    def _check_avion_distance(self):
        for rec in self:
            if rec.mode_transport == 'avion' and rec.distance_km < 500:
                raise ValidationError("Les avions ne sont autorisés que pour les distances supérieures ou égales à 500 km.")

    @api.constrains('mode_transport', 'vehicule_id')
    def _check_vehicule_required(self):
        for rec in self:
            if rec.mode_transport == 'vehicule_service' and not rec.vehicule_id:
                raise ValidationError("Le véhicule est obligatoire lorsque le mode de transport est 'Véhicule de service'.")

    def write(self, vals):
        """Empêcher le manager de modifier les demandes"""
        for rec in self:
            # Vérifier si l'utilisateur connecté est le manager
            current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
            if current_employee and rec.manager_id and current_employee.id == rec.manager_id.id:
                # Le manager ne peut modifier que l'état via les actions spécifiques
                # Autoriser uniquement si c'est juste un changement d'état via les méthodes d'action
                allowed_fields = {'state', 'motif_rejet'}
                if not allowed_fields.issuperset(vals.keys()):
                    # Si on essaie de modifier d'autres champs que l'état ou le motif de rejet
                    raise ValidationError("Le manager n'a pas le droit de modifier les demandes de déplacement.")
        return super().write(vals)

    def action_soumettre_validation(self):
        """Soumettre la demande à validation"""
        for rec in self:
            if rec.state != 'brouillon':
                raise ValidationError("Seules les demandes en brouillon peuvent être soumises à validation.")
            if not rec.manager_id:
                raise ValidationError("L'employé doit avoir un manager assigné pour soumettre la demande.")
            rec.state = 'attente_validation'
        return True

    def action_valider(self):
        """Valider la demande par le manager"""
        for rec in self:
            if rec.state != 'attente_validation':
                raise ValidationError("Seules les demandes en attente de validation peuvent être validées.")
            # Vérifier que l'utilisateur connecté est le manager
            current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
            if not current_employee or current_employee.id != rec.manager_id.id:
                raise ValidationError("Seul le manager de l'employé peut valider cette demande.")
            rec.state = 'valide'
        return True

    def action_rejeter(self):
        """Rejeter la demande - ouvre un wizard pour saisir le motif"""
        return {
            'name': 'Motif de rejet',
            'type': 'ir.actions.act_window',
            'res_model': 'gestion.deplacement.rejet.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_deplacement_id': self.id},
        }
    
    def action_rejeter_confirm(self, motif):
        """Confirmer le rejet avec le motif"""
        for rec in self:
            if rec.state != 'attente_validation':
                raise ValidationError("Seules les demandes en attente de validation peuvent être rejetées.")
            # Vérifier que l'utilisateur connecté est le manager
            current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
            if not current_employee or current_employee.id != rec.manager_id.id:
                raise ValidationError("Seul le manager de l'employé peut rejeter cette demande.")
            if not motif:
                raise ValidationError("Le motif de rejet est obligatoire.")
            rec.motif_rejet = motif
            rec.state = 'rejete'
        return True

    def action_reset_to_draft(self):
        """Remettre en brouillon"""
        for rec in self:
            rec.state = 'brouillon'
        return True

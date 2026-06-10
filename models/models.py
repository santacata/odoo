from odoo import models, fields, api, SUPERUSER_ID
from datetime import date

class Club(models.Model):
    _name = 'natacio.club'
    _description = 'Club'

    name = fields.Char()
    poble = fields.Char()
    num_socis = fields.Integer()
    nadadors_ids = fields.One2many('natacio.nadador', 'club_id', string="Nadadors")

class Categoria(models.Model):
    _name = 'natacio.categoria'
    _description = 'Categoria'

    name = fields.Char()
    edat_minima = fields.Integer()
    edat_maxima = fields.Integer()
    nadadors_ids = fields.One2many('natacio.nadador', 'categoria_id', string="Nadadors")

class Nadador(models.Model):
    _name = 'natacio.nadador'
    _inherit = 'res.partner'
    _description = 'Nadador'

    commercial_partner_id = fields.Many2one(
        'natacio.nadador', string='Commercial Entity',
        compute='_compute_commercial_partner', store=True,
        recursive=True, index=True
    )

    @api.depends('company_name', 'parent_id.is_company', 'commercial_partner_id.name')
    def _compute_commercial_partner(self):
        for partner in self:
            if partner.is_company or not partner.parent_id:
                partner.commercial_partner_id = partner
            else:
                commercial = partner.parent_id.commercial_partner_id
                if commercial and commercial._name != 'natacio.nadador':
                    commercial = self.browse(commercial.id)
                partner.commercial_partner_id = commercial

    @api.depends('user_ids.share', 'user_ids.active')
    def _compute_partner_share(self):
        super_partner = self.env['res.users'].browse(SUPERUSER_ID).partner_id
        if super_partner and super_partner._name != 'natacio.nadador':
            super_partner = self.browse(super_partner.id)
        for partner in self:
            if partner == super_partner:
                partner.partner_share = False
            else:
                partner.partner_share = not partner.user_ids or not any(not user.share for user in partner.user_ids)

    any_naixement = fields.Integer()
    edat = fields.Integer(compute='_compute_edat', store=True)

    categoria_id = fields.Many2one('natacio.categoria')
    club_id = fields.Many2one('natacio.club')

    temps_crol = fields.Float()
    temps_esquena = fields.Float()
    temps_brasa = fields.Float()
    temps_papallona = fields.Float()
    nivel = fields.Float()

    foto = fields.Binary()

    data_ultim_pagament = fields.Date()
    progres_pagament = fields.Float(
        compute='_compute_progres_pagament',
        store=True
    )

    es_nadador = fields.Boolean(default=True)

    @api.depends('any_naixement')
    def _compute_edat(self):
        for rec in self:
            rec.edat = date.today().year - rec.any_naixement if rec.any_naixement else 0

    @api.depends('data_ultim_pagament')
    def _compute_progres_pagament(self):
        for rec in self:
            if rec.data_ultim_pagament:
                dies_passats = (date.today() - rec.data_ultim_pagament).days
                rec.progres_pagament = min(100, max(0, (dies_passats / 365.0) * 100))
            else:
                rec.progres_pagament = 0

    def registrar_pagament(self):
        for rec in self:
            rec.data_ultim_pagament = date.today()

class Estil(models.Model):
    _name = 'natacio.estil'
    _description = 'Estil'

    name = fields.Char()
    millors_nadadors_ids = fields.Many2many('natacio.nadador', string="Millors Nadadors")


class Campionat(models.Model):
    _name = 'natacio.campionat'
    _description = 'Campionat'

    name = fields.Char()
    club_ids = fields.Many2many('natacio.club')
    data_inici = fields.Date()
    data_fi = fields.Date()
    nadadors_inscrits_ids = fields.Many2many('natacio.nadador', string="Nadadors Inscrits")
    sessio_ids = fields.One2many('natacio.sessio', 'campionat_id', string="Sessions")


class Sessio(models.Model):
    _name = 'natacio.sessio'
    _description = 'Sessio'

    data = fields.Date()
    campionat_id = fields.Many2one('natacio.campionat')
    prova_ids = fields.One2many('natacio.prova', 'sessio_id', string="Proves")
    nadadors_ids = fields.Many2many('natacio.nadador', string="Inscrits")


class Prova(models.Model):
    _name = 'natacio.prova'
    _description = 'Prova'

    descripcio = fields.Char()
    estil_id = fields.Many2one('natacio.estil')
    categoria_id = fields.Many2one('natacio.categoria')
    sessio_id = fields.Many2one('natacio.sessio')
    nadadors_ids = fields.Many2many('natacio.nadador', string="Inscrits")
    series_data = fields.Text()
    resultats_data = fields.Text()


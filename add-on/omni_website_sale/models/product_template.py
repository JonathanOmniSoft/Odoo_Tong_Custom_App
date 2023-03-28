# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.addons.http_routing.models.ir_http import slug, unslug
from odoo.addons.website.models import ir_http
from odoo.tools.translate import html_translate
from odoo.osv import expression


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    ecomm_file_upload = fields.Boolean('Enable eCommerce File Upload', default=False)
    ecomm_file_upload_rules = fields.Selection([('optional','Upload Optional'), ('required','Upload Required')], string="File Upload Setting",
        help='Select the condition for uploading a file.', default='optional')



    def _get_website_file_upload_rules(self):
        if self.file_upload_rules == 'optional':
            return self.file_upload_rules
        return self.file_upload_rules





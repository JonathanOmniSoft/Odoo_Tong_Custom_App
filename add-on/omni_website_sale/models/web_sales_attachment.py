# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.addons.http_routing.models.ir_http import slug, unslug
from odoo.addons.website.models import ir_http
from odoo.tools.translate import html_translate
from odoo.osv import expression


class WebsiteAttachment(models.Model):

    _name = 'website.attachment'

    partner_id = fields.Many2one('res.partner', string='Partner ID')
    product_product_id = fields.Many2one('product.product', string='Product')
    product_template_id = fields.Many2one('product.template', related='product_product_id.product_tmpl_id', string='Product Template')
    # attachment_id = fields.Many2one('ir.attachment', string='Attachment')
    attachment_name = fields.Char(string='Attachment Name')
    attachment_url = fields.Char(string='Attachment URL')

    sale_order_line_id = fields.Many2one('sale.order.line', string='Sale Order Line', ondelete='cascade')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    website_attachment_ids = fields.One2many(comodel_name='website.attachment', inverse_name='sale_order_line_id', string='Web Sales Attachment', ondelete='set null')
    website_attachment_url = fields.Html(string='Website Attachment URL', compute='_compute_website_attachment_url')

    def _compute_website_attachment_url(self):
        self.website_attachment_url = ""
        for line in self:
            website_attachment_url = "<ul>"
            for website_attachment_id in line.website_attachment_ids:
                website_attachment_url += "<li><a href='" + website_attachment_id.attachment_url + "'>" + website_attachment_id.attachment_name + "</a></li>"
                print(f"line.attachment_url: {website_attachment_id.attachment_url}")
            website_attachment_url += "</ul>"

            line.website_attachment_url = website_attachment_url


    def _get_attachment_order_line(self):
        if self.website_attachment_ids:
            # return self.website_attachment_ids
            return "<b>I love you, you love me.</b>"

        return "Empty"



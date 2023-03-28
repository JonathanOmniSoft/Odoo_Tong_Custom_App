# -*- coding: utf-8 -*-
import re
import os
import json
import pickle
import requests
from datetime import datetime, timedelta, time

from google.oauth2.credentials import Credentials
from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow


from odoo.http import request
from odoo import fields, http, _
from odoo.tools.misc import get_lang
from odoo.addons.website.controllers.backend import WebsiteBackend
from odoo.addons.website_sale.controllers.main import WebsiteSale


# Commonly used MINE Types Dictionary
mine_types = {
    ".aac": "audio/aac", ".abw": "application/x-abiword", ".arc": "application/x-freearc", ".avi": "video/x-msvideo", ".azw": "application/vnd.amazon.ebook",
    ".bin": "application/octet-stream", ".bmp": "image/bmp", ".bz": "application/x-bzip", ".bz2": "application/x-bzip2",
    ".csh": "application/x-csh", ".css": "text/css",".csv": "text/csv",
    ".doc": "application/msword", ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".eot": "application/vnd.ms-fontobject", ".epub": "application/epub+zip",
    ".gz": "application/gzip", ".gif": "image/gif",
    ".htm": "text/html", ".html": "text/html",
    ".ico": "image/vnd.microsoft.icon", ".ics": "text/calendar",
    ".jar": "application/java-archive", ".jpeg": "image/jpeg", ".jpg": "image/jpeg", ".js": "text/javascript", ".json": "application/json", ".jsonld": "application/ld+json",
    ".mid": "audio/midi audio/x-midi", ".midi": "audio/midi audio/x-midi", ".mjs": "text/javascript", ".mp3": "audio/mpeg", ".mpeg": "video/mpeg", ".mpkg": "application/vnd.apple.installer+xml",
    ".odp": "application/vnd.oasis.opendocument.presentation", ".ods": "application/vnd.oasis.opendocument.spreadsheet", ".odt": "application/vnd.oasis.opendocument.text", ".oga": "audio/ogg", ".ogv": "video/ogg", ".ogx": "application/ogg", ".opus": "audio/opus", ".otf": "font/otf",
    ".png": "image/png", ".pdf": "application/pdf", ".php": "application/x-httpd-php", ".ppt": "application/vnd.ms-powerpoint", ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".rar": "application/vnd.rar", ".rtf": "application/rtf",
    ".sh": "application/x-sh", ".svg": "image/svg+xml", ".swf": "application/x-shockwave-flash", ".tar": "application/x-tar", ".tif": "image/tiff", ".tiff": "image/tiff",
    ".ts": "video/mp2t", ".ttf": "font/ttf", ".txt": "text/plain",
    ".vsd": "application/vnd.visio",
    ".wav": "audio/wav", ".weba": "audio/webm", ".webm": "video/webm", ".webp": "image/webp", ".woff": "font/woff", ".woff2": "font/woff2",
    ".xhtml": "application/xhtml+xml", ".xls": "application/vnd.ms-excel", ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", ".xml": "application/xml", ".xul": "application/vnd.mozilla.xul+xml",
    ".zip": "application/zip",
    ".3gp": "video/3gpp", ".3g2": "video/3gpp2",
    ".7z": "application/x-7z-compressed"
}


class WebsiteSaleBackend(WebsiteBackend):

    @http.route('/shop/upload_attachment/<model("product.template"):product>', type='http', auth="public", website=True)
    def omni_upload_files(self, product, **post):
        print("omni_upload_files controller")

        directory_path = os.path.join(os.path.expanduser('~'), 'grive')
        user = request.env.user.partner_id
        # Setup Google credentials
        client_secret_file = os.path.join(directory_path,  'omnisoft-solution.json')
        scopes = ['https://www.googleapis.com/auth/drive']
        google_folder_id = '1PuOXgSr1Z6NCqx5sFVxz2sxpIJvVd-q-'
        API_NAME = 'drive'
        API_VERSION = 'v3'

        credentials = service_account.Credentials.from_service_account_file(client_secret_file)
        scoped_credentials = credentials.with_scopes(scopes)
        service = build(API_NAME, API_VERSION, credentials=scoped_credentials)

        # Get the file from post request
        product_template = product
        product_product = ""

        if post.get('attachment', False):
            name = post.get('attachment').filename
            file = post.get('attachment')
            file_format = '.' + name.split('.')[-1]

            os.makedirs(directory_path, exist_ok=True)
            file.save(os.path.join(directory_path, name))

            print("post['attribute'] = ", post['attribute'])

            if post['attribute']:
                attribute = None
                if len(re.split('=', post['attribute'])) > 1:
                    attribute = re.split('=', post['attribute'])[1]
                product_product = request.env['product.product'].search(
                    [('product_tmpl_id', '=', product_template.id), ('combination_indices', '=', attribute)])

            # Upload to Google Drive
            google_file_metadata = {
                'name': name,
                'parents': [google_folder_id],
            }

            data = MediaFileUpload(os.path.join(directory_path, name), mimetype=mine_types[file_format], resumable=True)

            google_file = (service.files().create(
                body=google_file_metadata,
                media_body = data,
                fields='id'
            ).execute())

            # Create google share link
            sharable_link_response = service.files().get(fileId=google_file['id'], fields='webViewLink').execute()

            request.env['website.attachment'].sudo().create({
                'partner_id': user.id,
                # 'product_template_id': product_template.id,
                'product_product_id': product_product.id,
                'attachment_name': name,
                'attachment_url': sharable_link_response['webViewLink']
            })

            return json.dumps({'status': 'success'})
        else:
            print("No attachment found")
            return json.dumps({'status': 'error'})


class WebsiteSaleInherit(WebsiteSale):

    @http.route(['/shop/cart/update_json'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update_json(
            self, product_id, line_id=None, add_qty=None, set_qty=None, display=True, product_custom_attribute_values=None, no_variant_attribute_values=None, **kw):
        """
        This route is called :
            - When changing quantity from the cart.
            - When adding a product from the wishlist.
            - When adding a product to cart on the same page (without redirection).
        """

        res = super(WebsiteSaleInherit, self).cart_update_json(product_id=product_id, line_id=False, add_qty=add_qty, set_qty=set_qty, display=display,
            product_custom_attribute_values=product_custom_attribute_values, no_variant_attribute_values=no_variant_attribute_values, **kw)

        print(f"{request.env.user.partner_id=}")
        user_id = request.env.user.partner_id.id

        print(f"{kw=}")


        print(f"{line_id=}")
        print(f"{product_id=}")

        sales_order_line = request.env['sale.order.line'].sudo().search([('id', '=', res['line_id'])])
        print(f"{sales_order_line=}")
        sales_order_line.website_attachment_ids = request.env['website.attachment'].sudo().search([('partner_id', '=', user_id), ('product_product_id', '=', product_id)])

        return res
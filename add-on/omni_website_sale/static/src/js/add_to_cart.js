/** @odoo-module */

import ajax from 'web.ajax';
import { qweb } from "web.core";
import { WebsiteSale } from 'website_sale.website_sale';
import publicWidget from 'web.public.widget';
import VariantMixin from 'website_sale.VariantMixin';

const session = require('web.session');
const cartHandlerMixin = require ('website_sale.utils');


WebsiteSale.include({

    events: Object.assign({}, WebsiteSale.prototype.events, {
        'change #omni_attachments': '_onChangeOmniAttachments',
    }),

     /**
     * @private
     * @param {Event} ev
     */
    _onChangeOmniAttachments: function (ev) {
    },

    isEmptyObject: function( obj ) {
        for ( var name in obj ) {
            return false;
        }
        return true;
    },

    async _uploadFiles() {
        if ('website_sale_cart_quantity' in sessionStorage) {
            this.cartQty = sessionStorage.getItem('website_sale_cart_quantity');
        }
        if (this.el.querySelector('.my_cart_quantity').innerText != this.cartQty) {
            return this._rpc({route: "/shop/cart/quantity"}).then((cartQty) => {
                this.cartQty = cartQty;
                sessionStorage.setItem('website_sale_cart_quantity', this.cartQty);
            });
        }
    },

    /**
     * @override
    */
    _submitForm: async function() {

        var data = {};
        var omni_attachment_id = null;

        $.each($('#omni_attachments'), function (outer_index, input) {
            $.each($(input).prop('files'), function (index, file) {
                data.attachment = file;
            });
        });

        if (!($.isEmptyObject(data))) {
            var user = session.user_id;
            var attribute = window.location.href.substring(window.location.href.lastIndexOf('/') + 1);
            data.attribute = attribute;
            data.user = user;

            await ajax.post('/shop/upload_attachment/' + attribute, data).then(function (res)
            {
                omni_attachment_id = JSON.parse(res)["attachment_id"];
                alert("File uploaded successfully");
            }).guardedCatch(function (error) {
                console.log(error);
                alert("File upload failed");
            });
        }

        const params = this.rootProduct;

        const $product = $('#product_detail');
        const productTrackingInfo = $product.data('product-tracking-info');
        if (productTrackingInfo) {
            productTrackingInfo.quantity = params.quantity;
            $product.trigger('add_to_cart_event', [productTrackingInfo]);
        }

        params.add_qty = params.quantity;
        params.product_custom_attribute_values = JSON.stringify(params.product_custom_attribute_values);
        params.no_variant_attribute_values = JSON.stringify(params.no_variant_attribute_values);
        if (omni_attachment_id) {
            params.attachment_ids = JSON.stringify(omni_attachment_id);
        }
        delete params.quantity;
        return this.addToCart(params);
    },

});
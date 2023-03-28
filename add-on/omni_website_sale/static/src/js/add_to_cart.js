/** @odoo-module */

import { qweb } from "web.core";
import { WebsiteSale } from 'website_sale.website_sale';
import publicWidget from 'web.public.widget';
import VariantMixin from 'sale.VariantMixin';
import { cartHandlerMixin } from 'website_sale.utils';

const OmniWebsiteSaleWidget = publicWidget.registry.WebsiteSale;

// cartHandlerMixin = {
//     _addToCartInPage(params) {
//         console.log("cartHandlerMixin Added to cart");
//     },
// };

// WebsiteSale.include( {
//     events: _.extend({
//         'click #add_to_cart, .o_we_buy_now, #products_grid .o_wsale_product_btn .a-submit': 'async _onClickAdd',
//         },
//     ),
//
//     /**
//      * @override
//     */
//     _onClickAdd: function (ev) {
//         console.log("Added to cart");
//         return this._super.apply(this, arguments);
//     },
//
// });
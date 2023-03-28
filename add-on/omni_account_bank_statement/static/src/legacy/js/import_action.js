odoo.define('omni_account_bank_statement.import', function (require) {
"use strict";

    var core = require('web.core');
    var ImportStmt = require('bank_stmt_import_csv.import')
    var _t = core._t;
    var _lt = core._lt;

    // function dataFilteredQuery(q) {
    //     var suggestions = _.clone(this.data);
    //     if (q.term) {
    //         var exact = _.filter(suggestions, function (s) {
    //             return s.id === q.term || s.text === q.term;
    //         });
    //         if (exact.length) {
    //             suggestions = exact;
    //         } else {
    //             suggestions = [_make_option(q.term)].concat(_.filter(suggestions, function (s) {
    //                 return s.id.indexOf(q.term) !== -1 || s.text.indexOf(q.term) !== -1
    //             }));
    //         }
    //     }
    //     q.callback({results: suggestions});
    // }

    // var OmniBankImport = BaseImport.DataImport.extend({
    var OmniBankImport = ImportStmt.DataImportStmt.include({
        parse_opts_bank: [
            {name: 'oe_import_bank', label: _lt("Bank Separator:"), value: ''}
        ],

        init: function (parent, action) {
            this._super.apply(this, arguments);
            console.log("Init AiYourrBaba");
            console.log(action.params.model);
            console.log(action.params.context);

            self = this;
            var def = self._rpc({
                model: 'account.journal',
                method: 'search_read',
                fields: ['name', 'type'],
                context: self.context,
            }).then(function (result) {
                console.log(result);
            });

        },
        // start: function () {
        //     var self = this;
        //     this.setup_bank_picker();
        //
        //     console.log("Init AiYourrBaba");
        // },
        // create_model: function() {
        //     return Promise.resolve();
        // },
        // import_options: function () {
        //     var options = this._super();
        //     var self = this;
        //     _(this.parse_opts_bank).each(function (opt) {
        //         options[opt.name] = self.$('input.oe_import_' + opt.name).val();
        //     });
        //     console.log("fsdfsfds")
        //     return options;
        // },
        // setup_bank_picker: function () {
        //     console.log("AiYourrBaba333");
            // var data_bank = [
            //     {id: 'bca', text: _t("BCA")},
            //     {id: 'bmw', text: _t("BMW")},
            // ];
            // this.$('input.oe_import_bank').select2({
            //     width: '50%',
            //     data: data_bank,
            //     query: dataFilteredQuery,
            //     minimumResultsForSearch: -1,
            //     // this is not provided to initSelection so can't use this.data
            //     initSelection: function ($e, c) {
            //         c(_from_data(data, $e.val()) || _make_option($e.val()))
            //     }
            // })
        // },
        // onfile_loaded: function () {
        //     var self = this;
        //     if (this.first_load) {
        //         this.$('.oe_import_file_show').val(this.filename);
        //         this.$('.oe_import_file_reload').hide();
        //         this.first_load = false;
        //         self['settings_changed']();
        //     }
        //     else {
        //         this.$('.oe_import_file_reload').show();
        //         this._super();
        //     }
        // },
        // onpreview_success: function (event, from, to, result) {
        //     var options = this._super();
        //     _.each(['bank'], function (id) {
        //     self.$('.oe_import_' + id).select2('val', result.options[id])
        // });
        // },
    });


    // core.action_registry.add('omni_account_bank_statement', OmniBankImport);

    // return {
    //     OmniBankImport: OmniBankImport,
    // };
});

console.log("Alibaba");

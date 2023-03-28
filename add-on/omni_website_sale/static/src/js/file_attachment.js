odoo.define('@omni_website_sale/js/file_attachment', async function(require) {
    'use strict';

    console.log("Omni file_attachment JS running");
    const session = require('web.session');

    var publicWidget = require('web.public.widget');
    var core = require('web.core');
    var time = require('web.time');
    var ajax = require('web.ajax');
    var _t = core._t

    const $fileInput = $('#omni_attachments');

    $fileInput.on("change", async (e) => {
        console.log("file input changed");
        var data = {};
        var attachments = e.target.files;

        const files = document.querySelectorAll(".obj");

        for (let i = 0; i < files.length; i++) {
            new FileUpload(files[i], files[i].file);
            console.log(files[i].file);
        }

        $.each($fileInput, function (outer_index, input) {
            $.each($(input).prop('files'), function (index, file) {
                data.attachment = file;
            });
        });

        var user = session.user_id;
        var attribute = window.location.href.substring(window.location.href.lastIndexOf('/') + 1);
        data.attribute = attribute;
        data.user = user;


        await ajax.post('/shop/upload_attachment/' + attribute, data)
            .then(function (res) {
                alert("File uploaded successfully");
            }).guardedCatch(function (error) {
                console.log(error);
                alert("File upload failed");
            });




    });

});

odoo.define('bi_vendor_registration_request.VendorForm', function (require) {
'use strict';
    
    var publicWidget = require('web.public.widget');
    var ajax = require('web.ajax');

    publicWidget.registry.VendorForm = publicWidget.Widget.extend({
        selector: '.vendor_form',

        events: {
            'change input:radio[name=type]:checked': '_onChangeType',
            'change select#country_id': '_onChangeStateGet',
        },

        _onChangeType: function(ev){
            var type = $(ev.currentTarget).val();
            if(type === 'company'){
                $('.contact_details').removeClass('d-none');
                $('input[name="child_ids1"], input[name="child_ids2"], input[name="email_from1"], input[name="email_from2"]').prop("required", true);
            }
            else{
                $('input[name="child_ids1"], input[name="child_ids2"], input[name="email_from1"], input[name="email_from2"]').prop("required", false);
                $('.contact_details').addClass('d-none');
            }
        },

        _onChangeStateGet: function(ev) {
            if (!$("#country_id").val()) {
                return;
            }
            var state_id = $('.state_id').val();
            $('.state_id').val(state_id);
            ajax.jsonRpc('/my/state/'+ $("#country_id").val(), 'call', {
            }).then(function (data) {
                // placeholder phone_code
                // populate states and display
                var selectStates = $("select[name='state_id']");
                // dont reload state at first loading (done in qweb)
                if (selectStates.data('init')===0 || selectStates.find('option').length===1) {
                    if (data.states.length) {
                        selectStates.html('');
                        _.each(data.states, function (x) {
                            var opt = $('<option>').text(x[1])
                                .attr('value', x[0])
                                .attr('data-code', x[2]);
                            selectStates.append(opt);
                        });
                        selectStates.parent('div').show();
                    } else {
                        selectStates.val('').parent('div').hide();
                    }
                    selectStates.data('init', 0);
                }
               
                 else {
                    if (data.states.length) {
                        selectStates.html('');
                        _.each(data.states, function (x) {
                            var opt = $('<option>').text(x[1])
                                .attr('value', x[0])
                                .attr('data-code', x[2]);
                            selectStates.append(opt);
                        });
                        selectStates.parent('div').show();
                    } else {
                        selectStates.val('').parent('div').hide();
                    }
                    selectStates.data('init', 0);
                    $('.state_id').val(state_id);
                }
            });
        }

    });

});
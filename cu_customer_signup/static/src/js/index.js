odoo.define('auth_signup.signup', [
    'web.public.widget'
], function (require) {
    "use strict";

    const publicWidget = require('web.public.widget');

    publicWidget.registry.AuthSignup = publicWidget.Widget.extend({
        selector: '.oe_signup_form', // Attach to the signup form element
        events: {
            'click .next-button': '_onNextButtonClick',
            'click .prev-button': '_onPrevButtonClick',
        },
        start: function () {
            this.steps = this.$('.step');
            this.currentStepIndex = 0;
            this._showStep(this.currentStepIndex);
            return this._super.apply(this, arguments);
        },
        _onNextButtonClick: function (ev) {
            ev.preventDefault();
            if (this.currentStepIndex < this.steps.length - 1) {
                this.currentStepIndex++;
                this._showStep(this.currentStepIndex);
            }
        },
        _onPrevButtonClick: function (ev) {
            ev.preventDefault();
            if (this.currentStepIndex > 0) {
                this.currentStepIndex--;
                this._showStep(this.currentStepIndex);
            }
        },
        _showStep: function (index) {
            this.steps.addClass('d-none');
            this.steps.eq(index).removeClass('d-none');
        },
    });

});

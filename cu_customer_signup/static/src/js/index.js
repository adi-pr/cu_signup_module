
odoo.define('auth_signup.signup', [], function (require) {
    "use strict";

    document.addEventListener('DOMContentLoaded', () => {
        const steps = document.querySelectorAll('.step');
        const nextButtons = document.querySelectorAll('.next-button');
        const prevButtons = document.querySelectorAll('.prev-button');

        nextButtons.forEach((button) => {
            button.addEventListener('click', () => {
                const currentStep = document.querySelector(`#${button.dataset.next}-indicator`);
                const nextStep = document.querySelector(`#${button.dataset.next}`);
                steps.forEach((step) => step.classList.add('d-none'));
                nextStep.classList.remove('d-none');
            });
        });

        prevButtons.forEach((button) => {
            button.addEventListener('click', () => {
                const prevStep = document.querySelector(`#${button.dataset.prev}`);
                steps.forEach((step) => step.classList.add('d-none'));
                prevStep.classList.remove('d-none');
            });
        });
    });
});
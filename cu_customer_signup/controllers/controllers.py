# -*- coding: utf-8 -*-
import json
import logging
import werkzeug
from odoo import http, tools, _
from werkzeug.exceptions import Forbidden, NotFound
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.addons.web.controllers.home import ensure_db, Home, SIGN_UP_REQUEST_PARAMS, LOGIN_SUCCESSFUL_PARAMS
from odoo.exceptions import UserError
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.http import request

_logger = logging.getLogger(__name__)

LOGIN_SUCCESSFUL_PARAMS.add('account_created')

class CustomAuthSignup(AuthSignupHome):
    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()
        name = kw.get('name')
        last_name = kw.get('last_name')
        full_name = f"{name} {last_name}"
        email = kw.get('login')
        account_type = kw.get('account_type')
        mobile = kw.get('mobile')
        street1 = kw.get('street1')
        street2 = kw.get('street2')
        city = kw.get('city')
        password = kw.get('password')
        account_type = kw.get('account_type')
        pickup_location = kw.get('pickup_location')
        registration_method = kw.get('registration_method')
        dob = kw.get('dob')
        id_passport = kw.get('id_passport')
        source = kw.get('source')
        confirm_password = kw.get('confirm_password')
        country = kw.get('country')

        country_id = request.env['res.country'].sudo().search([('id', '=', country)], limit=1)

        countries = request.env['res.country'].search([])
        if countries:
            qcontext['countries'] = countries



        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()

        plan_id = request.env['sale.subscription.plan'].sudo().search([('name', '=', 'Monthly')], limit=1)

        if account_type == 'Zoon+':
            sub_product = request.env['product.product'].sudo().search([('recurring_invoice', '=', True)], limit=1)
            if sub_product:
                partner = request.env['res.partner'].sudo().create({
                    'name': full_name,
                    'x_studio_email': email,
                    'mobile': mobile,
                    'phone': mobile,
                    'street': street1,
                    'street2': street2,
                    'city': city,
                    'country_id': country_id.id,
                    'customer_rank': 1,
                    'x_studio_account_type': account_type,
                    'x_studio_preferred_pickup_location': pickup_location,
                    'x_studio_registration_method': registration_method,
                    'x_studio_dob': dob,
                    'x_studio_idpassport': id_passport,
                    'x_studio_how_did_you_find_out_about_us': source,
                })

                existing_user = request.env['res.users'].sudo().search([('login', '=', email)], limit=1)
                if existing_user:
                    return json.dumps({'status': 'error', 'message': 'User with this email already exists.'})

                # Create user
                user_vals = {
                    'name': full_name,
                    'login': email,
                    'partner_id': partner.id,
                    'groups_id': [(6, 0, [request.env.ref('base.group_portal').id])],
                }
                # Set the user's password securely
                user = request.env['res.users'].sudo().create(user_vals)
                user.sudo().write({'password': password})

                sale_order = request.website.sale_get_order(force_create=True)
                sale_order.sudo().write({
                    'plan_id': plan_id.id,
                    'partner_id': partner.id,
                })
                request.env['sale.order.line'].sudo().create({
                    'order_id': sale_order.id,
                    'product_id': sub_product.id,
                    'product_uom_qty': 1,
                    'price_unit': sub_product.lst_price,
                })
                _logger.info("Redirecting to cart")

                # Redirect to cart
                return request.redirect('/shop/cart')

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                # Perform signup
                self.do_signup(qcontext)

                # Update or create partner
                partner = request.env['res.partner'].sudo().search([('email', '=', email)], limit=1)

                if not partner:
                    partner = request.env['res.partner'].sudo().create({
                        'name': full_name,
                        'x_studio_email': email,
                        'mobile': mobile,
                        'street': street1,
                        'street2': street2,
                        'city': city,
                        'country_id': country_id.id,
                        'customer_rank': 1,
                    })
                else:
                    partner.sudo().write({
                        'mobile': mobile,
                        'street': street1,
                        'street2': street2,
                        'city': city,
                        'x_studio_email': email,
                        'country_id': country_id.id,
                        'customer_rank': 1,
                        'x_studio_account_type': account_type,
                        'x_studio_preferred_pickup_location': pickup_location,
                        'x_studio_registration_method': registration_method,
                        'x_studio_dob': dob,
                        'x_studio_idpassport': id_passport,
                        'x_studio_how_did_you_find_out_about_us': source,
                    })

                # Send account creation email
                template = request.env.ref('auth_signup.mail_template_user_signup_account_created',
                                           raise_if_not_found=False)
                user_sudo = request.env['res.users'].sudo().search(
                    [('login', '=', qcontext.get('login'))], limit=1
                )
                if user_sudo and template:
                    template.sudo().send_mail(user_sudo.id, force_send=True)

                # Log the user in
                return self.web_login(*args, **kw)

            except UserError as e:
                qcontext['error'] = e.args[0]
            except (SignupError, AssertionError) as e:
                if request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))]):
                    qcontext["error"] = _("Another user is already registered using this email address.")
                else:
                    _logger.warning("%s", e)
                    qcontext['error'] = _("Could not create a new account.") + "\n" + str(e)

        response = request.render('auth_signup.signup', qcontext)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"

        return response
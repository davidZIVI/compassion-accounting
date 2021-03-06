﻿# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Compassion CH (http://www.compassion.ch)
#    Releasing children from poverty in Jesus' name
#    @author: Cyril Sester <csester@compassion.ch>
#
#    The licence is in the file __openerp__.py
#
##############################################################################

from openerp.osv import orm, fields
from openerp.tools.translate import _


class recurring_invoicer_wizard(orm.TransientModel):

    ''' This wizard generate invoices from contract groups when launched.
    By default, all contract groups are used.
    '''
    _name = 'recurring.invoicer.wizard'

    _columns = {
        'invoice_ids': fields.one2many(
            'account.invoice', 'recurring_invoicer_id',
            _('Generated invoices'), readonly=True),
        'generation_date': fields.date(_('Generation date'), readonly=True),
    }

    def generate(self, cr, uid, ids, context=None):
        contract_group_obj = self.pool.get('recurring.contract.group')
        recurring_invoicer_obj = self.pool.get('recurring.invoicer')
        invoicer_id = recurring_invoicer_obj.create(cr, uid, {}, context)

        contract_group_obj.generate_invoices(cr, uid, [], invoicer_id, context)

        # If no invoice in invoicer, we raise and exception.
        # This will cancel the invoicer creation too !
        recurring_invoicer = recurring_invoicer_obj.browse(cr, uid,
                                                           invoicer_id,
                                                           context)
        if not recurring_invoicer.invoice_ids:
            raise orm.except_orm('ZeroGenerationError',
                                 _('0 invoices have been generated.'))

        return {
            'name': 'recurring.invoicer.form',
            'view_mode': 'form',
            'view_type': 'form,tree',
            'res_id': invoicer_id,  # id of the object to which to redirect
            'res_model': 'recurring.invoicer',  # object name
            'type': 'ir.actions.act_window',
        }

    def generate_from_cron(self, cr, uid, context=None):
        self.generate(cr, uid, [], context=context)

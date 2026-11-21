/*
 * Case EDI-001 · Northbridge Health — source records (unchanged from v0.3.2).
 * All organizations, identifiers, addresses, and contacts are fictional.
 *
 * v0.4.0 (decision P2-6): the "note" values were rewritten as neutral investigative
 * information. v0.3.2's notes revealed the expected answers (e.g. "Same legal entity as
 * CRM-10489"). Evidence the learner needs is kept: the ERP address is identified as a
 * remittance (billing) address, the rebate record lacks tax and legal-name evidence, and
 * the partner-referral account lists no parent company.
 */
(function (A) {
  'use strict';
  A.registerModule('data/records', ['namespace']);

  A.data.records = [
    { id: 'CRM-10452', name: 'Northbridge Health', system: 'CRM', status: 'Active', tax: '91-4826103',
      address: '100 Medical Parkway, Seattle, WA', legal: 'Northbridge Health Inc.', parent: 'Northbridge Holdings',
      contact: 'operations@northbridge.example', verified: '2026-10-14',
      note: 'Account record maintained by the regional sales team. Address confirmed during an October 2026 site visit.' },
    { id: 'ERP-77831', name: 'Northbridge Health Inc.', system: 'ERP', status: 'Active', tax: '91-4826103',
      address: '400 Billing Plaza, Seattle, WA', legal: 'Northbridge Health Inc.', parent: 'Northbridge Holdings',
      contact: 'ap@northbridge.example', verified: '2026-10-22',
      note: 'Customer master used for invoicing. Address on file is the accounts-payable remittance address.' },
    { id: 'REB-33907', name: 'Northbridge Healthcare', system: 'Rebates', status: 'Pending', tax: '',
      address: '100 Medical Pkwy, Seattle, WA', legal: '', parent: 'Northbridge Holdings',
      contact: 'rebates@northbridge.example', verified: '2026-09-02',
      note: 'Rebate enrollment submitted without a W-9. Tax identifier and legal name not yet provided.' },
    { id: 'CRM-10489', name: 'Northbridge Medical Group', system: 'CRM', status: 'Active', tax: '91-7728041',
      address: '20 Clinic Way, Tacoma, WA', legal: 'Northbridge Medical Group LLC', parent: 'Northbridge Holdings',
      contact: 'office@nbmedical.example', verified: '2026-10-18',
      note: 'Clinic network account opened for the Tacoma location. Contracts are signed under its LLC name.' },
    { id: 'ERP-77902', name: 'Northbridge Medical Group LLC', system: 'ERP', status: 'Active', tax: '91-7728041',
      address: '20 Clinic Way, Tacoma, WA', legal: 'Northbridge Medical Group LLC', parent: 'Northbridge Holdings',
      contact: 'billing@nbmedical.example', verified: '2026-10-20',
      note: 'Customer master created from the signed clinic contract. Invoices go to the billing contact.' },
    { id: 'CRM-10814', name: 'Northbridge Health Partners', system: 'CRM', status: 'Active', tax: '91-9346180',
      address: '75 Harbor Avenue, Everett, WA', legal: 'Northbridge Health Partners LLC', parent: 'Independent',
      contact: 'hello@nbpartners.example', verified: '2026-10-09',
      note: 'Converted from a partner referral in September 2026. Contract lists no parent company.' }
  ];
})(window.Aperion);

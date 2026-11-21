/*
 * Case EDI-001 · Northbridge Health — source records (unchanged from v0.3.2).
 * All organizations, identifiers, addresses, and contacts are fictional.
 *
 * NOTE (instructional design): some "note" values reveal the expected answer, e.g.
 * "Same legal entity as CRM-10489". They are shown in the record details panel.
 * This is v0.3.2 content and is preserved as-is pending a design decision.
 */
(function (A) {
  'use strict';
  A.registerModule('data/records', ['namespace']);

  A.data.records = [
    { id: 'CRM-10452', name: 'Northbridge Health', system: 'CRM', status: 'Active', tax: '91-4826103',
      address: '100 Medical Parkway, Seattle, WA', legal: 'Northbridge Health Inc.', parent: 'Northbridge Holdings',
      contact: 'operations@northbridge.example', verified: '2026-10-14',
      note: 'Trade name recorded; current operating address.' },
    { id: 'ERP-77831', name: 'Northbridge Health Inc.', system: 'ERP', status: 'Active', tax: '91-4826103',
      address: '400 Billing Plaza, Seattle, WA', legal: 'Northbridge Health Inc.', parent: 'Northbridge Holdings',
      contact: 'ap@northbridge.example', verified: '2026-10-22',
      note: 'Billing address differs from operational address.' },
    { id: 'REB-33907', name: 'Northbridge Healthcare', system: 'Rebates', status: 'Pending', tax: '',
      address: '100 Medical Pkwy, Seattle, WA', legal: '', parent: 'Northbridge Holdings',
      contact: 'rebates@northbridge.example', verified: '2026-09-02',
      note: 'Incomplete tax identifier; rebate account needs verification.' },
    { id: 'CRM-10489', name: 'Northbridge Medical Group', system: 'CRM', status: 'Active', tax: '91-7728041',
      address: '20 Clinic Way, Tacoma, WA', legal: 'Northbridge Medical Group LLC', parent: 'Northbridge Holdings',
      contact: 'office@nbmedical.example', verified: '2026-10-18',
      note: 'Separate subsidiary under shared parent.' },
    { id: 'ERP-77902', name: 'Northbridge Medical Group LLC', system: 'ERP', status: 'Active', tax: '91-7728041',
      address: '20 Clinic Way, Tacoma, WA', legal: 'Northbridge Medical Group LLC', parent: 'Northbridge Holdings',
      contact: 'billing@nbmedical.example', verified: '2026-10-20',
      note: 'Same legal entity as CRM-10489.' },
    { id: 'CRM-10814', name: 'Northbridge Health Partners', system: 'CRM', status: 'Active', tax: '91-9346180',
      address: '75 Harbor Avenue, Everett, WA', legal: 'Northbridge Health Partners LLC', parent: 'Independent',
      contact: 'hello@nbpartners.example', verified: '2026-10-09',
      note: 'Similar name; unrelated legal entity.' }
  ];
})(window.Aperion);

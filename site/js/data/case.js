/*
 * Case EDI-001 answer key and golden-record design (v0.4.0, approved 2026-11-11).
 *
 * Identity decisions (decision P2-1):
 *   Group A  CRM-10452 + ERP-77831   same tax ID 91-4826103 and legal name "Northbridge Health Inc."
 *   Group B  CRM-10489 + ERP-77902   same tax ID 91-7728041 and legal name "Northbridge Medical Group LLC"
 *   CRM-10814  keep separate          different tax ID 91-9346180; parent "Independent"
 *   REB-33907  hold for verification  no tax ID or legal name; address and parent only *suggest* Group A
 *
 * Golden records (decision P2-2): values must come from the group's own records; learners pick a
 * value AND an evidence-based reason. No unconditional source precedence: each attribute lists
 * every reason that the case evidence supports. tests/phase2/test_case_data.py verifies that every
 * value below exists in the dataset and that the identity rules agree with this key.
 */
(function (A) {
  'use strict';
  A.registerModule('data/case', ['namespace']);

  /** Decisions a learner can make for each record on Match & Compare. */
  A.data.decisionOptions = {
    separate: 'Keep separate (distinct entity)',
    hold: 'Hold for verification'
  };

  A.data.answerKey = {
    groups: [
      { label: 'Northbridge Health Inc.', records: ['CRM-10452', 'ERP-77831'] },
      { label: 'Northbridge Medical Group LLC', records: ['CRM-10489', 'ERP-77902'] }
    ],
    separate: ['CRM-10814'],
    hold: ['REB-33907']
  };

  /** Evidence reasons a learner can give for a golden-record value. */
  A.data.goldenReasons = [
    { id: 'agree', label: 'All sources in the group agree on this value' },
    { id: 'erp-legal', label: 'ERP (finance) is the system of record for legal and tax identity' },
    { id: 'crm-operating', label: 'CRM holds the verified operating relationship (site, contact)' },
    { id: 'billing-source', label: 'Finance record identifies this as the billing / remittance value' },
    { id: 'recent', label: 'Most recently verified source' },
    { id: 'only', label: 'Only source with a value' }
  ];

  /** Golden-record attributes: label, the record field values come from, and a short prompt. */
  A.data.goldenAttributes = [
    { key: 'legalName', label: 'Legal name', field: 'legal', prompt: 'The registered legal entity name.' },
    { key: 'taxId', label: 'Tax identifier', field: 'tax', prompt: 'The entity’s tax identifier.' },
    { key: 'operatingAddress', label: 'Operating address', field: 'address', prompt: 'Where the organization actually operates.' },
    { key: 'billingAddress', label: 'Billing address', field: 'address', prompt: 'Where invoices and remittances are sent.' },
    { key: 'parent', label: 'Parent organization', field: 'parent', prompt: 'The corporate parent, if any.' },
    { key: 'primaryContact', label: 'Primary business contact', field: 'contact', prompt: 'The main operational contact (not accounts payable).' }
  ];

  /**
   * Expected golden-record values per group (keyed by sorted record IDs).
   * `reasons` lists every reason the evidence supports; any one of them is accepted.
   * `why` is shown to the learner in feedback.
   */
  A.data.goldenKey = {
    'CRM-10452|ERP-77831': {
      legalName: { value: 'Northbridge Health Inc.', reasons: ['agree', 'erp-legal'], why: 'Both sources agree, and ERP is the finance system of record for legal identity.' },
      taxId: { value: '91-4826103', reasons: ['agree', 'erp-legal'], why: 'Both sources carry the same tax identifier.' },
      operatingAddress: { value: '100 Medical Parkway, Seattle, WA', reasons: ['crm-operating'], why: 'CRM’s address was confirmed at an October 2026 site visit. The ERP address is a remittance address, not where the organization operates.' },
      billingAddress: { value: '400 Billing Plaza, Seattle, WA', reasons: ['billing-source'], why: 'The ERP note identifies 400 Billing Plaza as the accounts-payable remittance address.' },
      parent: { value: 'Northbridge Holdings', reasons: ['agree'], why: 'Both sources list the same parent.' },
      primaryContact: { value: 'operations@northbridge.example', reasons: ['crm-operating'], why: 'ap@ is an accounts-payable mailbox; the operations contact belongs to the CRM relationship record.' }
    },
    'CRM-10489|ERP-77902': {
      legalName: { value: 'Northbridge Medical Group LLC', reasons: ['agree', 'erp-legal'], why: 'Both sources agree on the LLC name used in contracts.' },
      taxId: { value: '91-7728041', reasons: ['agree', 'erp-legal'], why: 'Both sources carry the same tax identifier.' },
      operatingAddress: { value: '20 Clinic Way, Tacoma, WA', reasons: ['agree', 'crm-operating'], why: 'Both sources list the Tacoma clinic address.' },
      billingAddress: { value: '20 Clinic Way, Tacoma, WA', reasons: ['agree', 'billing-source'], why: 'The finance record invoices the same Tacoma address; no separate remittance address exists.' },
      parent: { value: 'Northbridge Holdings', reasons: ['agree'], why: 'Both sources list the same parent.' },
      primaryContact: { value: 'office@nbmedical.example', reasons: ['crm-operating'], why: 'billing@ is the invoicing contact named in the ERP note; the clinic office is the operational contact.' }
    }
  };

  // ---- Validation and assessment (decisions P2-2, P2-3; approved 2026-11-11) ---------------

  /** "Which evidence establishes that these records are the same entity?" Correct: tax + legal. */
  A.data.identityBasisOptions = [
    { id: 'tax', label: 'Matching tax identifier' },
    { id: 'legal', label: 'Matching legal name' },
    { id: 'name', label: 'Similar customer names' },
    { id: 'parent', label: 'Shared parent organization' },
    { id: 'address', label: 'Shared or similar address' }
  ];
  A.data.identityBasisKey = ['tax', 'legal'];

  /** Why a record was not proposed for a merge. */
  A.data.notProposedReasons = [
    { id: 'conflict-identity', label: 'Its tax identifier and parent organization conflict with the other records' },
    { id: 'missing-identity', label: 'It has no tax identifier or legal name to confirm its identity' },
    { id: 'name', label: 'Its customer name is different' },
    { id: 'status', label: 'Its status is Pending' },
    { id: 'address', label: 'Its address is in a different city' }
  ];
  A.data.notProposedKey = { 'CRM-10814': 'conflict-identity', 'REB-33907': 'missing-identity' };

  /** Follow-up action for a record held for verification. */
  A.data.heldFollowUps = [
    { id: 'request', label: 'Ask Commercial Operations to obtain the W-9 and legal name, then re-evaluate the record' },
    { id: 'merge-now', label: 'Merge it into the matching group now, because the address and parent match' },
    { id: 'deactivate', label: 'Deactivate the rebate account' }
  ];
  A.data.heldFollowUpKey = 'request';

  /** Minimum length of a governance rationale (words). */
  A.data.rationaleMinWords = 12;

  /** Contextual stakeholder guidance (text only; decision P2-4). */
  A.data.stakeholderPrompts = {
    work: { name: 'Daniel Brooks', role: 'Systems Architecture', img: 'daniel', text: 'Each system captures the customer for a different purpose: CRM for the relationship, ERP for invoicing, and Rebates for program enrollment. Expect differences. Look for the identifiers that only a legal entity has.' },
    compare: { name: 'Maya Chen', role: 'Data Governance', img: 'maya', text: 'A merge is only defensible when the tax identifier and legal name agree. Similar names, shared parents, and nearby addresses can point you to a candidate, but they cannot prove identity.' },
    golden: { name: 'Priya Shah', role: 'Finance Operations', img: 'priya', text: 'Finance needs the remittance address and the accounts-payable contact kept where invoices go. Do not let a billing address become the place the customer operates.' },
    validation: { name: 'Marcus Reed', role: 'Commercial Operations', img: 'marcus', text: 'If a rebate account is missing its W-9, tell me. I would rather chase the paperwork than have a payment merged into the wrong company.' },
    debrief: { name: 'Maya Chen', role: 'Data Governance', img: 'maya', text: 'Here is how your investigation measured up. Every point below comes from a specific decision you made.' }
  };
})(window.Aperion);

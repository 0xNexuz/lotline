# Problem

## One-line problem

Food recall coordinators cannot reliably identify the smallest safe recall set because ingredient, production, cleaning, shipment, and location relationships are fragmented across records.

## Users

- Primary: recall coordinator.
- Secondary: plant and distribution operators.
- Approver: authorized food-safety operator.
- Reviewer: internal auditor or judge inspecting the decision path.

## Current workaround

Manual reconciliation or broad SKU/date-window recalls can miss indirect exposure or quarantine safe inventory. No external user research has yet been completed; this problem framing is **PARTIAL** and based on domain reasoning rather than validated interviews.

## Success condition

Given complete lineage and cleaning data, a system returns the policy-defined affected lot set, explains each inclusion, requires authorized approval, executes actions once, and leaves unrelated inventory untouched.

## Non-goals

- Validate supplier claims.
- Predict contamination.
- Replace safety professionals.
- Claim regulatory compliance.
- Operate on real company or customer data in this prototype.

## Final statement

LotLine turns a structured safety alert into a traceable, approval-gated recall plan. It uses connected lot lineage and equipment-cleaning history to find direct and cross-contact exposure while preserving evidence for every proposed action.

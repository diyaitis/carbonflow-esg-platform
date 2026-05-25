# Decisions

## Source ingest mechanisms
- **SAP (fuel / procurement)**: file upload for CSV exports.
  - Real-world SAP teams often export transactional records via flat-file CSV from SAP S/4HANA or legacy ECC.
  - Chose this mode because it is the most common client-delivered format and avoids the complexity of OData/BAPI connection plumbing for a prototype.
- **Utility electricity**: portal CSV upload.
  - Facilities teams usually download meter bills or portal exports as CSV/Excel.
  - This prototype models a billing-period export with usage and rate details.
- **Corporate travel**: API fetch stub.
  - Concur and Navan expose travel data through APIs, and flight/hotel/ground categories are best represented as transactions.
  - Implemented a simulated API fetch to mirror the production expectation of pulling travel records from a corporate travel platform.

## Subset of SAP reality handled
- Focused on SAP invoice-line style exports with fuel and procurement matter.
- Supported German and English headers, inconsistent unit labels, and date formats.
- Ignored deep SAP metadata such as plant hierarchy, cost center hierarchies, and internal material master semantics.
- This lets the prototype demonstrate realistic parsing without building a full SAP connector.

## Utility source subset
- Supported meter billing rows with start/end dates and usage in kWh.
- Did not model time-of-use tariffs, demand charges, or multiple meter rates per bill.
- Chose to normalize to kWh and compute Scope 2 emissions using a fixed factor.

## Travel source subset
- Supported flights, hotels, and ground transport.
- Modeled flight distance-based emissions, hotel room-night emissions, and ground km emissions.
- Did not integrate with live airport code distance lookups or corporate travel booking APIs.

## What would I ask the PM?
- Should each tenant have independent emission factors, or should factors be centralized?
- Does the review workflow require rollback of approved rows or versioned corrections?
- Which specific SAP export line items are highest priority for the first client?
- Should the portal support manual reconciliation of meter IDs to facility records?

# Source Research

## SAP fuel and procurement
- Real-world format: SAP S/4HANA or ECC export to CSV/Excel.
- Typical export characteristics:
  - German headers such as `Werk`, `Material`, `Menge`, `Einheit`, `Betrag in EUR`.
  - Dates in formats like `YYYY-MM-DD`, `DD.MM.YYYY`, or `MM/DD/YYYY`.
  - Mixed units in the same report (`L`, `kg`, `EA`).
  - Line items may represent both fuel consumption and procurement spend.
- Prototype sample shape:
  - `plant`, `material`, `quantity`, `unit`, `amount_eur`, `posting_date`.
  - Category detection based on material description.
- What would break in real deployment:
  - Complex SAP material master logic.
  - Multiple currencies and exchange rates.
  - SAP ERP exports in Excel/IDoc or BAPI without a flattened CSV.

## Utility electricity
- Real-world format: utility portal CSV/Excel meter bill export.
- Typical characteristics:
  - Billing period start/end dates.
  - Usage in kWh, sometimes with demand and rate columns.
  - Meter identifier and account number.
- Prototype sample shape:
  - `billing_start`, `billing_end`, `total usage (kwh)`, `meter_id`, `account`.
  - Normalized to kWh and Scope 2 emissions.
- What would break in real deployment:
  - Time-of-use tariffs, net metering, and multi-rate bills.
  - Portal exports delivered as PDF instead of CSV.
  - Inconsistent date formats or non-standard header names.

## Corporate travel
- Real-world format: Concur/Navan booking API or CSV export.
- Typical characteristics:
  - Trip records with category, origin/destination, itinerary, traveler, and cost.
  - Distances sometimes provided, otherwise inferred from airport codes.
  - Different emissions per category: flights, hotels, ground transport.
- Prototype sample shape:
  - Flight records with `distance_km` and `class`.
  - Hotel records with `room_nights`.
  - Ground records with `distance_km`.
- What would break in real deployment:
  - Missing distance values requiring airport code lookups.
  - Airline class categories outside economy/business.
  - Aggregated travel spends without transaction-level detail.

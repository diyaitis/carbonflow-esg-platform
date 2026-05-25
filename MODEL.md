# Data Model

## Goals
- Support multi-tenancy across ingest pipelines.
- Track source-of-truth for every ingested row.
- Normalize quantities and units to compute kgCO2e consistently.
- Preserve original raw properties and audit changes.
- Represent Scope 1/2/3 categories clearly.

## Core entities

### Tenant
- `slug`, `name`
- Represents a client company or business unit.
- Enables segregated ingestion and review data for multi-tenancy.

### IngestionSource
- `tenant`, `source_type`, `name`, `external_id`, `raw_payload`, `origin_file_name`, `uploaded_at`
- Captures the exact source that produced a set of rows.
- `raw_payload` stores metadata about imported file contents or API payload.
- This is the source-of-truth anchor for downstream normalized rows.

### EmissionRow
- `tenant`, `ingestion_source`, `source_row_id`
- `source_category` identifies the normalized activity type (fuel, electricity, flight, hotel, ground).
- `scope` is an explicit Scope 1 / Scope 2 / Scope 3 enumeration.
- `activity_date`, `period_start`, `period_end` represent the activity or billing window.
- `activity_description` and `original_properties` preserve context from the raw source.
- `quantity` and `quantity_unit` store the original measured quantity.
- `normalized_quantity` and `normalized_unit` store the standardized activity basis used for emissions.
- `emission_factor` is the factor used to convert activity to CO2e.
- `emissions_kg_co2e` is the computed emission result.
- `suspicious_reason` flags rows worthy of analyst review.
- `status`, `reviewed_by`, `reviewed_at`, `edited_by`, `edited_at`, `note` enable review workflows.

### EmissionRowAudit
- Tracks edit history for a row.
- `change_type`, `changed_by`, `changed_at`, `changes`
- Preserves a small audit trail for review decisions and downstream audit support.

## Why this model?
- The model keeps raw source context separate from normalized emissions data.
- `IngestionSource` is the source-of-truth for where data came from.
- `EmissionRow` can represent invoice-line fuel, portal electricity bills, or travel transactions in a single table.
- The review fields and audit records support analyst sign-off and auditability.
- Multi-tenancy is enforced at the row and source level.

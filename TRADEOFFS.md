# Tradeoffs

## 1. No live SAP/OData connector
- Built a CSV upload interface instead of integrating directly with SAP OData, IDoc, or BAPI.
- Justification: ingesting realistic SAP export shapes is more valuable than wiring a brittle connection in a four-day prototype.

## 2. Fixed emission factors rather than a lookup engine
- Used hard-coded emission factors for diesel, electricity, flights, hotels, and ground transport.
- Justification: the prototype focuses on ingestion, normalization, and review flow; an emissions factor management service is a separate product feature.

## 3. Simplified approval workflow
- Provided row-level approve/reject actions without staged publishing, rollback histories, or auditor-facing certification states.
- Justification: the assignment weighs analyst UX and data model quality more heavily than a complete enterprise workflow engine.

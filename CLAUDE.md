# platform-contracts

Canonical Pydantic schemas for the OpenMind TransactionFlow platform.

## Purpose
Reference layer — new modules CAN import, existing repos DON'T change.
NO business logic, NO Django imports, NO framework dependencies.

## Install
pip install git+https://github.com/dziadekp/platform-contracts.git@v0.1.0

## Structure
- src/platform_contracts/enums.py — Shared enums
- src/platform_contracts/common/ — Identifiers, Money, Timestamps
- src/platform_contracts/accounting/ — Transaction, Classification, JournalEntry, Account, Vendor, Suspense, Risk
- src/platform_contracts/messaging/ — Message, Conversation, Templates
- src/platform_contracts/events/ — PlatformEvent, AuditEvent
- src/platform_contracts/tax/ — TaxComputeRequest/Response

## Rules
- Pydantic models only, no business logic
- Python 3.12+
- Additive changes within minor versions; breaking = major bump
- Semantic versioning via git tags

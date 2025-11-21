"""Connectors for external SaaS APIs (Gmail, Discord, etc.).

Phase 1/2: concrete, per-SaaS implementations live here with no shared
abstractions. Each connector provides a small, explicit async API
suitable for use by higher-level orchestration layers.
"""

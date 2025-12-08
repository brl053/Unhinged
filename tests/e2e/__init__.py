"""
@llm-type test.e2e
@llm-does end-to-end testing infrastructure with tenant isolation

E2E Test Package

Uses tenant-based isolation to run tests against real infrastructure
without affecting production/development data.

Key concepts:
- All tests use tenant='test' for data isolation
- Tests can be run against local containers or CI environment
- Cleanup is automatic via delete_tenant_data()
"""

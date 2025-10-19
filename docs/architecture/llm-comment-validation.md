# 🔍 LLM Comment Validation Report

## 📊 Summary

**Total Issues**: 7
**Errors**: ❌ 3
**Warnings**: ⚠️ 4

## ❌ Errors

### scripts/docs/llm-context-warmer.py:17
**Element**: LLMContextWarmer
**Issue**: Missing required @llm-key tag for class
**Type**: missing_tag

### scripts/docs/test_llm_extraction.py:42
**Element**: test_extract_llm_context_from_python
**Issue**: Missing required @llm-key tag for service
**Type**: missing_tag

### scripts/docs/test_llm_extraction.py:42
**Element**: test_extract_llm_context_from_python
**Issue**: Missing required @llm-map tag for service
**Type**: missing_tag

## ⚠️ Warnings

### scripts/docs/llm-context-warmer.py:316
**Element**: _validate_legend_completeness
**Issue**: @llm-legend too short (13 chars). Minimum: 20
**Type**: short_legend

### scripts/docs/extract-llm-comments.py:573
**Element**: extract_comments_from_file
**Issue**: @llm-legend too short (12 chars). Minimum: 20
**Type**: short_legend

### scripts/docs/extract-llm-comments.py:594
**Element**: extract_comments_from_codebase
**Issue**: @llm-legend too short (12 chars). Minimum: 20
**Type**: short_legend

### scripts/docs/extract-llm-comments.py:604
**Element**: parse_llm_tags
**Issue**: @llm-legend too short (17 chars). Minimum: 20
**Type**: short_legend

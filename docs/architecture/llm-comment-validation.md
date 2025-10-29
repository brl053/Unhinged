# 🔍 LLM Comment Validation Report

## 📊 Summary

**Total Issues**: 259
**Errors**: ❌ 253
**Warnings**: ⚠️ 2
**Infos**: ℹ️ 4

## ❌ Errors

### build/docs-generation/extract-llm-comments.py:542
**Element**: extract_comments_from_file
**Issue**: Missing required @llm-does tag for function
**Type**: missing_tag

### build/docs-generation/extract-llm-comments.py:563
**Element**: extract_comments_from_codebase
**Issue**: Missing required @llm-does tag for function
**Type**: missing_tag

### build/docs-generation/extract-llm-comments.py:573
**Element**: parse_llm_tags
**Issue**: Missing required @llm-does tag for function
**Type**: missing_tag

### build/docs-generation/extract-llm-comments.py:598
**Element**: save_extraction_results
**Issue**: Missing required @llm-does tag for function
**Type**: missing_tag

### build/tools/llm-docs-enforcer.py:165
**Element**: unknown
**Issue**: Invalid @llm-type '{llm_type}'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### build/tools/llm-docs-enforcer.py:170
**Element**: unknown
**Issue**: Invalid @llm-type '{llm_type}'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/build/llm_integration.py:3
**Element**: unknown
**Issue**: Missing required @llm-does tag for service
**Type**: missing_tag

### .llmdocs-backup/build/cli.py:3
**Element**: unknown
**Issue**: Missing required @llm-does tag for service
**Type**: missing_tag

### .llmdocs-backup/build/orchestrator.py:3
**Element**: unknown
**Issue**: Missing required @llm-does tag for service
**Type**: missing_tag

### .llmdocs-backup/build/monitoring.py:3
**Element**: unknown
**Issue**: Missing required @llm-does tag for service
**Type**: missing_tag

### .llmdocs-backup/build/developer_experience.py:3
**Element**: unknown
**Issue**: Missing required @llm-does tag for service
**Type**: missing_tag

### .llmdocs-backup/build/build.py:3
**Element**: unknown
**Issue**: Missing required @llm-does tag for service
**Type**: missing_tag

### .llmdocs-backup/build/python/run.py:2
**Element**: unknown
**Issue**: Missing required @llm-does tag for util.runner
**Type**: missing_tag

### .llmdocs-backup/build/python/run.py:32
**Element**: UnhingedPythonRunner
**Issue**: Missing required @llm-does tag for python-executor
**Type**: missing_tag

### .llmdocs-backup/build/python/run.py:32
**Element**: UnhingedPythonRunner
**Issue**: Invalid @llm-type 'python-executor'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/build/python/setup.py:2
**Element**: unknown
**Issue**: Missing required @llm-does tag for python-setup
**Type**: missing_tag

### .llmdocs-backup/build/python/setup.py:2
**Element**: unknown
**Issue**: Invalid @llm-type 'python-setup'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/build/python/setup.py:33
**Element**: UnhingedPythonSetup
**Issue**: Missing required @llm-does tag for python-environment-setup
**Type**: missing_tag

### .llmdocs-backup/build/python/setup.py:33
**Element**: UnhingedPythonSetup
**Issue**: Invalid @llm-type 'python-environment-setup'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/build/docs-generation/llm-context-warmer.py:2
**Element**: unknown
**Issue**: Missing required @llm-does tag for tool
**Type**: missing_tag

### .llmdocs-backup/build/docs-generation/llm-context-warmer.py:17
**Element**: LLMContextWarmer
**Issue**: Missing required @llm-does tag for class
**Type**: missing_tag

### .llmdocs-backup/build/docs-generation/llm-context-warmer.py:37
**Element**: generate_project_overview
**Issue**: Missing required @llm-does tag for function
**Type**: missing_tag

### .llmdocs-backup/build/docs-generation/llm-context-warmer.py:86
**Element**: _extract_key_components
**Issue**: Missing required @llm-does tag for function
**Type**: missing_tag

### .llmdocs-backup/build/docs-generation/llm-context-warmer.py:123
**Element**: paginate_comments
**Issue**: Missing required @llm-does tag for function
**Type**: missing_tag

### .llmdocs-backup/build/docs-generation/llm-context-warmer.py:156
**Element**: _improve_element_name
**Issue**: Missing required @llm-does tag for function
**Type**: missing_tag

### .llmdocs-backup/build/docs-generation/llm-context-warmer.py:179
**Element**: _find_related_services
**Issue**: Missing required @llm-does tag for function
**Type**: missing_tag

### .llmdocs-backup/build/docs-generation/llm-context-warmer.py:232
**Element**: _validate_context_completeness
**Issue**: Missing required @llm-does tag for function
**Type**: missing_tag

### .llmdocs-backup/build/docs-generation/llm-context-warmer.py:254
**Element**: _generate_getting_started_section
**Issue**: Missing required @llm-does tag for function
**Type**: missing_tag

### .llmdocs-backup/build/docs-generation/llm-context-warmer.py:283
**Element**: _extract_dependency_information
**Issue**: Missing required @llm-does tag for function
**Type**: missing_tag

### .llmdocs-backup/build/docs-generation/llm-context-warmer.py:316
**Element**: _validate_legend_completeness
**Issue**: Missing required @llm-does tag for function
**Type**: missing_tag

### .llmdocs-backup/build/docs-generation/llm-context-warmer.py:351
**Element**: generate_enhanced_project_overview
**Issue**: Missing required @llm-does tag for function
**Type**: missing_tag

### .llmdocs-backup/build/docs-generation/test_llm_extraction.py:2
**Element**: unknown
**Issue**: Missing required @llm-does tag for test
**Type**: missing_tag

### .llmdocs-backup/build/docs-generation/test_llm_extraction.py:42
**Element**: test_extract_llm_context_from_python
**Issue**: Missing required @llm-does tag for service
**Type**: missing_tag

### .llmdocs-backup/build/docs-generation/test_llm_extraction.py:70
**Element**: test_extract_llm_context_from_typescript
**Issue**: Missing required @llm-does tag for component
**Type**: missing_tag

### .llmdocs-backup/build/docs-generation/test_llm_extraction.py:91
**Element**: test_parse_llm_tags_with_context
**Issue**: Missing required @llm-does tag for validator
**Type**: missing_tag

### .llmdocs-backup/build/docs-generation/test_llm_extraction.py:203
**Element**: TestLLMContextWarmerImprovements
**Issue**: Missing required @llm-does tag for test
**Type**: missing_tag

### .llmdocs-backup/build/docs-generation/test_llm_extraction.py:210
**Element**: test_element_name_detection_from_service_path
**Issue**: Missing required @llm-does tag for test
**Type**: missing_tag

### .llmdocs-backup/build/docs-generation/test_llm_extraction.py:241
**Element**: test_element_name_detection_from_python_file
**Issue**: Missing required @llm-does tag for test
**Type**: missing_tag

### .llmdocs-backup/build/docs-generation/test_llm_extraction.py:270
**Element**: test_find_related_services_by_port_references
**Issue**: Missing required @llm-does tag for test
**Type**: missing_tag

### .llmdocs-backup/build/docs-generation/test_llm_extraction.py:315
**Element**: test_context_completeness_validation
**Issue**: Missing required @llm-does tag for test
**Type**: missing_tag

### .llmdocs-backup/build/docs-generation/test_llm_extraction.py:357
**Element**: test_pagination_data_integrity
**Issue**: Missing required @llm-does tag for test
**Type**: missing_tag

### .llmdocs-backup/build/docs-generation/test_llm_extraction.py:418
**Element**: TestLLMContextWarmerEnhancements
**Issue**: Missing required @llm-does tag for test
**Type**: missing_tag

### .llmdocs-backup/build/docs-generation/test_llm_extraction.py:425
**Element**: test_getting_started_section_generation
**Issue**: Missing required @llm-does tag for test
**Type**: missing_tag

### .llmdocs-backup/build/docs-generation/test_llm_extraction.py:469
**Element**: test_dependency_information_extraction
**Issue**: Missing required @llm-does tag for test
**Type**: missing_tag

### .llmdocs-backup/build/docs-generation/test_llm_extraction.py:506
**Element**: test_complete_legend_validation
**Issue**: Missing required @llm-does tag for test
**Type**: missing_tag

### .llmdocs-backup/build/docs-generation/test_llm_extraction.py:549
**Element**: test_enhanced_overview_with_getting_started
**Issue**: Missing required @llm-does tag for test
**Type**: missing_tag

### .llmdocs-backup/build/docs-generation/extract-llm-comments.py:573
**Element**: extract_comments_from_file
**Issue**: Missing required @llm-does tag for function
**Type**: missing_tag

### .llmdocs-backup/build/docs-generation/extract-llm-comments.py:594
**Element**: extract_comments_from_codebase
**Issue**: Missing required @llm-does tag for function
**Type**: missing_tag

### .llmdocs-backup/build/docs-generation/extract-llm-comments.py:604
**Element**: parse_llm_tags
**Issue**: Missing required @llm-does tag for function
**Type**: missing_tag

### .llmdocs-backup/build/docs-generation/extract-llm-comments.py:634
**Element**: save_extraction_results
**Issue**: Missing required @llm-does tag for function
**Type**: missing_tag

### .llmdocs-backup/build/docs-generation/validate-llm-comments.py:287
**Element**: validate_comment
**Issue**: Missing required @llm-does tag for function
**Type**: missing_tag

### .llmdocs-backup/build/docs-generation/validate-llm-comments.py:299
**Element**: validate_all_comments
**Issue**: Missing required @llm-does tag for function
**Type**: missing_tag

### .llmdocs-backup/build/docs-generation/validate-llm-comments.py:324
**Element**: check_required_tags
**Issue**: Missing required @llm-does tag for function
**Type**: missing_tag

### .llmdocs-backup/build/docs-generation/validate-llm-comments.py:351
**Element**: check_tag_format
**Issue**: Missing required @llm-does tag for function
**Type**: missing_tag

### .llmdocs-backup/build/docs-generation/llm_types.py:2
**Element**: unknown
**Issue**: Missing required @llm-does tag for contract
**Type**: missing_tag

### .llmdocs-backup/build/tools/dead-code-analyzer.py:2
**Element**: unknown
**Issue**: Missing required @llm-does tag for dead-code-analyzer
**Type**: missing_tag

### .llmdocs-backup/build/tools/dead-code-analyzer.py:2
**Element**: unknown
**Issue**: Invalid @llm-type 'dead-code-analyzer'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/build/tools/dead-code-analyzer.py:61
**Element**: DeadCodeAnalyzer
**Issue**: Missing required @llm-does tag for analyzer-class
**Type**: missing_tag

### .llmdocs-backup/build/tools/dead-code-analyzer.py:61
**Element**: DeadCodeAnalyzer
**Issue**: Invalid @llm-type 'analyzer-class'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/build/tools/cleanup-dead-code.py:2
**Element**: unknown
**Issue**: Missing required @llm-does tag for cleanup-tool
**Type**: missing_tag

### .llmdocs-backup/build/tools/cleanup-dead-code.py:2
**Element**: unknown
**Issue**: Invalid @llm-type 'cleanup-tool'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/build/tools/cleanup-dead-code.py:48
**Element**: DeadCodeCleanup
**Issue**: Missing required @llm-does tag for cleanup-class
**Type**: missing_tag

### .llmdocs-backup/build/tools/cleanup-dead-code.py:48
**Element**: DeadCodeCleanup
**Issue**: Invalid @llm-type 'cleanup-class'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/build/tools/llmdocs-v2-migrator.py:2
**Element**: unknown
**Issue**: Missing required @llm-does tag for util.migrator
**Type**: missing_tag

### .llmdocs-backup/build/tools/llm-docs-enforcer.py:2
**Element**: unknown
**Issue**: Missing required @llm-does tag for build-tool
**Type**: missing_tag

### .llmdocs-backup/build/tools/llm-docs-enforcer.py:2
**Element**: unknown
**Issue**: Invalid @llm-type 'build-tool'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/build/tools/llm-docs-enforcer.py:170
**Element**: unknown
**Issue**: Missing required @llm-does tag for {llm_type}
**Type**: missing_tag

### .llmdocs-backup/build/tools/llm-docs-enforcer.py:170
**Element**: unknown
**Issue**: Invalid @llm-type '{llm_type}'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/build/tools/llm-docs-enforcer.py:180
**Element**: unknown
**Issue**: Missing required @llm-does tag for {llm_type}
**Type**: missing_tag

### .llmdocs-backup/build/tools/llm-docs-enforcer.py:180
**Element**: unknown
**Issue**: Invalid @llm-type '{llm_type}'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/build/ci/ci-config.yml:2
**Element**: version
**Issue**: Missing required @llm-does tag for ci-configuration
**Type**: missing_tag

### .llmdocs-backup/build/ci/ci-config.yml:2
**Element**: version
**Issue**: Invalid @llm-type 'ci-configuration'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/build/orchestration/docker-compose.production.yml:5
**Element**: version
**Issue**: Missing required @llm-does tag for infrastructure-config
**Type**: missing_tag

### .llmdocs-backup/build/orchestration/docker-compose.production.yml:5
**Element**: version
**Issue**: Invalid @llm-type 'infrastructure-config'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/build/orchestration/docker-compose.development.yml:5
**Element**: version
**Issue**: Missing required @llm-does tag for infrastructure-config
**Type**: missing_tag

### .llmdocs-backup/build/orchestration/docker-compose.development.yml:5
**Element**: version
**Issue**: Invalid @llm-type 'infrastructure-config'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/build/config/build-config.yml:2
**Element**: version
**Issue**: Missing required @llm-does tag for build-configuration
**Type**: missing_tag

### .llmdocs-backup/build/config/build-config.yml:2
**Element**: version
**Issue**: Invalid @llm-type 'build-configuration'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/build/modules/typescript_builder.py:3
**Element**: unknown
**Issue**: Missing required @llm-does tag for service
**Type**: missing_tag

### .llmdocs-backup/build/modules/registry_builder.py:3
**Element**: unknown
**Issue**: Missing required @llm-does tag for build-module
**Type**: missing_tag

### .llmdocs-backup/build/modules/registry_builder.py:3
**Element**: unknown
**Issue**: Invalid @llm-type 'build-module'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/build/modules/registry_builder.py:47
**Element**: RegistryBuilder
**Issue**: Missing required @llm-does tag for build-module
**Type**: missing_tag

### .llmdocs-backup/build/modules/registry_builder.py:47
**Element**: RegistryBuilder
**Issue**: Invalid @llm-type 'build-module'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/build/modules/registry_builder.py:62
**Element**: can_handle
**Issue**: Missing required @llm-does tag for function
**Type**: missing_tag

### .llmdocs-backup/build/modules/registry_builder.py:76
**Element**: get_dependencies
**Issue**: Missing required @llm-does tag for function
**Type**: missing_tag

### .llmdocs-backup/build/modules/registry_builder.py:94
**Element**: calculate_cache_key
**Issue**: Missing required @llm-does tag for function
**Type**: missing_tag

### .llmdocs-backup/build/modules/registry_builder.py:121
**Element**: extract_html_metadata
**Issue**: Missing required @llm-does tag for function
**Type**: missing_tag

### .llmdocs-backup/build/modules/registry_builder.py:189
**Element**: scan_static_html_directory
**Issue**: Missing required @llm-does tag for function
**Type**: missing_tag

### .llmdocs-backup/build/modules/registry_builder.py:217
**Element**: build_file_structure
**Issue**: Missing required @llm-does tag for function
**Type**: missing_tag

### .llmdocs-backup/build/modules/registry_builder.py:284
**Element**: generate_registry_js
**Issue**: Missing required @llm-does tag for function
**Type**: missing_tag

### .llmdocs-backup/build/modules/registry_builder.py:291
**Element**: unknown
**Issue**: Missing required @llm-does tag for config
**Type**: missing_tag

### .llmdocs-backup/build/modules/registry_builder.py:431
**Element**: build
**Issue**: Missing required @llm-does tag for function
**Type**: missing_tag

### .llmdocs-backup/build/modules/registry_builder.py:503
**Element**: clean
**Issue**: Missing required @llm-does tag for function
**Type**: missing_tag

### .llmdocs-backup/build/modules/proto_client_builder.py:3
**Element**: unknown
**Issue**: Missing required @llm-does tag for build-module
**Type**: missing_tag

### .llmdocs-backup/build/modules/proto_client_builder.py:3
**Element**: unknown
**Issue**: Invalid @llm-type 'build-module'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/build/modules/proto_client_builder.py:55
**Element**: ProtoClientBuilder
**Issue**: Missing required @llm-does tag for build-module
**Type**: missing_tag

### .llmdocs-backup/build/modules/proto_client_builder.py:55
**Element**: ProtoClientBuilder
**Issue**: Invalid @llm-type 'build-module'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/build/modules/typescript_proto_handler.py:3
**Element**: unknown
**Issue**: Missing required @llm-does tag for proto-handler
**Type**: missing_tag

### .llmdocs-backup/build/modules/typescript_proto_handler.py:3
**Element**: unknown
**Issue**: Invalid @llm-type 'proto-handler'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/build/modules/__init__.py:1
**Element**: unknown
**Issue**: Missing required @llm-does tag for contract
**Type**: missing_tag

### .llmdocs-backup/build/modules/__init__.py:251
**Element**: validate_build_patterns
**Issue**: Missing required @llm-does tag for validation
**Type**: missing_tag

### .llmdocs-backup/build/modules/__init__.py:251
**Element**: validate_build_patterns
**Issue**: Invalid @llm-type 'validation'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/build/modules/c_builder.py:3
**Element**: unknown
**Issue**: Missing required @llm-does tag for service
**Type**: missing_tag

### .llmdocs-backup/build/modules/python_builder.py:3
**Element**: unknown
**Issue**: Missing required @llm-does tag for service
**Type**: missing_tag

### .llmdocs-backup/build/modules/python_proto_handler.py:3
**Element**: unknown
**Issue**: Missing required @llm-does tag for proto-handler
**Type**: missing_tag

### .llmdocs-backup/build/modules/python_proto_handler.py:3
**Element**: unknown
**Issue**: Invalid @llm-type 'proto-handler'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/build/modules/service_discovery_builder.py:3
**Element**: unknown
**Issue**: Missing required @llm-does tag for build-module
**Type**: missing_tag

### .llmdocs-backup/build/modules/service_discovery_builder.py:3
**Element**: unknown
**Issue**: Invalid @llm-type 'build-module'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/build/modules/service_discovery_builder.py:45
**Element**: ServiceDiscoveryBuilder
**Issue**: Missing required @llm-does tag for build-module
**Type**: missing_tag

### .llmdocs-backup/build/modules/service_discovery_builder.py:45
**Element**: ServiceDiscoveryBuilder
**Issue**: Invalid @llm-type 'build-module'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/build/modules/dual_system_builder.py:3
**Element**: unknown
**Issue**: Missing required @llm-does tag for service
**Type**: missing_tag

### .llmdocs-backup/build/modules/kotlin_proto_handler.py:3
**Element**: unknown
**Issue**: Missing required @llm-does tag for proto-handler
**Type**: missing_tag

### .llmdocs-backup/build/modules/kotlin_proto_handler.py:3
**Element**: unknown
**Issue**: Invalid @llm-type 'proto-handler'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/build/modules/polyglot_proto_engine.py:3
**Element**: unknown
**Issue**: Missing required @llm-does tag for build-engine
**Type**: missing_tag

### .llmdocs-backup/build/modules/polyglot_proto_engine.py:3
**Element**: unknown
**Issue**: Invalid @llm-type 'build-engine'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/build/modules/polyglot_proto_engine.py:175
**Element**: PolyglotProtoEngine
**Issue**: Missing required @llm-does tag for proto-engine
**Type**: missing_tag

### .llmdocs-backup/build/modules/polyglot_proto_engine.py:175
**Element**: PolyglotProtoEngine
**Issue**: Invalid @llm-type 'proto-engine'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/build/modules/c_proto_handler.py:3
**Element**: unknown
**Issue**: Missing required @llm-does tag for proto-handler
**Type**: missing_tag

### .llmdocs-backup/build/modules/c_proto_handler.py:3
**Element**: unknown
**Issue**: Invalid @llm-type 'proto-handler'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/build/modules/kotlin_builder.py:3
**Element**: unknown
**Issue**: Missing required @llm-does tag for service
**Type**: missing_tag

### .llmdocs-backup/build/validators/port_validator.py:1
**Element**: unknown
**Issue**: Missing required @llm-does tag for build-validator
**Type**: missing_tag

### .llmdocs-backup/build/validators/port_validator.py:1
**Element**: unknown
**Issue**: Invalid @llm-type 'build-validator'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/build/validators/resource_validator.py:1
**Element**: unknown
**Issue**: Missing required @llm-does tag for build-validator
**Type**: missing_tag

### .llmdocs-backup/build/validators/resource_validator.py:1
**Element**: unknown
**Issue**: Invalid @llm-type 'build-validator'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/build/validators/kotlin_validator.py:2
**Element**: unknown
**Issue**: Missing required @llm-does tag for validator
**Type**: missing_tag

### .llmdocs-backup/build/validators/kotlin_validator.py:27
**Element**: KotlinValidator
**Issue**: Missing required @llm-does tag for validator
**Type**: missing_tag

### .llmdocs-backup/build/validators/__init__.py:1
**Element**: unknown
**Issue**: Missing required @llm-does tag for build-validation
**Type**: missing_tag

### .llmdocs-backup/build/validators/__init__.py:1
**Element**: unknown
**Issue**: Invalid @llm-type 'build-validation'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/build/validators/polyglot_validator.py:2
**Element**: unknown
**Issue**: Missing required @llm-does tag for validation-system
**Type**: missing_tag

### .llmdocs-backup/build/validators/polyglot_validator.py:2
**Element**: unknown
**Issue**: Invalid @llm-type 'validation-system'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/build/validators/polyglot_validator.py:40
**Element**: ValidationResult
**Issue**: Missing required @llm-does tag for data-model
**Type**: missing_tag

### .llmdocs-backup/build/validators/polyglot_validator.py:40
**Element**: ValidationResult
**Issue**: Invalid @llm-type 'data-model'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/build/validators/polyglot_validator.py:56
**Element**: ValidationSummary
**Issue**: Missing required @llm-does tag for data-model
**Type**: missing_tag

### .llmdocs-backup/build/validators/polyglot_validator.py:56
**Element**: ValidationSummary
**Issue**: Invalid @llm-type 'data-model'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/build/validators/polyglot_validator.py:71
**Element**: BaseValidator
**Issue**: Missing required @llm-does tag for interface
**Type**: missing_tag

### .llmdocs-backup/build/validators/polyglot_validator.py:100
**Element**: FilePatternValidator
**Issue**: Missing required @llm-does tag for validator
**Type**: missing_tag

### .llmdocs-backup/build/validators/polyglot_validator.py:221
**Element**: GeneratedContentValidator
**Issue**: Missing required @llm-does tag for validator
**Type**: missing_tag

### .llmdocs-backup/build/validators/polyglot_validator.py:261
**Element**: PolyglotValidationRunner
**Issue**: Missing required @llm-does tag for orchestrator
**Type**: missing_tag

### .llmdocs-backup/build/validators/polyglot_validator.py:261
**Element**: PolyglotValidationRunner
**Issue**: Invalid @llm-type 'orchestrator'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/build/validators/polyglot_validator.py:301
**Element**: run_validation
**Issue**: Missing required @llm-does tag for function
**Type**: missing_tag

### .llmdocs-backup/build/validators/polyglot_validator.py:363
**Element**: main
**Issue**: Missing required @llm-does tag for function
**Type**: missing_tag

### .llmdocs-backup/build/validators/dependency_validator.py:1
**Element**: unknown
**Issue**: Missing required @llm-does tag for build-validator
**Type**: missing_tag

### .llmdocs-backup/build/validators/dependency_validator.py:1
**Element**: unknown
**Issue**: Invalid @llm-type 'build-validator'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/build/validators/python_validator.py:2
**Element**: unknown
**Issue**: Missing required @llm-does tag for validator
**Type**: missing_tag

### .llmdocs-backup/build/validators/python_validator.py:28
**Element**: PythonValidator
**Issue**: Missing required @llm-does tag for validator
**Type**: missing_tag

### .llmdocs-backup/build/validators/python_validator.py:256
**Element**: PythonFormatterValidator
**Issue**: Missing required @llm-does tag for validator
**Type**: missing_tag

### .llmdocs-backup/services/shared/__init__.py:2
**Element**: unknown
**Issue**: Missing required @llm-does tag for service-shared
**Type**: missing_tag

### .llmdocs-backup/services/shared/__init__.py:2
**Element**: unknown
**Issue**: Invalid @llm-type 'service-shared'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/services/shared/paths.py:2
**Element**: unknown
**Issue**: Missing required @llm-does tag for service-utilities
**Type**: missing_tag

### .llmdocs-backup/services/shared/paths.py:2
**Element**: unknown
**Issue**: Invalid @llm-type 'service-utilities'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/services/shared/paths.py:82
**Element**: ServicePaths
**Issue**: Missing required @llm-does tag for service-path-manager
**Type**: missing_tag

### .llmdocs-backup/services/shared/paths.py:82
**Element**: ServicePaths
**Issue**: Invalid @llm-type 'service-path-manager'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/services/speech-to-text/simple_whisper_server.py:2
**Element**: unknown
**Issue**: Missing required @llm-does tag for service
**Type**: missing_tag

### .llmdocs-backup/services/speech-to-text/__init__.py:1
**Element**: unknown
**Issue**: Missing required @llm-does tag for service
**Type**: missing_tag

### .llmdocs-backup/services/speech-to-text/main.py:2
**Element**: unknown
**Issue**: Missing required @llm-does tag for service-launcher
**Type**: missing_tag

### .llmdocs-backup/services/speech-to-text/main.py:2
**Element**: unknown
**Issue**: Invalid @llm-type 'service-launcher'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/services/speech-to-text/grpc_server.py:2
**Element**: unknown
**Issue**: Missing required @llm-does tag for service
**Type**: missing_tag

### .llmdocs-backup/services/text-to-speech/main.py:2
**Element**: unknown
**Issue**: Missing required @llm-does tag for service-launcher
**Type**: missing_tag

### .llmdocs-backup/services/text-to-speech/main.py:2
**Element**: unknown
**Issue**: Invalid @llm-type 'service-launcher'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/services/text-to-speech/grpc_server.py:2
**Element**: unknown
**Issue**: Missing required @llm-does tag for service
**Type**: missing_tag

### .llmdocs-backup/services/vision-ai/main.py:2
**Element**: unknown
**Issue**: Missing required @llm-does tag for service-launcher
**Type**: missing_tag

### .llmdocs-backup/services/vision-ai/main.py:2
**Element**: unknown
**Issue**: Invalid @llm-type 'service-launcher'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/services/vision-ai/grpc_server.py:2
**Element**: unknown
**Issue**: Missing required @llm-does tag for service
**Type**: missing_tag

### .llmdocs-backup/control/proxy_server.py:2
**Element**: unknown
**Issue**: Missing required @llm-does tag for virtualization-boundary
**Type**: missing_tag

### .llmdocs-backup/control/proxy_server.py:2
**Element**: unknown
**Issue**: Invalid @llm-type 'virtualization-boundary'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/control/conversation_cli.py:3
**Element**: unknown
**Issue**: Missing required @llm-does tag for service
**Type**: missing_tag

### .llmdocs-backup/control/service_launcher.py:2
**Element**: unknown
**Issue**: Missing required @llm-does tag for control-system
**Type**: missing_tag

### .llmdocs-backup/control/service_launcher.py:2
**Element**: unknown
**Issue**: Invalid @llm-type 'control-system'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/control/network/service_registry.py:2
**Element**: unknown
**Issue**: Missing required @llm-does tag for control-system
**Type**: missing_tag

### .llmdocs-backup/control/network/service_registry.py:2
**Element**: unknown
**Issue**: Invalid @llm-type 'control-system'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/control/network/__init__.py:1
**Element**: unknown
**Issue**: Missing required @llm-does tag for control-system
**Type**: missing_tag

### .llmdocs-backup/control/network/__init__.py:1
**Element**: unknown
**Issue**: Invalid @llm-type 'control-system'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/control/deployment/deploy.py:2
**Element**: unknown
**Issue**: Missing required @llm-does tag for control-tool
**Type**: missing_tag

### .llmdocs-backup/control/deployment/deploy.py:2
**Element**: unknown
**Issue**: Invalid @llm-type 'control-tool'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/control/deployment/deploy.py:31
**Element**: UnhingedDeploymentOrchestrator
**Issue**: Missing required @llm-does tag for control-orchestrator
**Type**: missing_tag

### .llmdocs-backup/control/deployment/deploy.py:31
**Element**: UnhingedDeploymentOrchestrator
**Issue**: Invalid @llm-type 'control-orchestrator'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/control/deployment/health-checks.py:2
**Element**: unknown
**Issue**: Missing required @llm-does tag for control-tool
**Type**: missing_tag

### .llmdocs-backup/control/deployment/health-checks.py:2
**Element**: unknown
**Issue**: Invalid @llm-type 'control-tool'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/control/deployment/health-checks.py:57
**Element**: UnhingedHealthMonitor
**Issue**: Missing required @llm-does tag for control-monitor
**Type**: missing_tag

### .llmdocs-backup/control/deployment/health-checks.py:57
**Element**: UnhingedHealthMonitor
**Issue**: Invalid @llm-type 'control-monitor'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/control/sdk/javascript/unhinged-sdk.js:1
**Element**: UnhingedSDK
**Issue**: Missing required @llm-does tag for client-sdk
**Type**: missing_tag

### .llmdocs-backup/control/sdk/javascript/unhinged-sdk.js:1
**Element**: UnhingedSDK
**Issue**: Invalid @llm-type 'client-sdk'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/control/system/__init__.py:1
**Element**: unknown
**Issue**: Missing required @llm-does tag for control-plane-package
**Type**: missing_tag

### .llmdocs-backup/control/system/__init__.py:1
**Element**: unknown
**Issue**: Invalid @llm-type 'control-plane-package'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/control/system/system_controller.py:1
**Element**: unknown
**Issue**: Missing required @llm-does tag for control-plane
**Type**: missing_tag

### .llmdocs-backup/control/system/system_controller.py:1
**Element**: unknown
**Issue**: Invalid @llm-type 'control-plane'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/control/system/operation_result.py:1
**Element**: unknown
**Issue**: Missing required @llm-does tag for data-model
**Type**: missing_tag

### .llmdocs-backup/control/system/operation_result.py:1
**Element**: unknown
**Issue**: Invalid @llm-type 'data-model'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/control/config/environments/production.yml:2
**Element**: environment
**Issue**: Missing required @llm-does tag for control-config
**Type**: missing_tag

### .llmdocs-backup/control/config/environments/production.yml:2
**Element**: environment
**Issue**: Invalid @llm-type 'control-config'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/control/config/environments/development.yml:2
**Element**: environment
**Issue**: Missing required @llm-does tag for control-config
**Type**: missing_tag

### .llmdocs-backup/control/config/environments/development.yml:2
**Element**: environment
**Issue**: Invalid @llm-type 'control-config'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/platforms/persistence/docker-compose.yml:2
**Element**: version
**Issue**: Missing required @llm-does tag for platform
**Type**: missing_tag

### .llmdocs-backup/platforms/persistence/docker-compose.yml:2
**Element**: version
**Issue**: Invalid @llm-type 'platform'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/platforms/persistence/src/main/kotlin/com/unhinged/persistence/PersistencePlatformApplication.kt:27
**Element**: PersistencePlatformApplication
**Issue**: Missing required @llm-does tag for application
**Type**: missing_tag

### .llmdocs-backup/platforms/persistence/src/main/kotlin/com/unhinged/persistence/PersistencePlatformApplication.kt:27
**Element**: PersistencePlatformApplication
**Issue**: Invalid @llm-type 'application'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/platforms/persistence/src/main/kotlin/com/unhinged/persistence/client/DatabaseClientRegistry.kt:24
**Element**: DatabaseClientRegistry
**Issue**: Missing required @llm-does tag for database-registry
**Type**: missing_tag

### .llmdocs-backup/platforms/persistence/src/main/kotlin/com/unhinged/persistence/client/DatabaseClientRegistry.kt:24
**Element**: DatabaseClientRegistry
**Issue**: Invalid @llm-type 'database-registry'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/platforms/persistence/src/main/kotlin/com/unhinged/persistence/monitoring/ObservabilityManager.kt:34
**Element**: ObservabilityManager
**Issue**: Missing required @llm-does tag for observability-manager
**Type**: missing_tag

### .llmdocs-backup/platforms/persistence/src/main/kotlin/com/unhinged/persistence/monitoring/ObservabilityManager.kt:34
**Element**: ObservabilityManager
**Issue**: Invalid @llm-type 'observability-manager'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/platforms/persistence/src/main/kotlin/com/unhinged/persistence/model/CoreModels.kt:26
**Element**: ExecutionContext
**Issue**: Missing required @llm-does tag for model
**Type**: missing_tag

### .llmdocs-backup/platforms/persistence/src/main/kotlin/com/unhinged/persistence/model/CoreModels.kt:26
**Element**: ExecutionContext
**Issue**: Invalid @llm-type 'model'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/platforms/persistence/src/main/kotlin/com/unhinged/persistence/core/OperationOrchestrator.kt:25
**Element**: OperationOrchestrator
**Issue**: Missing required @llm-does tag for interface
**Type**: missing_tag

### .llmdocs-backup/platforms/persistence/src/main/kotlin/com/unhinged/persistence/core/DatabaseProvider.kt:25
**Element**: DatabaseProvider
**Issue**: Missing required @llm-does tag for interface
**Type**: missing_tag

### .llmdocs-backup/platforms/persistence/src/main/kotlin/com/unhinged/persistence/core/QueryExecutor.kt:23
**Element**: QueryExecutor
**Issue**: Missing required @llm-does tag for interface
**Type**: missing_tag

### .llmdocs-backup/platforms/persistence/src/main/kotlin/com/unhinged/persistence/core/PersistenceManager.kt:24
**Element**: PersistenceManager
**Issue**: Missing required @llm-does tag for interface
**Type**: missing_tag

### .llmdocs-backup/platforms/persistence/src/main/kotlin/com/unhinged/persistence/impl/PersistenceManagerImpl.kt:29
**Element**: PersistenceManagerImpl
**Issue**: Missing required @llm-does tag for implementation
**Type**: missing_tag

### .llmdocs-backup/platforms/persistence/src/main/kotlin/com/unhinged/persistence/impl/PersistenceManagerImpl.kt:29
**Element**: PersistenceManagerImpl
**Issue**: Invalid @llm-type 'implementation'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/platforms/persistence/src/main/kotlin/com/unhinged/persistence/providers/RedisProvider.kt:35
**Element**: RedisProvider
**Issue**: Missing required @llm-does tag for provider
**Type**: missing_tag

### .llmdocs-backup/platforms/persistence/src/main/kotlin/com/unhinged/persistence/providers/RedisProvider.kt:35
**Element**: RedisProvider
**Issue**: Invalid @llm-type 'provider'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/platforms/persistence/src/main/kotlin/com/unhinged/persistence/providers/ProviderRegistry.kt:25
**Element**: ProviderRegistry
**Issue**: Missing required @llm-does tag for registry
**Type**: missing_tag

### .llmdocs-backup/platforms/persistence/src/main/kotlin/com/unhinged/persistence/providers/ProviderRegistry.kt:25
**Element**: ProviderRegistry
**Issue**: Invalid @llm-type 'registry'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/platforms/persistence/src/main/kotlin/com/unhinged/persistence/providers/CockroachDBProvider.kt:35
**Element**: CockroachDBProvider
**Issue**: Missing required @llm-does tag for provider
**Type**: missing_tag

### .llmdocs-backup/platforms/persistence/src/main/kotlin/com/unhinged/persistence/providers/CockroachDBProvider.kt:35
**Element**: CockroachDBProvider
**Issue**: Invalid @llm-type 'provider'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/platforms/persistence/src/main/kotlin/com/unhinged/persistence/api/PersistenceApiServer.kt:42
**Element**: PersistenceApiServer
**Issue**: Missing required @llm-does tag for api-server
**Type**: missing_tag

### .llmdocs-backup/platforms/persistence/src/main/kotlin/com/unhinged/persistence/api/PersistenceApiServer.kt:42
**Element**: PersistenceApiServer
**Issue**: Invalid @llm-type 'api-server'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/platforms/persistence/src/main/kotlin/com/unhinged/persistence/config/ConfigurationModels.kt:26
**Element**: PersistenceConfiguration
**Issue**: Missing required @llm-does tag for config
**Type**: missing_tag

### .llmdocs-backup/platforms/persistence/src/main/kotlin/com/unhinged/persistence/lifecycle/DataLifecycleManager.kt:32
**Element**: DataLifecycleManager
**Issue**: Missing required @llm-does tag for lifecycle-manager
**Type**: missing_tag

### .llmdocs-backup/platforms/persistence/src/main/kotlin/com/unhinged/persistence/lifecycle/DataLifecycleManager.kt:32
**Element**: DataLifecycleManager
**Issue**: Invalid @llm-type 'lifecycle-manager'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/platforms/persistence/config/persistence-platform.yaml:2
**Element**: persistence_platform
**Issue**: Missing required @llm-does tag for platform
**Type**: missing_tag

### .llmdocs-backup/platforms/persistence/config/persistence-platform.yaml:2
**Element**: persistence_platform
**Issue**: Invalid @llm-type 'platform'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/desktop/auto_updater.py:3
**Element**: unknown
**Issue**: Missing required @llm-does tag for service
**Type**: missing_tag

### .llmdocs-backup/libs/design_system/build/design_token_builder.py:3
**Element**: unknown
**Issue**: Missing required @llm-does tag for build-module
**Type**: missing_tag

### .llmdocs-backup/libs/design_system/build/design_token_builder.py:3
**Element**: unknown
**Issue**: Invalid @llm-type 'build-module'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/libs/design_system/build/design_token_builder.py:71
**Element**: DesignTokenBuilder
**Issue**: Missing required @llm-does tag for build-module
**Type**: missing_tag

### .llmdocs-backup/libs/design_system/build/design_token_builder.py:71
**Element**: DesignTokenBuilder
**Issue**: Invalid @llm-type 'build-module'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/libs/design_system/build/component_validator.py:2
**Element**: unknown
**Issue**: Missing required @llm-does tag for validator
**Type**: missing_tag

### .llmdocs-backup/libs/design_system/build/component_validator.py:73
**Element**: ComponentSpecificationValidator
**Issue**: Missing required @llm-does tag for validator-class
**Type**: missing_tag

### .llmdocs-backup/libs/design_system/build/component_validator.py:73
**Element**: ComponentSpecificationValidator
**Issue**: Invalid @llm-type 'validator-class'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/libs/design_system/build/component_generator.py:2
**Element**: unknown
**Issue**: Missing required @llm-does tag for build-orchestrator
**Type**: missing_tag

### .llmdocs-backup/libs/design_system/build/component_generator.py:2
**Element**: unknown
**Issue**: Invalid @llm-type 'build-orchestrator'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/libs/design_system/build/component_build_module.py:2
**Element**: unknown
**Issue**: Missing required @llm-does tag for build-module
**Type**: missing_tag

### .llmdocs-backup/libs/design_system/build/component_build_module.py:2
**Element**: unknown
**Issue**: Invalid @llm-type 'build-module'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/libs/design_system/build/component_build_module.py:59
**Element**: ComponentBuildModule
**Issue**: Missing required @llm-does tag for build-module-implementation
**Type**: missing_tag

### .llmdocs-backup/libs/design_system/build/component_build_module.py:59
**Element**: ComponentBuildModule
**Issue**: Invalid @llm-type 'build-module-implementation'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/libs/design_system/build/generators/_abstract_generator.py:2
**Element**: unknown
**Issue**: Missing required @llm-does tag for generator-interface
**Type**: missing_tag

### .llmdocs-backup/libs/design_system/build/generators/_abstract_generator.py:2
**Element**: unknown
**Issue**: Invalid @llm-type 'generator-interface'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/libs/design_system/build/generators/gtk4/generator.py:2
**Element**: unknown
**Issue**: Missing required @llm-does tag for component-generator
**Type**: missing_tag

### .llmdocs-backup/libs/design_system/build/generators/gtk4/generator.py:2
**Element**: unknown
**Issue**: Invalid @llm-type 'component-generator'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/libs/design_system/build/generators/gtk4/generator.py:169
**Element**: resolve_token
**Issue**: Missing required @llm-does tag for token-resolver
**Type**: missing_tag

### .llmdocs-backup/libs/design_system/build/generators/gtk4/generator.py:169
**Element**: resolve_token
**Issue**: Invalid @llm-type 'token-resolver'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/libs/design_system/build/generators/gtk4/generator.py:233
**Element**: unknown
**Issue**: Missing required @llm-does tag for generated-component
**Type**: missing_tag

### .llmdocs-backup/libs/design_system/build/generators/gtk4/generator.py:233
**Element**: unknown
**Issue**: Invalid @llm-type 'generated-component'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/libs/design_system/components/_schema.yaml:2
**Element**: schema_version
**Issue**: Missing required @llm-does tag for schema
**Type**: missing_tag

### .llmdocs-backup/libs/design_system/components/_schema.yaml:2
**Element**: schema_version
**Issue**: Invalid @llm-type 'schema'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/libs/design_system/components/primitives/modal.yaml:2
**Element**: component
**Issue**: Missing required @llm-does tag for component-specification
**Type**: missing_tag

### .llmdocs-backup/libs/design_system/components/primitives/modal.yaml:2
**Element**: component
**Issue**: Invalid @llm-type 'component-specification'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/libs/design_system/components/primitives/input.yaml:2
**Element**: component
**Issue**: Missing required @llm-does tag for component-specification
**Type**: missing_tag

### .llmdocs-backup/libs/design_system/components/primitives/input.yaml:2
**Element**: component
**Issue**: Invalid @llm-type 'component-specification'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/libs/design_system/components/primitives/button.yaml:2
**Element**: component
**Issue**: Missing required @llm-does tag for component-specification
**Type**: missing_tag

### .llmdocs-backup/libs/design_system/components/primitives/button.yaml:2
**Element**: component
**Issue**: Invalid @llm-type 'component-specification'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### .llmdocs-backup/libs/design_system/components/primitives/simple-button.yaml:2
**Element**: component
**Issue**: Missing required @llm-does tag for component-specification
**Type**: missing_tag

### .llmdocs-backup/libs/design_system/components/primitives/simple-button.yaml:2
**Element**: component
**Issue**: Invalid @llm-type 'component-specification'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

## ⚠️ Warnings

### build/tools/llm-docs-enforcer.py:165
**Element**: unknown
**Issue**: @llm-does too short (9 chars). Minimum: 10
**Type**: short_does

### build/tools/llm-docs-enforcer.py:170
**Element**: unknown
**Issue**: @llm-does too short (9 chars). Minimum: 10
**Type**: short_does

## ℹ️ Infos

### build/llm_integration.py:3
**Element**: unknown
**Issue**: Type 'service.api' has 22 different actions - consider more specific types
**Type**: type_action_diversity

### build/python/run.py:2
**Element**: unknown
**Issue**: Type 'config.build' has 47 different actions - consider more specific types
**Type**: type_action_diversity

### build/docs-generation/llm-context-warmer.py:35
**Element**: generate_project_overview
**Issue**: Type 'util.function' has 31 different actions - consider more specific types
**Type**: type_action_diversity

### build/docs-generation/test_llm_extraction.py:87
**Element**: test_parse_llm_tags_with_context
**Issue**: Type 'util.validator' has 8 different actions - consider more specific types
**Type**: type_action_diversity

# 🔍 LLM Comment Validation Report

## 📊 Summary

**Total Issues**: 32
**Errors**: ❌ 25
**Warnings**: ⚠️ 2
**Infos**: ℹ️ 5

## ❌ Errors

### build/cli.py:3
**Element**: unknown
**Issue**: Invalid @llm-type 'service.cli'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### build/orchestrator.py:3
**Element**: unknown
**Issue**: Invalid @llm-type 'service.orchestrator'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### build/monitoring.py:3
**Element**: unknown
**Issue**: Invalid @llm-type 'service.monitor'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### build/docs-generation/extract-llm-comments.py:2
**Element**: unknown
**Issue**: Invalid @llm-type 'util.extractor'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### build/docs-generation/extract-llm-comments.py:541
**Element**: extract_comments_from_file
**Issue**: Missing required @llm-does tag for function
**Type**: missing_tag

### build/docs-generation/extract-llm-comments.py:562
**Element**: extract_comments_from_codebase
**Issue**: Missing required @llm-does tag for function
**Type**: missing_tag

### build/docs-generation/extract-llm-comments.py:572
**Element**: parse_llm_tags
**Issue**: Missing required @llm-does tag for function
**Type**: missing_tag

### build/docs-generation/extract-llm-comments.py:597
**Element**: save_extraction_results
**Issue**: Missing required @llm-does tag for function
**Type**: missing_tag

### build/docs-generation/generate-project-structure.py:2
**Element**: unknown
**Issue**: Invalid @llm-type 'util.generator'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### build/tools/dead-code-analyzer.py:2
**Element**: unknown
**Issue**: Invalid @llm-type 'util.analyzer'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### build/tools/cleanup-dead-code.py:2
**Element**: unknown
**Issue**: Invalid @llm-type 'util.cleaner'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### build/tools/llm-docs-enforcer.py:2
**Element**: unknown
**Issue**: Invalid @llm-type 'util.enforcer'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### build/tools/llm-docs-enforcer.py:166
**Element**: unknown
**Issue**: Invalid @llm-type '{llm_type}'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### build/tools/llm-docs-enforcer.py:171
**Element**: unknown
**Issue**: Invalid @llm-type '{llm_type}'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### build/modules/typescript_builder.py:3
**Element**: unknown
**Issue**: Invalid @llm-type 'service.builder'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### build/modules/__init__.py:1
**Element**: unknown
**Issue**: Invalid @llm-type 'service.framework'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### build/modules/c_builder.py:3
**Element**: unknown
**Issue**: Invalid @llm-type 'service.builder'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### build/modules/python_builder.py:3
**Element**: unknown
**Issue**: Invalid @llm-type 'service.builder'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### build/modules/service_discovery_builder.py:3
**Element**: unknown
**Issue**: Invalid @llm-type 'service.builder'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### build/modules/polyglot_proto_engine.py:3
**Element**: unknown
**Issue**: Invalid @llm-type 'service.builder'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### build/modules/kotlin_builder.py:3
**Element**: unknown
**Issue**: Invalid @llm-type 'service.builder'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### build/validators/__init__.py:1
**Element**: unknown
**Issue**: Invalid @llm-type 'service.validator'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### vm/docs/unhinged-os-architecture.py:2
**Element**: unknown
**Issue**: Invalid @llm-type 'architecture.system/unhinged-os-design'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### vm/docs/unhinged-os-development.py:2
**Element**: unknown
**Issue**: Invalid @llm-type 'development.workflow/unhinged-os-development'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

### vm/docs/unhinged-os-build-system.py:2
**Element**: unknown
**Issue**: Invalid @llm-type 'build.documentation/unhinged-os-build-system'. Valid types: class, component, component.complex, component.container, component.primitive, component.spec, config, config.app, config.build, config.deploy, config.env, constant, contract, endpoint, entity, function, interface, misc.control-monitor, misc.control-orchestrator, misc.control-plane, misc.control-plane-package, misc.control-system, misc.control-tool, misc.platform, misc.virtualization-boundary, model.config, model.dto, model.entity, model.schema, repository, service, service.api, service.launcher, service.shared, service.util, service.worker, test, tool, type-definition, util.cli, util.converter, util.executor, util.formatter, util.function, util.migrator, util.parser, util.runner, util.setup, util.tool, util.validator, validator
**Type**: invalid_type

## ⚠️ Warnings

### build/tools/llm-docs-enforcer.py:166
**Element**: unknown
**Issue**: @llm-does too short (9 chars). Minimum: 10
**Type**: short_does

### build/tools/llm-docs-enforcer.py:171
**Element**: unknown
**Issue**: @llm-does too short (9 chars). Minimum: 10
**Type**: short_does

## ℹ️ Infos

### build/llm_integration.py:3
**Element**: unknown
**Issue**: Type 'service.api' has 14 different actions - consider more specific types
**Type**: type_action_diversity

### build/python/setup.py:23
**Element**: UnhingedPythonSetup
**Issue**: Type 'config.build' has 39 different actions - consider more specific types
**Type**: type_action_diversity

### build/docs-generation/llm-context-warmer.py:35
**Element**: generate_project_overview
**Issue**: Type 'util.function' has 28 different actions - consider more specific types
**Type**: type_action_diversity

### build/docs-generation/test_llm_extraction.py:87
**Element**: test_parse_llm_tags_with_context
**Issue**: Type 'util.validator' has 12 different actions - consider more specific types
**Type**: type_action_diversity

### build/modules/typescript_builder.py:3
**Element**: unknown
**Issue**: Type 'service.builder' has 6 different actions - consider more specific types
**Type**: type_action_diversity

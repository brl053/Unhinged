# Proto-to-Polyglot Client Libraries Build Pipeline

## Overview

This document describes the implementation of a comprehensive proto-to-polyglot client library generation pipeline integrated into the Unhinged custom build system. The pipeline generates type-safe client libraries for multiple programming languages from protobuf service definitions.

## Architecture

### Core Components

1. **ProtoClientBuilder** (`build/modules/proto_client_builder.py`)
   - Implements `BuildModule` interface
   - Generates clients for TypeScript, JavaScript, Python, Kotlin, Go
   - Provides intelligent caching and dependency tracking
   - Integrates with build orchestrator for parallel execution

2. **API Registry Generator** (Embedded in ProtoClientBuilder)
   - Generates `generated/static_html/api-clients.js` (referenced directly by HTML files)
   - Provides service discovery for browser consumption
   - Creates unified client interface for tab system

3. **API Tab Integration** (`control/static_html/shared/api-integration.js`)
   - Bridges generated clients with tab system
   - Provides error handling and retry logic
   - Implements health monitoring and connection management

4. **Build Script** (`scripts/build-proto-clients.sh`)
   - Standalone script for proto client generation
   - Supports multiple languages and build options
   - Provides validation and environment checking

## Implementation Details

### Build Module Integration

The `ProtoClientBuilder` is registered with the build system in `build/cli.py`:

```python
from .modules.proto_client_builder import ProtoClientBuilder
proto_client_builder = ProtoClientBuilder(context)
register_module(proto_client_builder)
```

### Build Targets

Added to `build-config.yml`:

- `proto-clients`: Generate TypeScript and JavaScript clients (default)
- `proto-clients-all`: Generate clients for all supported languages
- `proto-clients-typescript`: TypeScript clients only
- `proto-clients-javascript`: JavaScript clients only
- `proto-clients-python`: Python clients only
- `proto-clients-kotlin`: Kotlin clients only
- `proto-clients-go`: Go clients only

### Language-Specific Generation

#### TypeScript
- Uses `ts-proto` plugin
- Generates gRPC-Web compatible clients
- Output: `generated/typescript/clients/`
- Features: Type safety, async/await support, streaming

#### JavaScript
- Uses `protoc-gen-grpc-web` plugin
- Browser-compatible clients
- Output: `generated/javascript/clients/`
- Features: CommonJS modules, gRPC-Web transport

#### Python
- Uses standard `protoc` Python plugin
- Backend service clients
- Output: `generated/python/clients/`
- Features: Standard gRPC Python bindings

#### Kotlin
- Uses `protoc-gen-kotlin` plugin
- JVM service clients
- Output: `generated/kotlin/clients/`
- Features: Coroutine support, type safety

#### Go
- Uses `protoc-gen-go` plugin
- Microservice clients
- Output: `generated/go/clients/`
- Features: Standard Go gRPC bindings

## Usage

### Via Build System

```bash
# Generate TypeScript and JavaScript clients (default)
python3 build/build.py build proto-clients

# Generate clients for all languages
python3 build/build.py build proto-clients-all

# Generate specific language clients
python3 build/build.py build proto-clients-typescript
python3 build/build.py build proto-clients-python

# With build options
python3 build/build.py build proto-clients --parallel --no-cache
```

### Via Standalone Script

```bash
# Default: TypeScript and JavaScript
./scripts/build-proto-clients.sh

# All languages
./scripts/build-proto-clients.sh --all-languages

# Specific languages
./scripts/build-proto-clients.sh --languages typescript,python

# With options
./scripts/build-proto-clients.sh --verbose --no-cache
```

### In Tab System

```javascript
// Get service client
const chatClient = window.UnhingedAPI.getClient('chat');

// Call service method
const response = await chatClient.call('CreateConversation', {
    title: 'New Conversation',
    participants: ['user1', 'user2']
});

// Via tab system integration
const tabSystem = new UnhingedComponents.TabSystem(container);
const result = await tabSystem.callService('llm', 'GenerateCompletion', {
    prompt: 'Hello, world!',
    max_tokens: 100
});
```

## Dependencies

### System Requirements
- `protoc` (Protocol Buffers compiler)
- `npm` (Node.js package manager)
- `python3` with `pyyaml` and `psutil`

### Language-Specific Tools
- **TypeScript**: `ts-proto` (auto-installed via npm)
- **JavaScript**: `protoc-gen-grpc-web` (optional, for enhanced features)
- **Python**: Standard protoc Python plugin
- **Kotlin**: `protoc-gen-kotlin` (requires Kotlin toolchain)
- **Go**: `protoc-gen-go` (requires Go toolchain)

## Integration Points

### With Existing Build System
- Extends `BuildModule` interface
- Uses build orchestrator for dependency tracking
- Leverages intelligent caching system
- Supports parallel execution

### With Tab System
- Generates browser-compatible API registry
- Provides seamless service integration
- Implements error handling and retry logic
- Supports health monitoring

### With Control Plane
- Integrates with static HTML interfaces
- Provides unified service access
- Supports real-time status monitoring
- Enables dynamic service discovery

## Caching Strategy

The pipeline implements content-based caching:

1. **Cache Key Calculation**
   - Hashes all `.proto` files
   - Includes build configuration
   - Considers target-specific options

2. **Incremental Builds**
   - Only regenerates when proto files change
   - Supports per-language incremental updates
   - Maintains dependency tracking

3. **Cache Invalidation**
   - Automatic on proto file changes
   - Manual via `--no-cache` flag
   - Smart invalidation for configuration changes

## Error Handling

### Build-Time Errors
- Environment validation before generation
- Tool availability checking
- Dependency resolution
- Clear error messages with remediation steps

### Runtime Errors
- Service connection failures
- Method call timeouts
- Automatic retry with exponential backoff
- Health monitoring and status reporting

## Performance Optimizations

1. **Parallel Generation**
   - Multiple languages generated concurrently
   - Parallel protoc invocations
   - Optimized for multi-core systems

2. **Intelligent Caching**
   - Content-based cache keys
   - Incremental updates
   - Fast cache validation

3. **Lazy Loading**
   - Clients instantiated on demand
   - Connection pooling
   - Resource optimization

## Future Enhancements

1. **Enhanced gRPC-Web Support**
   - Streaming support for browsers
   - Advanced authentication
   - Custom transport options

2. **Service Mesh Integration**
   - Istio/Envoy compatibility
   - Load balancing
   - Circuit breaker patterns

3. **Advanced Monitoring**
   - Metrics collection
   - Distributed tracing
   - Performance analytics

4. **Code Generation Optimization**
   - Template-based generation
   - Custom annotations
   - Advanced type mappings

## Troubleshooting

### Common Issues

1. **Missing Dependencies**
   ```bash
   pip install pyyaml psutil
   npm install ts-proto
   ```

2. **Protoc Not Found**
   ```bash
   # macOS
   brew install protobuf
   
   # Ubuntu
   sudo apt-get install protobuf-compiler
   ```

3. **Permission Errors**
   ```bash
   chmod +x scripts/build-proto-clients.sh
   ```

4. **Cache Issues**
   ```bash
   python3 build/build.py build proto-clients --no-cache
   ```

### Debug Mode

Enable verbose logging:
```bash
python3 build/build.py build proto-clients --verbose
./scripts/build-proto-clients.sh --verbose
```

## Contributing

When adding new language support:

1. Add language configuration to `client_configs` in `ProtoClientBuilder`
2. Implement `_generate_<language>_clients()` method
3. Add build target to `build-config.yml`
4. Update documentation and tests
5. Ensure proper error handling and validation

## Conclusion

The proto-to-polyglot client libraries build pipeline provides a comprehensive solution for generating type-safe client libraries from protobuf service definitions. It integrates seamlessly with the existing build system while providing advanced features like intelligent caching, parallel execution, and browser integration through the tab system.

The pipeline supports the distributed systems architecture by enabling consistent service communication across multiple programming languages and deployment environments, while maintaining the flexibility and performance required for a modern microservices platform.

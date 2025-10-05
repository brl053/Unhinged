# Protocol Buffer Definitions

This directory contains the protobuf schema definitions for the Unhinged system.

## ⚠️ Generated Files Policy

**Generated files are NOT committed to git.** All protobuf-generated code is excluded from version control and must be generated locally or in CI/CD.

### Why Generated Files Are Excluded:

1. **Source of Truth**: `.proto` files are the single source of truth
2. **Platform Differences**: Generated code varies by platform/compiler version
3. **Merge Conflicts**: Generated files create unnecessary merge conflicts
4. **Build Reproducibility**: Forces proper build process setup
5. **Repository Size**: Keeps repository lean and focused

## Schema Files

### `document_store.proto`
Complete document store API with:
- Document CRUD operations with versioning
- Tag-based version management
- Session context queries for LLM integration
- Batch operations and health checks

### `google/protobuf/`
Standard Google protobuf types (timestamp, struct, etc.)

## Code Generation

### Prerequisites
```bash
# Install protoc (Protocol Buffers compiler)
# Already installed locally in ~/bin/protoc

# Install ts-proto for TypeScript generation
npm install ts-proto --save-dev
```

### Generate All Bindings
```bash
# From project root
./proto/build.sh
```

### Manual Generation

#### Frontend (TypeScript)
```bash
protoc \
  --plugin=protoc-gen-ts_proto=./node_modules/.bin/protoc-gen-ts_proto \
  --ts_proto_out=./frontend/src/types/generated \
  --ts_proto_opt=esModuleInterop=true \
  --ts_proto_opt=forceLong=string \
  --ts_proto_opt=useOptionals=messages \
  --proto_path=./proto \
  ./proto/document_store.proto
```

#### Backend (Kotlin)
```bash
protoc \
  --kotlin_out=./backend/src/main/kotlin \
  --java_out=./backend/src/main/kotlin \
  --proto_path=./proto \
  ./proto/document_store.proto
```

## Generated File Locations

### Frontend (TypeScript)
- `frontend/src/types/generated/document_store.ts`
- `frontend/src/types/generated/google/protobuf/`

### Backend (Kotlin)
- `backend/src/main/kotlin/unhinged/document_store/`
- Includes both Kotlin DSL (.kt) and Java classes (.java)

## Usage Examples

### Frontend (TypeScript)
```typescript
import { 
  Document, 
  PutDocumentRequest, 
  GetSessionContextRequest 
} from '../types/generated/document_store';

const document: Document = {
  documentUuid: crypto.randomUUID(),
  type: 'llm_interaction',
  name: 'User Query',
  namespace: 'default',
  version: 1,
  bodyJson: JSON.stringify({ query: 'Hello world' }),
  metadata: { userId: '123' },
  tags: ['latest'],
  createdAt: new Date(),
  createdBy: 'user',
  createdByType: 'human',
  sessionId: 'session-123'
};
```

### Backend (Kotlin)
```kotlin
import unhinged.document_store.*

val document = document {
    documentUuid = UUID.randomUUID().toString()
    type = "llm_interaction"
    name = "User Query"
    namespace = "default"
    version = 1
    bodyJson = """{"query": "Hello world"}"""
    // ... other fields
}
```

## Development Workflow

1. **Modify Schema**: Edit `.proto` files
2. **Generate Code**: Run `./proto/build.sh`
3. **Implement**: Use generated types in your code
4. **Test**: Verify compatibility across services
5. **Commit**: Only commit `.proto` files, never generated code

## CI/CD Integration

Generated files should be created during build process:

```yaml
# Example GitHub Actions step
- name: Generate Protobuf Code
  run: |
    export PATH="$HOME/bin:$PATH"
    ./proto/build.sh
```

## Troubleshooting

### Missing protoc
```bash
# Download and install protoc locally
cd /tmp
wget https://github.com/protocolbuffers/protobuf/releases/download/v25.1/protoc-25.1-linux-x86_64.zip
unzip protoc-25.1-linux-x86_64.zip
mkdir -p ~/bin
cp bin/protoc ~/bin/
chmod +x ~/bin/protoc
export PATH="$HOME/bin:$PATH"
```

### Missing ts-proto
```bash
npm install ts-proto --save-dev
```

### Import Errors
Ensure Google protobuf includes are available:
```bash
mkdir -p proto/google/protobuf
cp /tmp/include/google/protobuf/*.proto proto/google/protobuf/
```

## Best Practices

1. **Version Compatibility**: Keep protobuf schemas backward compatible
2. **Field Numbers**: Never reuse field numbers
3. **Optional Fields**: Use optional for new fields
4. **Documentation**: Document all messages and fields
5. **Validation**: Validate generated code in tests
6. **Naming**: Use consistent naming conventions across languages

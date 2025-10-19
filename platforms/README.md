# Unhinged Platforms

This directory contains the **platform-level services** that provide complex, multi-technology abstractions and orchestration capabilities. Platforms are distinguished from simple services by their complexity, multi-technology integration, and comprehensive feature sets.

## 🏗️ Architecture Distinction

### **Platforms** (Complex Service Offerings)
- **Multi-technology integration** - Abstract multiple underlying technologies
- **Complex orchestration** - Coordinate workflows across multiple systems
- **Comprehensive APIs** - Provide rich, feature-complete interfaces
- **Self-contained deployment** - Include their own Docker configurations
- **Advanced capabilities** - Lifecycle management, observability, routing, etc.

### **Services** (Simple, Single-Purpose Offerings)
- **Single technology focus** - Wrap one specific capability
- **Simple interfaces** - Straightforward request/response patterns  
- **Focused functionality** - Do one thing very well
- **Lightweight deployment** - Minimal resource requirements
- **Clear boundaries** - Well-defined input/output contracts

## 🚀 Current Platforms

### **Persistence Platform** (`persistence/`)
A centralized, multi-technology persistence platform that abstracts database complexity behind unified APIs.

**Technologies Integrated:**
- Redis (caching, sessions)
- CockroachDB (distributed SQL)
- MongoDB (document store)
- Weaviate (vector database)
- Elasticsearch (search & analytics)
- Cassandra (wide-column store)
- Neo4j (graph database)
- Data Lake (OLAP warehouse)

**Key Capabilities:**
- Unified CRUD operations across all database technologies
- Intelligent data routing based on access patterns
- Automatic hot/warm/cold data tiering
- Vector search and semantic operations
- Graph traversal and relationship queries
- Distributed transactions across technologies
- Comprehensive observability and monitoring
- Data lifecycle management and retention policies

**API Endpoints:**
- REST API: `http://localhost:8090/api/v1`
- gRPC API: `localhost:9090`
- Health: `http://localhost:8090/api/v1/health`
- Metrics: `http://localhost:8090/api/v1/metrics`

## 🔮 Planned Platforms

### **Agent Platform** (`agent/` - Future)
A comprehensive AI agent orchestration platform that manages agent lifecycles, capabilities, and interactions.

**Planned Capabilities:**
- Agent lifecycle management (creation, deployment, scaling)
- Multi-modal agent coordination (text, voice, vision)
- Agent capability discovery and routing
- Inter-agent communication protocols
- Agent performance monitoring and optimization
- Dynamic agent composition and workflows

### **Workflow Platform** (`workflow/` - Future)
A sophisticated workflow orchestration platform for complex business processes and automation.

**Planned Capabilities:**
- Visual workflow designer and execution engine
- Multi-step process orchestration
- Human-in-the-loop workflow support
- Conditional branching and parallel execution
- Workflow versioning and rollback
- Integration with external systems and APIs
- Workflow analytics and optimization

## 🔧 Development Guidelines

### **When to Create a Platform**
Create a new platform when you need to:
- Integrate multiple underlying technologies
- Provide complex orchestration capabilities
- Abstract significant complexity from applications
- Offer comprehensive lifecycle management
- Support advanced observability and monitoring

### **When to Create a Service**
Create a simple service when you need to:
- Wrap a single technology or capability
- Provide a focused, well-defined function
- Offer lightweight, fast operations
- Maintain clear, simple interfaces
- Support high-throughput, low-latency operations

### **Platform Structure**
Each platform should include:
```
platforms/[platform-name]/
├── src/                    # Source code
├── config/                 # Configuration files
├── scripts/                # Deployment and utility scripts
├── Dockerfile             # Container definition
├── docker-compose.yml     # Development environment
├── build.gradle.kts       # Build configuration (if applicable)
├── README.md              # Platform documentation
└── monitoring/            # Observability configuration
```

### **Integration Patterns**
- **Configuration-driven** - Use declarative YAML/JSON configuration
- **API-first** - Provide both REST and gRPC interfaces
- **Observable** - Include comprehensive metrics, tracing, and health checks
- **Scalable** - Support horizontal scaling and load balancing
- **Resilient** - Include circuit breakers, retries, and graceful degradation

## 🚀 Getting Started

### **Running All Platforms**
```bash
# Start all platforms with their dependencies
docker-compose -f platforms/docker-compose.all.yml up -d
```

### **Running Individual Platforms**
```bash
# Start persistence platform
cd platforms/persistence
docker-compose up -d

# Start agent platform (when available)
cd platforms/agent
docker-compose up -d

# Start workflow platform (when available)
cd platforms/workflow
docker-compose up -d
```

### **Development**
```bash
# Build all platforms
make build-platforms

# Test all platforms
make test-platforms

# Deploy all platforms
make deploy-platforms
```

## 📊 Monitoring

Each platform includes comprehensive observability:
- **Metrics** - Prometheus metrics for performance monitoring
- **Tracing** - Distributed tracing with Jaeger
- **Logging** - Structured logging with correlation IDs
- **Health Checks** - Kubernetes-ready health and readiness probes
- **Dashboards** - Grafana dashboards for operational visibility

## 🤝 Contributing

When contributing to platforms:
1. Follow the platform structure guidelines
2. Include comprehensive tests (unit, integration, performance)
3. Add observability instrumentation
4. Update documentation and API specifications
5. Ensure Docker and Kubernetes compatibility

## 📄 License

All platforms are licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

---

**Platforms provide the foundation for Unhinged's complex capabilities, abstracting multi-technology complexity behind unified, powerful APIs.**

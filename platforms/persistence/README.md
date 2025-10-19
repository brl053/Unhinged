# Unhinged Persistence Platform

A centralized, multi-technology persistence platform that abstracts database complexity behind unified APIs, enabling self-service data operations across multiple database technologies.

> **Platform Architecture**: This is a **platform-level service** that provides complex, multi-technology abstractions. It integrates 8 different database technologies behind a unified API, unlike simple services that focus on single capabilities.

## 🚀 Overview

The Unhinged Persistence Platform provides a **blackbox abstraction layer** that enables applications to interact with multiple database technologies through a single, unified API. It supports intelligent routing, automatic caching, data lifecycle management, and cross-technology operations.

### Supported Database Technologies

- **Redis** - High-performance caching and session storage
- **CockroachDB** - Distributed SQL for transactional data
- **MongoDB** - Document-oriented NoSQL for flexible schemas
- **Weaviate** - Vector database for AI/ML embeddings and semantic search
- **Elasticsearch** - Full-text search and analytics
- **Cassandra** - Wide-column store for time-series and high-write workloads
- **Neo4j** - Graph database for relationship modeling
- **Data Lake** - OLAP capabilities with Apache Iceberg

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Application Services                         │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Persistence Platform Service                    │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │              Unified API Layer                              ││
│  │    REST API    │    gRPC API    │   GraphQL API             ││
│  └─────────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────────┐│
│  │            Configuration Management                         ││
│  │   YAML Config  │  Schema Validation  │  Dynamic Updates    ││
│  └─────────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────────┐│
│  │              Query & Operation Router                       ││
│  │  Smart Routing │ Load Balancing │ Caching │ Transactions   ││
│  └─────────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────────┐│
│  │            Data Lifecycle Management                        ││
│  │   Hot/Warm/Cold │  Archival  │  Retention  │  Migration    ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                Database Technology Providers                    │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐    │
│ │  Redis  │ │  CRDB   │ │ MongoDB │ │Weaviate │ │Elastic  │    │
│ │Provider │ │Provider │ │Provider │ │Provider │ │Provider │    │
│ └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘    │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐                            │
│ │Cassandra│ │  Neo4j  │ │DataLake │                            │
│ │Provider │ │Provider │ │Provider │                            │
│ └─────────┘ └─────────┘ └─────────┘                            │
└─────────────────────────────────────────────────────────────────┘
```

## 🎯 Key Features

### Self-Service Configuration
- **Declarative YAML Configuration** - Define databases, tables, queries, and operations
- **Automatic Provisioning** - Database and table creation based on configuration
- **Schema Validation** - JSON Schema validation for configuration files
- **Dynamic Updates** - Hot-reload configuration changes

### Intelligent Data Routing
- **Access Pattern Analysis** - Route data to optimal technologies based on usage
- **Hot/Warm/Cold Tiering** - Automatic data movement based on access frequency
- **Technology-Agnostic APIs** - Applications don't need to know about underlying databases

### Unified Operations
- **CRUD Operations** - Consistent create, read, update, delete across all technologies
- **Complex Queries** - Named queries with caching and optimization
- **Distributed Transactions** - ACID transactions across multiple technologies
- **Batch Operations** - Efficient bulk data operations

### Advanced Capabilities
- **Vector Search** - Semantic search and similarity operations
- **Graph Traversal** - Relationship queries and path finding
- **Full-Text Search** - Content discovery and analytics
- **Time-Series Operations** - High-performance event and metrics storage

### Observability & Monitoring
- **Comprehensive Metrics** - Per-technology and platform-wide metrics
- **Distributed Tracing** - Request tracing across all database operations
- **Health Monitoring** - Real-time health checks and alerting
- **Performance Analytics** - Query performance analysis and optimization

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Java 17+ (for local development)
- Gradle 8+ (for building)

### Using Docker Compose

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd persistence-platform
   ```

2. **Start all services**
   ```bash
   docker-compose up -d
   ```

3. **Verify the platform is running**
   ```bash
   curl http://localhost:8090/api/v1/health
   ```

4. **Access the services**
   - **REST API**: http://localhost:8090/api/v1
   - **Health Check**: http://localhost:8090/api/v1/health
   - **Metrics**: http://localhost:8090/api/v1/metrics
   - **Grafana Dashboard**: http://localhost:3000 (admin/admin)
   - **Prometheus**: http://localhost:9090

### Local Development

1. **Build the application**
   ```bash
   ./gradlew build
   ```

2. **Run with development profile**
   ```bash
   ./gradlew dev
   ```

3. **Run tests**
   ```bash
   ./gradlew test integrationTest
   ```

## 📋 Configuration

The platform is configured through a comprehensive YAML file that defines all aspects of the persistence layer.

### Example Configuration

```yaml
persistence_platform:
  version: "2.1.0"
  
  # Database technologies
  technologies:
    redis:
      type: "cache"
      clusters: ["redis-cache"]
      use_cases: ["caching", "sessions"]
      
    cockroachdb:
      type: "newsql"
      clusters: ["crdb-primary"]
      use_cases: ["transactional", "relational"]
  
  # Logical databases
  databases:
    user_data:
      primary_technology: "cockroachdb"
      use_case: "user_profiles"
      
    session_store:
      primary_technology: "redis"
      use_case: "user_sessions"
  
  # Table definitions
  tables:
    users:
      database: "user_data"
      technology: "cockroachdb"
      schema:
        id: { type: "uuid", primary_key: true }
        email: { type: "string", unique: true, indexed: true }
        profile: { type: "jsonb" }
  
  # Named queries
  queries:
    get_user_by_id:
      table: "users"
      type: "point_lookup"
      parameters: ["user_id"]
      cache_strategy: "redis_aside"
      cache_ttl: "5m"
```

See [config/README.md](config/README.md) for complete configuration documentation.

## 🔌 API Usage

### REST API Examples

#### Create a User
```bash
curl -X POST http://localhost:8090/api/v1/tables/users \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "profile": {"name": "John Doe", "age": 30}
  }'
```

#### Execute a Named Query
```bash
curl -X POST http://localhost:8090/api/v1/query/get_user_by_id \
  -H "Content-Type: application/json" \
  -d '{"parameters": {"user_id": "123e4567-e89b-12d3-a456-426614174000"}}'
```

#### Vector Search
```bash
curl -X POST http://localhost:8090/api/v1/vector/search/documents \
  -H "Content-Type: application/json" \
  -d '{
    "queryVector": [0.1, 0.2, 0.3, ...],
    "limit": 10,
    "threshold": 0.7
  }'
```

#### Execute Complex Operation
```bash
curl -X POST http://localhost:8090/api/v1/operations/create_user_complete \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {
      "email": "user@example.com",
      "profile": {"name": "John Doe"}
    }
  }'
```

### gRPC API

The platform also provides gRPC APIs for high-performance applications. See the proto definitions in `src/main/proto/`.

## 🧪 Testing

### Unit Tests
```bash
./gradlew test
```

### Integration Tests
```bash
./gradlew integrationTest
```

### Performance Tests
```bash
./gradlew performanceTest
```

### Manual Testing with Docker
```bash
# Start test environment
docker-compose -f docker-compose.test.yml up -d

# Run integration tests
./gradlew integrationTest

# Cleanup
docker-compose -f docker-compose.test.yml down -v
```

## 📊 Monitoring

### Metrics

The platform exposes comprehensive metrics through:
- **Prometheus metrics** at `/api/v1/metrics`
- **Custom dashboards** in Grafana
- **Health checks** at `/api/v1/health`

### Key Metrics
- Query latency (P50, P95, P99)
- Throughput per technology
- Error rates and success rates
- Cache hit ratios
- Connection pool utilization
- Resource usage (CPU, memory, disk)

### Alerting

Configure alerts in Prometheus for:
- High query latency (>1000ms P99)
- High error rate (>1%)
- Low cache hit ratio (<80%)
- Resource exhaustion (>90% usage)

## 🔧 Development

### Project Structure
```
persistence-platform/
├── src/main/kotlin/com/unhinged/persistence/
│   ├── core/                 # Core interfaces
│   ├── impl/                 # Main implementations
│   ├── providers/            # Database providers
│   ├── api/                  # REST/gRPC APIs
│   ├── config/               # Configuration models
│   └── model/                # Data models
├── config/                   # Configuration files
├── scripts/                  # Deployment scripts
├── monitoring/               # Monitoring configs
└── docker-compose.yml        # Development environment
```

### Adding a New Database Provider

1. **Implement DatabaseProvider interface**
   ```kotlin
   class MyDatabaseProvider : DatabaseProvider {
       override val technologyType = TechnologyType.MY_TYPE
       override val providerName = "mydatabase"
       // ... implement all methods
   }
   ```

2. **Register in ProviderRegistry**
   ```kotlin
   registerProvider(TechnologyType.MY_TYPE) { MyDatabaseProvider() }
   ```

3. **Add configuration support**
   ```yaml
   technologies:
     mydatabase:
       type: "my_type"
       # ... configuration
   ```

4. **Add to Docker Compose**
   ```yaml
   mydatabase:
     image: mydatabase:latest
     # ... service configuration
   ```

### Code Quality

- **Kotlin coding standards** with ktlint
- **Comprehensive testing** with JUnit 5 and MockK
- **Documentation** with KDoc
- **Static analysis** with detekt

## 🚀 Deployment

### Production Deployment

1. **Build production image**
   ```bash
   ./gradlew buildDocker
   ```

2. **Deploy with Docker Compose**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Kubernetes deployment**
   ```bash
   kubectl apply -f k8s/
   ```

### Environment Configuration

- **Development**: Single-node setup with minimal resources
- **Staging**: Multi-node setup with production-like configuration
- **Production**: High-availability setup with clustering and replication

### Scaling

- **Horizontal scaling**: Multiple persistence platform instances
- **Database scaling**: Technology-specific clustering and sharding
- **Load balancing**: API gateway with intelligent routing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow Kotlin coding conventions
- Write comprehensive tests
- Update documentation
- Ensure all checks pass (`./gradlew check`)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs/](docs/)
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Wiki**: GitHub Wiki

## 🗺️ Roadmap

### Version 1.1
- [ ] GraphQL API support
- [ ] Advanced caching strategies
- [ ] Query optimization engine
- [ ] Real-time data streaming

### Version 1.2
- [ ] Multi-tenant support
- [ ] Advanced security features
- [ ] Machine learning integration
- [ ] Data governance tools

### Version 2.0
- [ ] Serverless deployment support
- [ ] Edge computing integration
- [ ] Advanced analytics platform
- [ ] AI-powered optimization

---

**Built with ❤️ by the Unhinged Team**

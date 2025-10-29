# Persistence Platform Configuration

This directory contains the configuration system for the Unhinged Persistence Platform - a centralized, multi-technology data platform that abstracts database complexity behind unified APIs.

## Overview

The persistence platform provides a **declarative, self-service** approach to data management across multiple database technologies:

- **Redis** - High-performance caching and session storage
- **CockroachDB** - Distributed SQL for transactional data
- **MongoDB** - Document-oriented NoSQL for flexible schemas
- **Weaviate** - Vector database for AI/ML embeddings and semantic search
- **Elasticsearch** - Full-text search and analytics
- **Cassandra** - Wide-column store for time-series and high-write workloads
- **Neo4j** - Graph database for relationship modeling
- **Data Lake** - OLAP capabilities with Apache Iceberg

## Configuration Files

### `persistence-platform.yaml`
The main configuration file that defines:
- **Technologies**: Database technology configurations and clusters
- **Databases**: Logical database definitions with technology mappings
- **Tables**: Schema definitions with access patterns
- **Queries**: Named queries with caching and optimization hints
- **Operations**: Complex operations including distributed transactions
- **Routing**: Data placement rules based on access patterns
- **Lifecycle**: Data retention, archival, and migration policies
- **API**: REST/gRPC endpoint configurations
- **Monitoring**: Metrics, alerts, and observability settings

### `schema.json`
JSON Schema for validating the YAML configuration to ensure:
- Required fields are present
- Data types are correct
- Enum values are valid
- Patterns match expected formats

## Key Concepts

### Self-Service Data Operations

The configuration enables complete self-service for:

1. **Database Provisioning**: Define new databases with technology selection
2. **Table Creation**: Specify schemas with automatic optimization
3. **Query Definition**: Named queries with caching strategies
4. **Operation Orchestration**: Complex multi-technology operations
5. **Data Lifecycle**: Automatic archival and retention policies

### Technology-Agnostic APIs

Applications interact with the persistence platform through unified APIs:

```yaml
# Define a table that automatically uses the best technology
users:
  database: "user_data"
  technology: "cockroachdb"  # Platform chooses optimal technology
  schema:
    id: { type: "uuid", primary_key: true }
    email: { type: "string", unique: true, indexed: true }
    profile: { type: "jsonb" }
```

### Intelligent Data Routing

Data is automatically placed in optimal technologies based on:

```yaml
routing:
  hot_data:
    criteria: "accessed_within_24h"
    technologies: ["redis", "cockroachdb"]
    
  analytical:
    criteria: "olap_workload"
    technologies: ["datalake", "elasticsearch"]
```

### Cross-Technology Operations

Complex operations span multiple technologies seamlessly:

```yaml
operations:
  create_user_complete:
    type: "distributed_transaction"
    steps:
      - { table: "users", operation: "insert", technology: "cockroachdb" }
      - { operation: "create_graph_node", technology: "neo4j" }
      - { operation: "create_search_index", technology: "elasticsearch" }
```

## Usage Examples

### 1. Adding a New Table

```yaml
# Add to tables section
new_feature_data:
  database: "feature_store"
  technology: "mongodb"  # Flexible schema for rapid development
  schema:
    feature_id: { type: "string", primary_key: true }
    data: { type: "object" }  # Flexible structure
    created_at: { type: "date", indexed: true }
```

### 2. Defining a Query

```yaml
# Add to queries section
get_recent_features:
  table: "new_feature_data"
  type: "range_scan"
  parameters: ["start_date", "limit"]
  cache_strategy: "redis_aside"
  cache_ttl: "5m"
```

### 3. Creating an API Endpoint

```yaml
# Add to api.endpoints section
"/api/v1/features":
  operations: ["get_recent_features"]
  rate_limit: "100/hour"
  authentication: "required"
```

## Configuration Validation

Validate your configuration using the JSON schema:

```bash
# Install a YAML/JSON schema validator
npm install -g ajv-cli

# Validate the configuration
ajv validate -s schema.json -d persistence-platform.yaml
```

## Environment-Specific Configuration

The configuration supports environment-specific overrides:

```yaml
environments:
  development:
    technologies:
      redis: { replicas: 1, memory: "512MB" }
      
  production:
    technologies:
      redis: { replicas: 3, memory: "4GB" }
```

## Best Practices

### 1. Technology Selection
- **Redis**: Session data, caching, real-time features
- **CockroachDB**: Financial data, user profiles, ACID requirements
- **MongoDB**: Content management, flexible schemas, rapid prototyping
- **Weaviate**: AI embeddings, semantic search, recommendations
- **Elasticsearch**: Full-text search, log analytics, metrics
- **Cassandra**: Time-series data, high-write workloads, IoT
- **Neo4j**: Social networks, recommendations, fraud detection
- **Data Lake**: Analytics, reporting, long-term storage

### 2. Schema Design
- Use appropriate data types for each technology
- Define access patterns to optimize indexing
- Consider data lifecycle from the start

### 3. Query Optimization
- Use caching for frequently accessed data
- Define appropriate cache TTLs
- Consider read/write patterns

### 4. Data Lifecycle
- Plan retention policies early
- Use hot/warm/cold storage tiers
- Automate archival processes

## Integration with Unhinged

The persistence platform integrates with the existing Unhinged architecture:

- **Backend Services**: Use persistence platform APIs instead of direct database access
- **Event System**: Automatic event emission for all data operations
- **Monitoring**: Integrated with existing observability stack
- **Security**: Unified authentication and authorization

## Next Steps

1. Review the configuration schema
2. Customize for your specific use cases
3. Validate configuration changes
4. Deploy with environment-specific settings
5. Monitor performance and adjust as needed

For implementation details, see the main persistence platform documentation.

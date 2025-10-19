# 🏗️ Persistence Platform Dev Tool

A single-page HTML interface for interacting with the Unhinged Persistence Platform from a developer tooling perspective. This tool provides direct access to all persistence platform APIs for testing, debugging, and development.

## 🚀 Quick Start

### 1. Start the Persistence Platform
```bash
# From project root
./static-dashboard/start-persistence-dev.sh
```

This will:
- Start Redis (port 6379) 
- Start CockroachDB (port 26257, admin UI on 8080)
- Build and start the Persistence Platform (port 8090)

### 2. Open the Dev Tool
```bash
# Open in your browser
open static-dashboard/persistence-dev-tool.html
```

Or navigate to: `file:///path/to/Unhinged/static-dashboard/persistence-dev-tool.html`

## 🎯 Features

### **Platform Status**
- Real-time health monitoring
- Version and uptime information
- Technology status overview

### **CRUD Operations**
- **Insert Record**: Add new records to any table
- **Execute Query**: Run named queries with parameters
- **Update/Delete**: Modify or remove records

### **Advanced Operations**
- **Vector Search**: Semantic similarity search
- **Graph Traversal**: Relationship queries
- **Complex Operations**: Multi-step workflows

### **Raw API Testing**
- Custom HTTP method selection
- Direct endpoint access
- Raw JSON request/response

## 📋 Usage Examples

### Insert a User Record
```json
Table: users
Data: {
  "email": "user@example.com",
  "profile": {
    "name": "John Doe",
    "age": 30
  }
}
```

### Execute a Named Query
```json
Query: get_user_by_id
Parameters: {
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "active"
}
```

### Vector Search
```json
Table: document_embeddings
Vector: [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
Limit: 10
```

### Complex Operation
```json
Operation: create_user_complete
Parameters: {
  "userId": "123e4567-e89b-12d3-a456-426614174000",
  "profile": {
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```

## 🔧 API Endpoints Tested

The dev tool directly hits these persistence platform endpoints:

- `GET /api/v1/health` - Platform health check
- `GET /api/v1/info` - Platform information
- `POST /api/v1/tables/{tableName}` - Insert records
- `POST /api/v1/query/{queryName}` - Execute named queries
- `POST /api/v1/vector/search/{tableName}` - Vector search
- `POST /api/v1/operations/{operationName}` - Complex operations
- Custom endpoints via raw API testing

## 🎨 UI Features

### **Responsive Design**
- Matches existing Unhinged dashboard styling
- Dark theme with consistent color scheme
- Mobile-friendly responsive layout

### **Real-time Feedback**
- Success/error status indicators
- JSON response formatting
- Copy-to-clipboard functionality
- Execution time tracking

### **Developer Experience**
- Syntax highlighting for JSON
- Pre-filled example data
- Form validation and error handling
- Auto-refresh platform status

## 🔍 Troubleshooting

### Platform Not Responding
1. Check if persistence platform is running: `curl http://localhost:8090/api/v1/health`
2. Verify databases are running: `docker ps`
3. Check platform logs for errors

### CORS Issues
The platform is configured to allow:
- `http://localhost:3000` (frontend)
- `file://` protocol (dev tool)
- `null` origin (local files)

### Database Connection Issues
1. Redis: `docker exec unhinged-redis-dev redis-cli ping`
2. CockroachDB: `curl http://localhost:8080/health?ready=1`

## 🛠️ Development

### File Structure
```
static-dashboard/
├── persistence-dev-tool.html     # Main dev tool interface
├── start-persistence-dev.sh      # Platform startup script
├── styles.css                    # Shared dashboard styles
└── PERSISTENCE_DEV_TOOL.md      # This documentation
```

### Customization
- Modify `PLATFORM_BASE_URL` in the HTML to point to different environments
- Add new operation types by extending the JavaScript functions
- Customize styling by modifying the embedded CSS

### Adding New Operations
1. Add HTML form section for the new operation
2. Create JavaScript function to handle the API call
3. Add response handling and display logic

## 🔗 Related Documentation

- [Persistence Platform API](../docs/api/persistence-platform.md)
- [Platform Configuration](../platforms/persistence/config/README.md)
- [Protobuf Contracts](../proto/persistence_platform.proto)

## 🎯 Use Cases

### **Development Testing**
- Test new queries and operations
- Validate API responses
- Debug data access patterns

### **Data Exploration**
- Browse table contents
- Test search functionality
- Explore relationships

### **Integration Testing**
- Verify API contracts
- Test error handling
- Validate performance

### **Debugging**
- Inspect raw API responses
- Test edge cases
- Troubleshoot connectivity

---

**This dev tool provides complete end-to-end testing of the persistence platform APIs with a clean, developer-friendly interface that matches the Unhinged ecosystem styling.**

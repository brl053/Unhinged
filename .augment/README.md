# Augment Configuration for Unhinged Project

This directory contains configuration files that help Augment Agent maintain consistent behavior when working with the Unhinged monorepo.

## Files

### `config.json`
Main project configuration including:
- Project metadata and architecture
- Component definitions and dependencies  
- Development commands and workflows
- Docker configuration
- Coding standards

### `agent-instructions.md`
Detailed instructions for Augment Agent including:
- Project overview and setup
- Development workflow guidelines
- Code standards and practices
- Testing strategies
- Common tasks and patterns

### `mcp-config.json`
Model Context Protocol (MCP) server configuration for:
- File system access
- Git operations
- PostgreSQL database integration
- Docker container management
- Web search capabilities

## Usage

When Augment Agent is invoked in this repository, it will automatically:
1. Load the project configuration
2. Follow the established coding standards
3. Use the configured MCP servers for enhanced capabilities
4. Maintain consistency with project patterns

## Customization

To modify Augment's behavior:
1. Update `config.json` for project structure changes
2. Edit `agent-instructions.md` for workflow modifications
3. Adjust `mcp-config.json` for different tool integrations

## MCP Server Setup

To enable the MCP servers defined in `mcp-config.json`:

1. Install required MCP servers:
   ```bash
   npm install -g @modelcontextprotocol/server-filesystem
   npm install -g @modelcontextprotocol/server-git
   npm install -g @modelcontextprotocol/server-postgres
   npm install -g @modelcontextprotocol/server-docker
   npm install -g @modelcontextprotocol/server-brave-search
   ```

2. Set environment variables if needed:
   ```bash
   export BRAVE_API_KEY="your-brave-api-key"  # Optional for web search
   ```

3. The configuration will be automatically loaded by Augment Agent

## Notes

- Database MCP server requires the PostgreSQL service to be running
- File paths in MCP config are absolute and may need adjustment for different environments
- Web search MCP server requires a Brave API key (optional)

# AutoGen MCP Dynamic Tool Discovery

An advanced multi-agent system that integrates AutoGen with Model Context Protocol (MCP) for dynamic tool discovery and domain-based access control.

## 🎯 Features

- **Dynamic Tool Discovery**: Tools are discovered at runtime based on domain patterns
- **Domain-Based Access Control**: Agents only access tools matching their allowed domains (e.g., "event.*")
- **Type-Safe Integration**: Properly typed async functions compatible with AutoGen
- **Modular Architecture**: Easy to add new tools and agent types
- **Real-World Application**: Demonstrates event planning with multiple specialized agents

## 🏗️ Architecture

### Core Components

- **`mcp_client.py`** - MCP client with dynamic tool discovery
- **`unified_mcp_server.py`** - MCP server handling multiple tool domains
- **`test.py`** - Main application with domain-based agent tool assignment
- **`prompts.json`** - Agent system prompts and task definitions

### Tool Domains

- **`event.*`** - Event planning and coordination
- **`fundraising.*`** - Fundraising and budget management
- **`quality.*`** - Quality assurance and checking
- **`db.*`** - Database operations
- **`file.*`** - File system operations

## 🚀 Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables**:
   ```bash
   # Create .env file
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Run the System**:
   ```bash
   python test.py
   ```

4. **Run Tests**:
   ```bash
   python tests/test_dynamic_tools.py
   python tests/test_integration.py
   ```

## 📁 Project Structure

```
AutoGen_Project/
├── mcp_client.py           # Dynamic MCP client
├── unified_mcp_server.py   # MCP server
├── test.py                 # Main application
├── prompts.json           # Agent prompts
├── requirements.txt       # Dependencies
├── tests/                 # Test files
│   ├── test_dynamic_tools.py
│   └── test_integration.py
├── PROJECT_SUMMARY.md     # Detailed technical summary
└── README.md             # This file
```

## 🎭 Example Usage

The system creates specialized agents with domain-specific tools:

```python
agent_configs = {
    "event_coordinator": {
        "allowed_domains": ["event.*"],
        "system_message": prompts["EventCoordinator"]
    },
    "fundraising_coordinator": {
        "allowed_domains": ["fundraising.*"],
        "system_message": prompts["FundraisingCoordinator"]
    },
    "quality_checker": {
        "allowed_domains": ["quality.*"],
        "system_message": prompts["QualityChecker"]
    }
}
```

## 🧪 Testing

- **Tool Discovery**: Validates domain-based filtering
- **Integration**: Tests agent creation with dynamic tools
- **End-to-End**: Full multi-agent conversation demonstration

## 📈 Benefits

- **Security**: Agents only access authorized tools
- **Modularity**: Easy to extend with new tools/agents
- **Scalability**: Domain patterns support growth
- **Maintainability**: No hardcoded tool assignments
- **Type Safety**: Compatible with AutoGen framework

## 🔧 Configuration

Agents are configured with allowed tool domains using glob patterns:

- `"event.*"` - All event-related tools
- `"fundraising.*"` - All fundraising tools
- `"quality.*"` - All quality assurance tools
- `["event.*", "quality.*"]` - Multiple domains

## 📄 License

This project is for educational and research purposes.

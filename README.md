# MCP Paint Project

## Purpose
This project demonstrates a **Modular Control Protocol (MCP)** system for automating tasks in the Paint application.  
It consists of two main components:

1. **MCP Server (`mcp_Server_paint`)**  
   Contains tools and utilities specifically designed to interact with the Paint application.

2. **MCP Client (`mcp_client_paint`)**  
   Contains code that uses the MCP Server tools to perform actions in Paint, leveraging **Gemini 2.0 Flash** for command execution.  
   The client can also handle starting the MCP Server automatically.

---

## Getting Started

### Start the MCP Server
To launch the MCP Server, run the following commands:

```bash
uv add "mcp[cli]"
uv run mcp dev mcp_server_paint.py
```

Run the client after the server is launched, run the following command:

```bash
uv run mcp_client_paint.py

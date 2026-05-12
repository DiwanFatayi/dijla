"""MCP client wrappers.

For unit tests and in-process orchestration we expose the backend objects
directly via thin protocol-conformant wrappers. The same MCP servers are also
runnable as stdio subprocesses (see ``dijla.mcp_servers``) so external clients
(Claude Desktop, Cursor) can talk to them.
"""

from dijla.infrastructure.mcp_clients.direct import (
    DirectAgnnCertClient,
    DirectLean4Client,
    DirectRcgnnClient,
)
from dijla.infrastructure.mcp_clients.stdio import (
    StdioAgnnCertClient,
    StdioLean4Client,
    StdioRcgnnClient,
)

__all__ = [
    "DirectAgnnCertClient",
    "DirectLean4Client",
    "DirectRcgnnClient",
    "StdioAgnnCertClient",
    "StdioLean4Client",
    "StdioRcgnnClient",
]

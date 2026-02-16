from mcp.server.fastmcp import FastMCP

# Cursor가 tool 결과를 잘 읽게 하려면 json_response=True 권장
mcp = FastMCP("COLA-MVP", json_response=True)

@mcp.tool()
def ping() -> str:
    """Connectivity test tool"""
    return "pong"

if __name__ == "__main__":
    # Cursor 로컬 연동은 보통 stdio 방식이 가장 단순합니다.
    mcp.run(transport="stdio")

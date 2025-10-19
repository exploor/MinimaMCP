"""Minima MCP Server - Exposes Minima blockchain functionality via Model Context Protocol."""

import json
import logging
import os
from typing import Annotated, Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from .minima_client import MinimaClient, MinimaClientError

# Import tool modules
from . import contract_tools
from . import transaction_tools
from . import event_tools
from . import maxima_tools
from . import token_tools
from . import dev_tools
from . import minima_primer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP("Minima Blockchain")

# Initialize Minima client (will be configured on first use)
_client: Optional[MinimaClient] = None


def get_client() -> MinimaClient:
    """Get or create Minima client instance."""
    global _client
    if _client is None:
        host = os.getenv("MINIMA_HOST", "localhost")
        port = int(os.getenv("MINIMA_PORT", "9003"))
        password = os.getenv("MINIMA_MDS_PASSWORD")

        _client = MinimaClient(host=host, port=port, mds_password=password)
        logger.info(f"Connected to Minima MDS at {host}:{port}")

    return _client


# ============================================================================
# Minima Context & Primer
# ============================================================================


@mcp.tool()
def get_minima_primer() -> str:
    """
    Get comprehensive Minima blockchain primer and context.

    **IMPORTANT**: Call this FIRST to understand Minima's unique concepts:
    - KISSVM smart contract language
    - UTxO model vs account model
    - MAST (Merkle Abstract Syntax Tree)
    - MDS (MiniDapp System)
    - Maxima P2P messaging
    - State variables and events
    - MiniDapp Store creation and management

    Returns detailed explanations, examples, and best practices for working
    with Minima's unique features.

    **Use this when:**
    - Starting any Minima development task
    - Need to understand KISSVM syntax
    - Confused about UTxOs vs accounts
    - Building smart contracts or MiniDapps
    - Creating MiniDapp stores with MCP tools
    - Using advanced features like Maxima or events

    Includes detailed scenarios for:
    - Creating MiniDapp stores with create_minidapp_store()
    - Smart contract development workflows
    - Transaction building patterns
    - Real-time event monitoring
    - P2P messaging applications

    Returns complete primer document with examples and patterns.
    """
    return minima_primer.get_minima_primer()


# ============================================================================
# MiniDapp Store Tools
# ============================================================================


@mcp.tool()
def create_minidapp_store(
    name: Annotated[str, Field(description="Store name (e.g., 'DeFi Hub', 'Gaming Store')")],
    description: Annotated[str, Field(description="Store description")],
    dapps: Annotated[Optional[List[Dict[str, Any]]], Field(description="List of MiniDapps in store (optional - can be empty)")] = None,
    banner_url: Annotated[Optional[str], Field(description="Banner image URL")] = None,
    icon_url: Annotated[Optional[str], Field(description="Store icon URL")] = None,
    output_dir: Annotated[Optional[str], Field(description="Directory to create store files")] = None,
    scan_installed: Annotated[bool, Field(description="Scan user's installed MiniDapps and offer to include them")] = False
) -> Dict[str, Any]:
    """
    Create a MiniDapp Store - a JSON manifest that can be loaded by the Minima Storefront.

    This creates a store definition JSON file that users can host anywhere (web server, IPFS, etc.)
    and load into the Minima Storefront MiniDapp. The store follows the official Minima
    Storefront JSON format and can contain any number of MiniDapps with metadata like
    descriptions, versions, and download URLs.

    Set scan_installed=True to automatically scan your installed MiniDapps and include them
    in the store (you can still add additional ones via the dapps parameter).

    Returns the store JSON and public URL for immediate use.
    """
    try:
        import os
        import json
        from pathlib import Path
        from datetime import datetime

        # Set defaults
        if dapps is None:
            dapps = []

        if output_dir is None:
            output_dir = "./minidapp_stores"

        # Scan installed MiniDapps if requested
        if scan_installed:
            try:
                client = get_client()
                installed_apps = client.list_minidapps()
                if installed_apps and isinstance(installed_apps, dict) and "response" in installed_apps:
                    minidapps = installed_apps["response"].get("minidapps", [])
                    for app in minidapps:
                        # Skip system MiniDapps and stores
                        if (app.get("conf", {}).get("category") not in ["System", "Store"] and
                            app.get("conf", {}).get("name") != "Storefront"):

                            # Create a dapp entry for the installed MiniDapp
                            installed_dapp = {
                                "name": app.get("conf", {}).get("name", "Unknown App"),
                                "description": app.get("conf", {}).get("description", "Installed MiniDapp"),
                                "version": app.get("conf", {}).get("version", "1.0.0"),
                                "file": f"http://127.0.0.1:9003/{app.get('uid', '')}/app.mds.zip",
                                "date": datetime.now().strftime("%b %d, %Y")
                            }

                            # Add icon if available
                            if "icon" in app.get("conf", {}):
                                installed_dapp["icon"] = f"http://127.0.0.1:9003/{app.get('uid', '')}/{app['conf']['icon']}"

                            dapps.append(installed_dapp)

            except Exception as e:
                logger.warning(f"Could not scan installed MiniDapps: {e}")
                # Continue without installed apps if scanning fails

        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Generate store JSON
        store_data = {
            "name": name,
            "description": description,
            "version": "1.0",
            "manifest_version": 2
        }

        # Add optional fields
        if banner_url:
            store_data["banner"] = banner_url
        if icon_url:
            store_data["icon"] = icon_url

        # Add dapps array
        store_data["dapps"] = []
        for i, dapp in enumerate(dapps):
            # Ensure required fields and add defaults
            dapp_entry = {
                "file": dapp.get("file", ""),
                "name": dapp.get("name", f"App {i+1}"),
                "description": dapp.get("description", ""),
                "version": dapp.get("version", "1.0.0"),
                "date": dapp.get("date", datetime.now().strftime("%b %d, %Y"))
            }

            # Add optional fields
            if "icon" in dapp:
                dapp_entry["icon"] = dapp["icon"]
            if "repository_url" in dapp:
                dapp_entry["repository_url"] = dapp["repository_url"]
            if "about" in dapp:
                dapp_entry["about"] = dapp["about"]
            if "screenshots" in dapp:
                dapp_entry["screenshots"] = dapp["screenshots"]
            if "release_notes" in dapp:
                dapp_entry["release_notes"] = dapp["release_notes"]
            if "history" in dapp:
                dapp_entry["history"] = dapp["history"]

            store_data["dapps"].append(dapp_entry)

        # Create store-specific filename
        store_name_clean = name.replace(" ", "_").replace("/", "_").lower()
        store_json_filename = f"{store_name_clean}.json"
        store_json_path = output_path / store_json_filename

        # Write store.json
        with open(store_json_path, 'w', encoding='utf-8') as f:
            json.dump(store_data, f, indent=2, ensure_ascii=False)

        # Get the Minima host for URL construction
        host = os.getenv("MINIMA_HOST", "127.0.0.1")

        # The store is now hosted on the local HTTP server at the same location as MiniDapps
        local_file_path = str(store_json_path.absolute())
        public_url = f"http://{host}:8080/{store_json_filename}"

        # Calculate how many apps were from scanning
        scanned_count = 0
        if scan_installed and dapps:
            try:
                client = get_client()
                installed_apps = client.list_minidapps()
                if installed_apps and isinstance(installed_apps, dict) and "response" in installed_apps:
                    scanned_count = len([app for app in installed_apps["response"].get("minidapps", [])
                                       if app.get("conf", {}).get("category") not in ["System", "Store"] and
                                       app.get("conf", {}).get("name") != "Storefront"])
            except:
                pass

        return {
            "success": True,
            "message": f"Successfully created MiniDapp Store JSON '{name}' with {len(dapps)} MiniDapps{' (' + str(scanned_count) + ' from installed apps)' if scanned_count > 0 else ''}",
            "data": {
                "store_name": name,
                "store_description": description,
                "dapps_count": len(dapps),
                "scanned_apps_count": scanned_count,
                "store_json_path": local_file_path,
                "public_url": public_url,
                "store_json": store_data,
                "usage_instructions": [
                    f"Copy this URL: {public_url}",
                    "Open the Minima Storefront MiniDapp",
                    "Click the '+' button to add a store",
                    "Paste the URL and load your MiniDapp store"
                ]
            }
        }

    except Exception as e:
        logger.error(f"Failed to create MiniDapp store: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to create store: {str(e)}"
        }


@mcp.tool()
def update_minidapp_store(
    store_uid: Annotated[str, Field(description="Store UID from original creation")],
    updates: Annotated[Dict[str, Any], Field(description="Updates to apply (name, description, dapps array, etc.)")]
) -> Dict[str, Any]:
    """
    Update an existing MiniDapp Store with new data.

    This allows you to modify store metadata, add/remove MiniDapps,
    update descriptions, etc. The store will be repackaged and reinstalled.
    """
    try:
        # This is a simplified version - in practice you'd need to:
        # 1. Fetch current store data from MDS
        # 2. Apply updates
        # 3. Repackage and reinstall

        return {
            "success": False,
            "error": "Update functionality not yet implemented. Manually recreate store with updates."
        }

    except Exception as e:
        logger.error(f"Store update failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def list_minidapp_stores() -> Dict[str, Any]:
    """
    List all installed MiniDapp Stores on this node.

    Returns stores that have been created and installed as MiniDapps.
    """
    try:
        client = get_client()
        mds_list = client.list_minidapps()

        stores = []
        if mds_list and "minidapps" in mds_list:
            for app in mds_list["minidapps"]:
                conf = app.get("conf", {})
                if conf.get("category") == "Store":
                    stores.append({
                        "uid": app.get("uid"),
                        "name": conf.get("name", "Unknown Store"),
                        "description": conf.get("description", ""),
                        "url": f"https://127.0.0.1:9003/{app.get('uid')}/store.json",
                        "version": conf.get("version", "1.0")
                    })

        return {
            "success": True,
            "data": {
                "stores": stores,
                "count": len(stores)
            }
        }

    except Exception as e:
        logger.error(f"Store listing failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# ============================================================================
# Blockchain Query Tools
# ============================================================================


@mcp.tool()
def get_balance(
    address: Annotated[Optional[str], Field(description="Specific address to check balance for")] = None,
    tokenid: Annotated[Optional[str], Field(description="Token ID to check (0x00 for Minima)")] = None
) -> Dict[str, Any]:
    """
    Get balance of Minima or specific tokens.

    Returns total balance across all addresses or for a specific address/token.
    """
    try:
        client = get_client()
        result = client.get_balance(
            address=address,
            tokenid=tokenid
        )
        return {
            "success": True,
            "data": result
        }
    except MinimaClientError as e:
        logger.error(f"Balance query failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def get_node_status() -> Dict[str, Any]:
    """
    Get current node status and blockchain information.

    Returns chain height, version, sync status, and other node details.
    """
    try:
        client = get_client()
        result = client.get_status()
        return {
            "success": True,
            "data": result
        }
    except MinimaClientError as e:
        logger.error(f"Status query failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def get_address() -> Dict[str, Any]:
    """
    Get a Minima address for receiving funds.

    Returns a new or existing address that can be used to receive Minima or tokens.
    """
    try:
        client = get_client()
        result = client.get_address()
        return {
            "success": True,
            "data": result
        }
    except MinimaClientError as e:
        logger.error(f"Get address failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def list_tokens(
    tokenid: Annotated[Optional[str], Field(description="Specific token ID to query")] = None
) -> Dict[str, Any]:
    """
    List all tokens or get information about a specific token.

    Returns details about tokens including name, amount, and token ID.
    """
    try:
        client = get_client()
        result = client.get_tokens(tokenid=tokenid)
        return {
            "success": True,
            "data": result
        }
    except MinimaClientError as e:
        logger.error(f"Token query failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def get_coins(
    relevant: Annotated[bool, Field(description="Show only relevant coins")] = True,
    sendable: Annotated[bool, Field(description="Show only sendable coins")] = False,
    address: Annotated[Optional[str], Field(description="Filter by specific address")] = None,
    tokenid: Annotated[Optional[str], Field(description="Filter by token ID")] = None
) -> Dict[str, Any]:
    """
    Get coins (UTxOs) information from the blockchain.

    Returns unspent transaction outputs that can be used in transactions.
    """
    try:
        client = get_client()
        result = client.get_coins(
            relevant=relevant,
            sendable=sendable,
            address=address,
            tokenid=tokenid
        )
        return {
            "success": True,
            "data": result
        }
    except MinimaClientError as e:
        logger.error(f"Coins query failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# ============================================================================
# Transaction Tools
# ============================================================================


@mcp.tool()
def send_minima(
    amount: str = Field(..., description="Amount to send"),
    address: str = Field(..., description="Recipient address"),
    tokenid: str = Field("0x00", description="Token ID (0x00 for Minima)")
) -> Dict[str, Any]:
    """
    Send Minima or tokens to an address.

    Creates and broadcasts a transaction to send funds. Requires wallet to be unlocked.
    """
    try:
        client = get_client()
        result = client.send(
            amount=amount,
            address=address,
            tokenid=tokenid
        )
        return {
            "success": True,
            "data": result,
            "message": f"Successfully sent {amount} to {address}"
        }
    except MinimaClientError as e:
        logger.error(f"Send transaction failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def create_token(
    name: str = Field(..., description="Token name"),
    amount: str = Field(..., description="Total token amount"),
    decimals: int = Field(8, description="Decimal places"),
    description: str = Field(None, description="Token description"),
    icon: str = Field(None, description="Icon URL or path"),
    proof: str = Field(None, description="Proof data")
) -> Dict[str, Any]:
    """
    Create a new token on the Minima blockchain.

    Creates a custom token with specified name, amount, and properties.
    """
    try:
        client = get_client()
        result = client.create_token(
            name=name,
            amount=amount,
            decimals=decimals,
            description=description,
            icon=icon,
            proof=proof
        )
        return {
            "success": True,
            "data": result,
            "message": f"Token '{name}' created successfully"
        }
    except MinimaClientError as e:
        logger.error(f"Token creation failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def get_transaction(
    txpowid: str = Field(..., description="Transaction PoW ID")
) -> Dict[str, Any]:
    """
    Get details of a specific transaction by its ID.

    Returns complete transaction information including inputs, outputs, and status.
    """
    try:
        client = get_client()
        result = client.get_txpow(txpowid=txpowid)
        return {
            "success": True,
            "data": result
        }
    except MinimaClientError as e:
        logger.error(f"Transaction query failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def search_blockchain(
    block: int = Field(None, description="Specific block number"),
    address: str = Field(None, description="Search by address"),
    tokenid: str = Field(None, description="Search by token ID")
) -> Dict[str, Any]:
    """
    Search the Minima blockchain for transactions and blocks.

    Search by block number, address, or token ID to find relevant blockchain data.
    """
    try:
        client = get_client()
        result = client.search_chain(
            block=block,
            address=address,
            tokenid=tokenid
        )
        return {
            "success": True,
            "data": result
        }
    except MinimaClientError as e:
        logger.error(f"Blockchain search failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# ============================================================================
# Network Tools
# ============================================================================


@mcp.tool()
def get_network_info() -> Dict[str, Any]:
    """
    Get information about the Minima network.

    Returns network statistics, node count, and connection details.
    """
    try:
        client = get_client()
        result = client.get_network_info()
        return {
            "success": True,
            "data": result
        }
    except MinimaClientError as e:
        logger.error(f"Network query failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def get_peers() -> Dict[str, Any]:
    """
    Get list of connected peers.

    Returns information about nodes currently connected to your Minima node.
    """
    try:
        client = get_client()
        result = client.get_peers()
        return {
            "success": True,
            "data": result
        }
    except MinimaClientError as e:
        logger.error(f"Peers query failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# ============================================================================
# MiniDapp Tools
# ============================================================================


@mcp.tool()
def list_minidapps() -> Dict[str, Any]:
    """
    List all installed MiniDapps.

    Returns information about all MiniDapps currently installed on the node.
    """
    try:
        client = get_client()
        result = client.list_minidapps()
        return {
            "success": True,
            "data": result
        }
    except MinimaClientError as e:
        logger.error(f"MiniDapp list failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def install_minidapp(
    file_path: str = Field(..., description="Path to .mds.zip file")
) -> Dict[str, Any]:
    """
    Install a MiniDapp from a .mds.zip file.

    Installs a MiniDapp package onto the Minima node.
    """
    try:
        client = get_client()
        result = client.install_minidapp(file_path=file_path)
        return {
            "success": True,
            "data": result,
            "message": f"MiniDapp installed successfully from {file_path}"
        }
    except MinimaClientError as e:
        logger.error(f"MiniDapp installation failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def get_minidapp_info(
    uid: str = Field(..., description="MiniDapp UID")
) -> Dict[str, Any]:
    """
    Get information about a specific MiniDapp.

    Returns details about a MiniDapp including name, version, and status.
    """
    try:
        client = get_client()
        result = client.get_minidapp_info(uid=uid)
        return {
            "success": True,
            "data": result
        }
    except MinimaClientError as e:
        logger.error(f"MiniDapp info query failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# ============================================================================
# Utility Tools
# ============================================================================


@mcp.tool()
def execute_command(
    command: str = Field(..., description="Minima command to execute")
) -> Dict[str, Any]:
    """
    Execute any Minima terminal command.

    Advanced tool for running arbitrary Minima commands. Use with caution.
    Example: execute_command(command="status") or execute_command(command="balance confirmations:3")
    """
    try:
        client = get_client()
        result = client.execute_command(command)
        return {
            "success": True,
            "data": result
        }
    except MinimaClientError as e:
        logger.error(f"Command execution failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def health_check() -> Dict[str, Any]:
    """
    Check if Minima node is responsive and healthy.

    Returns connection status and basic node health information.
    """
    try:
        client = get_client()
        is_healthy = client.health_check()

        if is_healthy:
            status = client.get_status()
            return {
                "success": True,
                "healthy": True,
                "message": "Minima node is responsive",
                "data": status
            }
        else:
            return {
                "success": False,
                "healthy": False,
                "message": "Minima node is not responsive"
            }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "success": False,
            "healthy": False,
            "error": str(e)
        }


# ============================================================================
# MiniDapp Builder Tools
# ============================================================================


@mcp.tool()
def create_minidapp_project(
    name: Annotated[str, Field(description="MiniDapp name")],
    description: Annotated[str, Field(description="MiniDapp description")],
    output_dir: Annotated[str, Field(description="Directory to create project in")],
    version: Annotated[str, Field(description="Version")] = "1.0.0",
    category: Annotated[str, Field(description="Category")] = "Utility"
) -> Dict[str, Any]:
    """
    Create a new MiniDapp project with basic structure.

    Creates directory with dapp.conf, index.html, and basic files.
    """
    try:
        import os
        import json
        from pathlib import Path

        # Create project directory
        project_path = Path(output_dir) / name
        project_path.mkdir(parents=True, exist_ok=True)

        # Create minidapp.conf
        conf = {
            "name": name,
            "version": version,
            "description": description,
            "icon": "icon.png",
            "category": category,
            "browser": "index.html"
        }

        conf_path = project_path / "dapp.conf"
        with open(conf_path, 'w') as f:
            json.dump(conf, f, indent=2)

        # Create basic index.html
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name}</title>
    <script src="https://docs.minima.global/mds.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        h1 {{
            color: #667eea;
            margin-top: 0;
        }}
        .status {{
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }}
        .success {{
            background: #d4edda;
            color: #155724;
        }}
        .info {{
            background: #d1ecf1;
            color: #0c5460;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{name}</h1>
        <p>{description}</p>

        <div id="status" class="status info">
            Initializing MDS connection...
        </div>

        <div id="content"></div>
    </div>

    <script>
        MDS.init(function(msg) {{
            console.log('MDS Message:', msg);

            if(msg.event == "inited") {{
                document.getElementById('status').className = 'status success';
                document.getElementById('status').textContent = 'Connected to Minima!';

                // Get node status
                MDS.cmd("status", function(resp) {{
                    console.log('Status:', resp);
                    if(resp.status) {{
                        const data = resp.response;
                        document.getElementById('content').innerHTML = `
                            <h2>Node Info</h2>
                            <p><strong>Version:</strong> ${{data.version}}</p>
                            <p><strong>Block:</strong> ${{data.chain.block}}</p>
                            <p><strong>Uptime:</strong> ${{data.uptime}}</p>
                        `;
                    }}
                }});
            }}
        }});
    </script>
</body>
</html>
"""

        html_path = project_path / "index.html"
        with open(html_path, 'w') as f:
            f.write(html_content)

        logger.info(f"Created MiniDapp project at {project_path}")

        return {
            "success": True,
            "message": f"Created MiniDapp project '{name}'",
            "data": {
                "project_path": str(project_path),
                "files": ["dapp.conf", "index.html"]
            }
        }

    except Exception as e:
        logger.error(f"Failed to create MiniDapp project: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def write_minidapp_file(
    project_path: Annotated[str, Field(description="Path to MiniDapp project directory")],
    file_name: Annotated[str, Field(description="File name (e.g., 'app.js', 'style.css')")],
    content: Annotated[str, Field(description="File content")]
) -> Dict[str, Any]:
    """
    Write a file to a MiniDapp project directory.

    Use this to add CSS, JavaScript, or other files to your MiniDapp.
    """
    try:
        from pathlib import Path

        file_path = Path(project_path) / file_name

        # Create parent directories if needed
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Wrote file {file_name} to {project_path}")

        return {
            "success": True,
            "message": f"File '{file_name}' written successfully",
            "data": {
                "file_path": str(file_path)
            }
        }

    except Exception as e:
        logger.error(f"Failed to write file: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def package_minidapp(
    project_path: Annotated[str, Field(description="Path to MiniDapp project directory")],
    output_path: Annotated[Optional[str], Field(description="Output .mds.zip path (optional)")] = None
) -> Dict[str, Any]:
    """
    Package a MiniDapp project directory into .mds.zip file.

    Creates a .mds.zip file that can be installed on Minima.
    """
    try:
        import zipfile
        from pathlib import Path

        project_path = Path(project_path)

        if not project_path.exists():
            return {
                "success": False,
                "error": f"Project directory not found: {project_path}"
            }

        # Check for required dapp.conf
        conf_path = project_path / "dapp.conf"
        if not conf_path.exists():
            return {
                "success": False,
                "error": "dapp.conf not found in project directory"
            }

        # Check for mds.js (MDS client library) - warn if missing
        mds_js_path = project_path / "mds.js"
        warnings = []
        if not mds_js_path.exists():
            warning_msg = (
                "⚠️ WARNING: mds.js not found in your MiniDapp!\n"
                "Your MiniDapp will likely fail to load with ERR_BLOCKED_BY_ORB.\n\n"
                "The mds.js client library must be INSIDE your MiniDapp package.\n"
                "Download it from:\n"
                "  https://raw.githubusercontent.com/minima-global/Minima/master/mds/mds.js\n"
                "Or get it from releases:\n"
                "  https://github.com/minima-global/Minima/releases\n\n"
                "Then add to your HTML:\n"
                '  <script src="./mds.js"></script>'
            )
            warnings.append(warning_msg)
            logger.warning(warning_msg)

        # Determine output path
        if output_path is None:
            output_path = project_path.parent / f"{project_path.name}.mds.zip"
        else:
            output_path = Path(output_path)

        # Exclusion patterns for packaging
        exclude_patterns = [
            '__pycache__',
            '*.pyc',
            '.git',
            '.gitignore',
            'node_modules',
            '.DS_Store',
            'Thumbs.db',
            '.env',
            '*.log',
            '.vscode',
            '.idea',
            'venv',
            'env',
            '.pytest_cache',
            '*.mds.zip',  # Exclude all zip files to prevent recursion
            '.venv',
            '.claude',  # Claude Code artifacts
            'temp_minidapp',  # Temp directories
            '*.jar',  # Java archives (like minima.jar)
            '*.md',  # Documentation files
            '*.py',  # Python scripts
            'README*',  # README files
            'LICENSE',  # License files
            '.gitattributes',
            '*.exe',  # Executables
            '*.dll',  # DLLs
            'dist',  # Build directories
            'build',
            '.next',
            '.cache'
        ]

        def should_exclude(path: Path) -> bool:
            """Check if path should be excluded from packaging."""
            path_parts = path.parts

            for pattern in exclude_patterns:
                # Check if any part of the path matches the pattern
                if pattern in path_parts:
                    return True
                # Check wildcards
                if '*' in pattern:
                    import fnmatch
                    if fnmatch.fnmatch(path.name, pattern):
                        return True
            return False

        # Create zip file
        file_count = 0
        total_size = 0
        max_size_mb = 100  # Safety limit: 100MB

        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in project_path.rglob('*'):
                # Safety check: ensure we're still within project directory
                try:
                    relative = file_path.relative_to(project_path)
                except ValueError:
                    logger.warning(f"Skipping file outside project: {file_path}")
                    continue

                if file_path.is_file():
                    if should_exclude(file_path):
                        logger.debug(f"Excluding: {relative}")
                        continue

                    file_size_mb = file_path.stat().st_size / (1024 * 1024)

                    # Safety check: prevent huge archives
                    if total_size + file_size_mb > max_size_mb:
                        logger.error(f"Archive size would exceed {max_size_mb}MB limit. Stopping.")
                        logger.error(f"Problem file: {relative} ({file_size_mb:.2f}MB)")
                        raise Exception(f"MiniDapp package would exceed {max_size_mb}MB size limit. Check for unwanted files.")

                    zipf.write(file_path, relative)
                    file_count += 1
                    total_size += file_size_mb
                    logger.debug(f"Added {relative} to zip ({file_size_mb:.2f}MB)")

        logger.info(f"Packaged {file_count} files ({total_size:.2f}MB) to {output_path}")

        result = {
            "success": True,
            "message": f"MiniDapp packaged successfully",
            "data": {
                "zip_path": str(output_path),
                "size_bytes": output_path.stat().st_size,
                "file_count": file_count,
                "size_mb": round(total_size, 2)
            }
        }

        # Add warnings if any
        if warnings:
            result["warnings"] = warnings

        return result

    except Exception as e:
        logger.error(f"Failed to package MiniDapp: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def install_packaged_minidapp(
    zip_path: Annotated[str, Field(description="Path to .mds.zip file")]
) -> Dict[str, Any]:
    """
    Install a packaged MiniDapp (.mds.zip) to Minima node.

    This uses the MDS install command to deploy your MiniDapp.
    """
    try:
        from pathlib import Path

        zip_path = Path(zip_path)

        if not zip_path.exists():
            return {
                "success": False,
                "error": f"Zip file not found: {zip_path}"
            }

        # Convert to absolute path for MDS
        abs_path = str(zip_path.absolute())

        # Use text-based install method (MDS install returns plain text, not JSON)
        client = get_client()

        # Convert to file:// URL format for MDS
        file_url = f"file:{abs_path}"
        result = client.install_minidapp_text(file_url)

        logger.info(f"Installed MiniDapp from {abs_path}")
        logger.debug(f"Install response: {result[:200]}...")

        return {
            "success": True,
            "message": "MiniDapp installed successfully",
            "data": result
        }

    except Exception as e:
        logger.error(f"Failed to install MiniDapp: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# ============================================================================
# Contract Studio Tools (KISSVM)
# ============================================================================


@mcp.tool()
def create_contract_script(
    name: Annotated[str, Field(description="Script name")],
    template: Annotated[Optional[str], Field(description="Template name (multisig_2_of_2, multisig_2_of_3, timelock, htlc, simple_lock)")] = None,
    script: Annotated[Optional[str], Field(description="Custom KISSVM script code")] = None,
    description: Annotated[Optional[str], Field(description="Script description")] = None
) -> Dict[str, Any]:
    """
    Create a new KISSVM smart contract script.

    **KISSVM** is Minima's smart contract language - a simple, explicit scripting
    language for on-chain contracts. Contracts must return TRUE or FALSE.

    **Use templates for common patterns:**
    - multisig_2_of_2: Requires signatures from both parties
    - multisig_2_of_3: Requires 2 of 3 signatures
    - timelock: Locks funds until specific block height
    - htlc: Hash Time Lock Contract for atomic swaps
    - simple_lock: Basic single signature lock

    **Or provide custom KISSVM code using globals like:**
    - @BLOCK: Current block number
    - @AMOUNT: Transaction amount
    - SIGNEDBY(pubkey): Check if transaction signed by key
    - @STATE(n): Access state variable

    **Example KISSVM:**
    ```
    LET owner = @PUBKEY
    IF SIGNEDBY(owner) THEN
        RETURN TRUE
    ENDIF
    RETURN FALSE
    ```

    **Note:** Call get_minima_primer() first for full KISSVM reference.

    Returns contract details including script and compilation result.
    """
    client = get_client()
    return contract_tools.create_contract_script(client, name, template, script, description)


@mcp.tool()
def validate_contract_script(
    script: Annotated[str, Field(description="KISSVM script code to validate")],
    check_semantics: Annotated[bool, Field(description="Enable deep semantic validation")] = True
) -> Dict[str, Any]:
    """
    Validate KISSVM contract syntax and semantics.

    Returns errors, warnings, and compilation status.
    """
    client = get_client()
    return contract_tools.validate_contract_script(client, script, check_semantics)


@mcp.tool()
def compile_contract(
    script: Annotated[str, Field(description="KISSVM script to compile")],
    optimize: Annotated[bool, Field(description="Enable optimizations")] = False
) -> Dict[str, Any]:
    """
    Compile KISSVM script to bytecode and get contract address.
    """
    client = get_client()
    return contract_tools.compile_contract(client, script, optimize)


@mcp.tool()
def test_contract(
    script: Annotated[str, Field(description="KISSVM script to test")],
    test_inputs: Annotated[Dict[str, Any], Field(description="Test input parameters")],
    expected_output: Annotated[Optional[bool], Field(description="Expected test result")] = None
) -> Dict[str, Any]:
    """
    Test contract with mock inputs.

    Executes contract with test data and optionally verifies expected output.
    """
    client = get_client()
    return contract_tools.test_contract(client, script, test_inputs, expected_output)


@mcp.tool()
def get_contract_templates() -> Dict[str, Any]:
    """
    Get available KISSVM contract templates.

    Returns list of templates with descriptions and parameters.
    """
    return contract_tools.get_contract_templates()


@mcp.tool()
def list_contracts() -> Dict[str, Any]:
    """
    List all saved smart contracts/scripts.
    """
    client = get_client()
    return contract_tools.list_contracts(client)


@mcp.tool()
def get_contract_details(
    address: Annotated[str, Field(description="Contract address")]
) -> Dict[str, Any]:
    """
    Get detailed information about a contract.
    """
    client = get_client()
    return contract_tools.get_contract_details(client, address)


@mcp.tool()
def get_contract_template_by_id(
    template_id: Annotated[str, Field(description="Template ID")]
) -> Dict[str, Any]:
    """
    Get full template details including script code.
    """
    return contract_tools.get_contract_template_by_id(template_id)


@mcp.tool()
def get_script_globals() -> Dict[str, Any]:
    """
    Get available KISSVM globals and functions.

    Returns documentation for @BLOCK, @AMOUNT, SIGNEDBY(), etc.
    """
    client = get_client()
    return contract_tools.get_script_globals(client)


# ============================================================================
# Transaction Builder Tools
# ============================================================================


@mcp.tool()
def create_custom_transaction(
    transaction_id: Annotated[Optional[str], Field(description="Optional transaction ID")] = None
) -> Dict[str, Any]:
    """
    Create a new custom transaction for manual UTxO management.

    **Minima uses the UTxO model** (like Bitcoin), not accounts (like Ethereum).
    Instead of balances, you have discrete "coins" (UTxOs) that can be spent.

    **Custom transactions let you:**
    - Select specific coins to spend (manual coin selection)
    - Create multiple outputs with different amounts/tokens
    - Add custom scripts to outputs
    - Build atomic swaps, multisig transactions, etc.

    **Workflow:**
    1. create_custom_transaction() - Start building
    2. add_transaction_input() - Add coins to spend
    3. add_transaction_output() - Create new coins
    4. sign_transaction() - Sign with wallet
    5. simulate_transaction() - Test (optional but recommended!)
    6. post_transaction() - Broadcast to network

    **For simple sends, use send_minima() instead.**

    Returns transaction ID for subsequent operations.
    """
    client = get_client()
    return transaction_tools.create_custom_transaction(client, transaction_id)


@mcp.tool()
def add_transaction_input(
    transaction_id: Annotated[str, Field(description="Transaction ID")],
    coin_id: Annotated[str, Field(description="Coin ID to spend")],
    amount: Annotated[Optional[str], Field(description="Amount")] = None,
    script: Annotated[Optional[str], Field(description="Custom script")] = None
) -> Dict[str, Any]:
    """
    Add input (coin) to custom transaction.
    """
    client = get_client()
    return transaction_tools.add_transaction_input(client, transaction_id, coin_id, amount, script)


@mcp.tool()
def add_transaction_output(
    transaction_id: Annotated[str, Field(description="Transaction ID")],
    address: Annotated[str, Field(description="Recipient address")],
    amount: Annotated[str, Field(description="Amount to send")],
    tokenid: Annotated[str, Field(description="Token ID")] = "0x00",
    state: Annotated[Optional[Dict[str, str]], Field(description="State variables")] = None
) -> Dict[str, Any]:
    """
    Add output to custom transaction.
    """
    client = get_client()
    return transaction_tools.add_transaction_output(client, transaction_id, address, amount, tokenid, state)


@mcp.tool()
def sign_transaction(
    transaction_id: Annotated[str, Field(description="Transaction ID")]
) -> Dict[str, Any]:
    """
    Sign transaction with wallet keys.
    """
    client = get_client()
    return transaction_tools.sign_transaction(client, transaction_id)


@mcp.tool()
def post_transaction(
    transaction_id: Annotated[str, Field(description="Transaction ID")]
) -> Dict[str, Any]:
    """
    Broadcast transaction to network.
    """
    client = get_client()
    return transaction_tools.post_transaction(client, transaction_id)


@mcp.tool()
def simulate_transaction(
    transaction_id: Annotated[str, Field(description="Transaction ID")]
) -> Dict[str, Any]:
    """
    Simulate transaction without broadcasting.

    Validates transaction and estimates fees.
    """
    client = get_client()
    return transaction_tools.simulate_transaction(client, transaction_id)


@mcp.tool()
def get_transaction_status(
    transaction_id: Annotated[str, Field(description="Transaction ID")]
) -> Dict[str, Any]:
    """
    Get custom transaction status and details.
    """
    client = get_client()
    return transaction_tools.get_transaction_status(client, transaction_id)


@mcp.tool()
def delete_transaction(
    transaction_id: Annotated[str, Field(description="Transaction ID")]
) -> Dict[str, Any]:
    """
    Delete/cancel custom transaction.
    """
    client = get_client()
    return transaction_tools.delete_transaction(client, transaction_id)


@mcp.tool()
def get_transaction_templates() -> Dict[str, Any]:
    """
    Get available transaction templates.

    Templates for common patterns like atomic swaps, multisig, etc.
    """
    return transaction_tools.get_transaction_templates()


@mcp.tool()
def list_active_transactions() -> Dict[str, Any]:
    """
    List all active custom transactions.
    """
    return transaction_tools.list_active_transactions()


@mcp.tool()
def import_transaction(
    transaction_data: Annotated[str, Field(description="Transaction hex data")]
) -> Dict[str, Any]:
    """
    Import transaction from hex data.
    """
    client = get_client()
    return transaction_tools.import_transaction(client, transaction_data)


@mcp.tool()
def export_transaction(
    transaction_id: Annotated[str, Field(description="Transaction ID")]
) -> Dict[str, Any]:
    """
    Export transaction as hex data for sharing.
    """
    client = get_client()
    return transaction_tools.export_transaction(client, transaction_id)


# ============================================================================
# Event System Tools
# ============================================================================


@mcp.tool()
def subscribe_to_events(
    event_types: Annotated[list[str], Field(description="Event types to subscribe to")],
    webhook_url: Annotated[Optional[str], Field(description="Optional webhook URL")] = None
) -> Dict[str, Any]:
    """
    Subscribe to blockchain events for real-time notifications.

    Events: NEWBLOCK, NEWBALANCE, MINING, MAXIMA, MDS_PENDING, etc.
    """
    return event_tools.subscribe_to_events(event_types, webhook_url)


@mcp.tool()
def unsubscribe_from_events(
    subscription_id: Annotated[str, Field(description="Subscription ID")]
) -> Dict[str, Any]:
    """
    Unsubscribe from events.
    """
    return event_tools.unsubscribe_from_events(subscription_id)


@mcp.tool()
def get_event_history(
    event_type: Annotated[Optional[str], Field(description="Filter by event type")] = None,
    start_time: Annotated[Optional[str], Field(description="Start timestamp")] = None,
    end_time: Annotated[Optional[str], Field(description="End timestamp")] = None,
    limit: Annotated[int, Field(description="Max results")] = 100
) -> Dict[str, Any]:
    """
    Get past events from history.
    """
    return event_tools.get_event_history(event_type, start_time, end_time, limit)


@mcp.tool()
def poll_events(
    subscription_id: Annotated[Optional[str], Field(description="Subscription ID")] = None
) -> Dict[str, Any]:
    """
    Poll for new events (non-blocking).
    """
    return event_tools.poll_events(subscription_id)


@mcp.tool()
def watch_address(
    address: Annotated[str, Field(description="Address to monitor")],
    event_types: Annotated[Optional[list[str]], Field(description="Event types to track")] = None
) -> Dict[str, Any]:
    """
    Monitor specific address for activity.

    Get notified when address receives funds or transactions.
    """
    client = get_client()
    return event_tools.watch_address(client, address, event_types)


@mcp.tool()
def unwatch_address(
    watch_id: Annotated[str, Field(description="Watch ID")]
) -> Dict[str, Any]:
    """
    Stop watching an address.
    """
    return event_tools.unwatch_address(watch_id)


@mcp.tool()
def get_watched_addresses() -> Dict[str, Any]:
    """
    Get list of all watched addresses.
    """
    return event_tools.get_watched_addresses()


@mcp.tool()
def get_event_statistics() -> Dict[str, Any]:
    """
    Get event statistics and analytics.
    """
    return event_tools.get_event_statistics()


@mcp.tool()
def get_pending_transactions_list() -> Dict[str, Any]:
    """
    Get pending transactions requiring confirmation.
    """
    client = get_client()
    return event_tools.get_pending_transactions(client)


@mcp.tool()
def list_event_subscriptions() -> Dict[str, Any]:
    """
    List all active event subscriptions.
    """
    return event_tools.list_subscriptions()


@mcp.tool()
def get_available_event_types() -> Dict[str, Any]:
    """
    Get list of available event types with descriptions.
    """
    return event_tools.get_available_event_types()


# ============================================================================
# Maxima P2P Messaging Tools
# ============================================================================


@mcp.tool()
def get_maxima_address() -> Dict[str, Any]:
    """
    Get your Maxima P2P address for receiving messages.
    """
    client = get_client()
    return maxima_tools.get_maxima_address(client)


@mcp.tool()
def send_maxima_message(
    to_address: Annotated[str, Field(description="Recipient Maxima address")],
    message: Annotated[str, Field(description="Message content")],
    application: Annotated[str, Field(description="Application identifier")] = "general"
) -> Dict[str, Any]:
    """
    Send P2P encrypted message via Maxima.

    **Maxima** is Minima's P2P messaging layer - enables direct node-to-node
    communication without central servers.

    **What is Maxima?**
    - Encrypted messaging between Minima nodes
    - Similar to email but decentralized
    - Each node has a unique Maxima address
    - Messages route through P2P network

    **Use cases:**
    - Messaging applications
    - P2P trading/markets
    - Decentralized social networks
    - Direct node-to-node protocols
    - Encrypted coordination between parties

    **Application identifier** groups messages by app (like email subjects).
    Use consistent identifiers for your app so recipients can filter.

    **Note:** Get recipient's Maxima address first using their contact info
    or by having them call get_maxima_address().

    Returns send result with confirmation.
    """
    client = get_client()
    return maxima_tools.send_maxima_message(client, to_address, message, application)


@mcp.tool()
def get_maxima_contacts() -> Dict[str, Any]:
    """
    List all Maxima contacts.
    """
    client = get_client()
    return maxima_tools.get_maxima_contacts(client)


@mcp.tool()
def add_maxima_contact(
    name: Annotated[str, Field(description="Contact name")],
    address: Annotated[str, Field(description="Maxima address")]
) -> Dict[str, Any]:
    """
    Add new Maxima contact.
    """
    client = get_client()
    return maxima_tools.add_maxima_contact(client, name, address)


@mcp.tool()
def remove_maxima_contact(
    name: Annotated[str, Field(description="Contact name")]
) -> Dict[str, Any]:
    """
    Remove Maxima contact.
    """
    client = get_client()
    return maxima_tools.remove_maxima_contact(client, name)


@mcp.tool()
def get_maxima_messages(
    application: Annotated[Optional[str], Field(description="Filter by application")] = None,
    from_address: Annotated[Optional[str], Field(description="Filter by sender")] = None,
    limit: Annotated[int, Field(description="Max results")] = 50
) -> Dict[str, Any]:
    """
    Get received Maxima messages.

    Note: Subscribe to MAXIMA events for real-time message reception.
    """
    client = get_client()
    return maxima_tools.get_maxima_messages(client, application, from_address, limit)


@mcp.tool()
def create_static_maxima_address(
    name: Annotated[Optional[str], Field(description="Optional name")] = None
) -> Dict[str, Any]:
    """
    Create static Maxima address.

    Static addresses don't change between sessions.
    """
    client = get_client()
    return maxima_tools.create_static_maxima_address(client, name)


@mcp.tool()
def get_maxima_info() -> Dict[str, Any]:
    """
    Get detailed Maxima status and configuration.
    """
    client = get_client()
    return maxima_tools.get_maxima_info(client)


@mcp.tool()
def set_maxima_name(
    name: Annotated[str, Field(description="Display name")]
) -> Dict[str, Any]:
    """
    Set your Maxima display name.
    """
    client = get_client()
    return maxima_tools.set_maxima_name(client, name)


# ============================================================================
# Token Management Tools
# ============================================================================


@mcp.tool()
def get_token_details(
    tokenid: Annotated[str, Field(description="Token ID")]
) -> Dict[str, Any]:
    """
    Get comprehensive token information including balance.
    """
    client = get_client()
    return token_tools.get_token_details(client, tokenid)


@mcp.tool()
def search_tokens(
    query: Annotated[Optional[str], Field(description="Search term")] = None
) -> Dict[str, Any]:
    """
    Search for tokens by name or token ID.
    """
    client = get_client()
    return token_tools.search_tokens(client, query)


@mcp.tool()
def get_token_holders(
    tokenid: Annotated[str, Field(description="Token ID")]
) -> Dict[str, Any]:
    """
    Get list of addresses holding token with balances.
    """
    client = get_client()
    return token_tools.get_token_holders(client, tokenid)


@mcp.tool()
def get_token_transactions(
    tokenid: Annotated[str, Field(description="Token ID")],
    limit: Annotated[int, Field(description="Max results")] = 50
) -> Dict[str, Any]:
    """
    Get token transaction history.
    """
    client = get_client()
    return token_tools.get_token_transactions(client, tokenid, limit)


@mcp.tool()
def validate_token_script(
    script: Annotated[str, Field(description="Token script to validate")]
) -> Dict[str, Any]:
    """
    Validate token creation script.
    """
    client = get_client()
    return token_tools.validate_token_script(client, script)


@mcp.tool()
def get_token_supply(
    tokenid: Annotated[str, Field(description="Token ID")]
) -> Dict[str, Any]:
    """
    Get total and circulating token supply.
    """
    client = get_client()
    return token_tools.get_token_supply(client, tokenid)


@mcp.tool()
def analyze_token(
    tokenid: Annotated[str, Field(description="Token ID")]
) -> Dict[str, Any]:
    """
    Comprehensive token analysis.

    Returns holders, supply, distribution, and concentration metrics.
    """
    client = get_client()
    return token_tools.analyze_token(client, tokenid)


# ============================================================================
# Developer Tools
# ============================================================================


@mcp.tool()
def get_node_metrics() -> Dict[str, Any]:
    """
    Get detailed node performance metrics.

    Returns memory, network, blockchain stats.
    """
    client = get_client()
    return dev_tools.get_node_metrics(client)


@mcp.tool()
def get_chain_statistics() -> Dict[str, Any]:
    """
    Get blockchain statistics and analytics.
    """
    client = get_client()
    return dev_tools.get_chain_statistics(client)


@mcp.tool()
def run_performance_test(
    test_type: Annotated[str, Field(description="Test type: status_query, balance_query, script_compilation")] = "status_query"
) -> Dict[str, Any]:
    """
    Run node performance tests.

    Benchmarks query speed, script compilation, etc.
    """
    client = get_client()
    return dev_tools.run_performance_test(client, test_type)


@mcp.tool()
def get_memory_usage() -> Dict[str, Any]:
    """
    Get node memory usage statistics.
    """
    client = get_client()
    return dev_tools.get_memory_usage(client)


@mcp.tool()
def get_disk_usage() -> Dict[str, Any]:
    """
    Get node disk usage information.
    """
    client = get_client()
    return dev_tools.get_disk_usage(client)


@mcp.tool()
def diagnose_node() -> Dict[str, Any]:
    """
    Run comprehensive node diagnostics.

    Checks health, peers, sync status, and identifies issues.
    """
    client = get_client()
    return dev_tools.diagnose_node(client)


@mcp.tool()
def get_available_performance_tests() -> Dict[str, Any]:
    """
    Get list of available performance tests.
    """
    return dev_tools.get_available_tests()


# ============================================================================
# Main Entry Point
# ============================================================================


def main():
    """Run the Minima MCP server."""
    logger.info("Starting Minima MCP Server...")

    # Log configuration
    logger.info(f"Minima Host: {os.getenv('MINIMA_HOST', 'localhost')}")
    logger.info(f"Minima Port: {os.getenv('MINIMA_PORT', '9003')}")

    # Load and log primer for AI context (first 500 chars to avoid log spam)
    primer = get_minima_primer()
    logger.info(f"Minima primer loaded ({len(primer)} characters). AI now has full blockchain context.")
    logger.info("Key primer sections available: KISSVM contracts, MiniDapp stores, transaction patterns, etc.")

    # Run the server
    mcp.run()


if __name__ == "__main__":
    main()

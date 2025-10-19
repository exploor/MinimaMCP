"""Minima Blockchain Primer - Context for AI assistants."""


def get_minima_primer() -> str:
    """Get comprehensive Minima blockchain primer for AI understanding."""

    return """
# Minima Blockchain Primer

## Core Concepts

### What is Minima?
Minima is a ultra-lean blockchain designed to run on mobile devices. Every user runs a full validating node.

### Key Differences from Other Blockchains
- **No miners**: Uses Proof of Work but all users participate
- **UTxO model**: Like Bitcoin, not account-based like Ethereum
- **On-chain contracts**: All smart contracts run on Layer 1
- **MiniDapps**: Web apps that run locally and connect to your node

---

## KISSVM (Keep It Simple Stupid Virtual Machine)

### What is KISSVM?
Minima's smart contract language. Simple, explicit scripting language for on-chain contracts.

### KISSVM Basics
- **Turing complete**: Can express any computation
- **Stack-based**: Similar to Bitcoin Script but more powerful
- **Explicit state**: State variables must be declared
- **RETURN TRUE/FALSE**: Contracts must return boolean

### Key KISSVM Globals
- `@BLOCK` - Current block number
- `@AMOUNT` - Transaction amount
- `@TOKENID` - Token being transacted
- `SIGNEDBY(pubkey)` - Check if transaction signed by key
- `@STATE(n)` - Access state variable n

### Example KISSVM Contract
```
LET owner = @PUBKEY
IF SIGNEDBY(owner) THEN
    RETURN TRUE
ENDIF
RETURN FALSE
```

---

## MAST (Merkle Abstract Syntax Tree)

### What is MAST?
Every KISSVM script is compiled into a MAST - a Merkle tree of the script's structure.

### Why MAST Matters
- **Privacy**: Only reveal the branch you execute
- **Efficiency**: Smaller on-chain footprint
- **Flexibility**: Complex contracts with many paths

### Script Address
When you compile a script, you get an **address** (the MAST root hash). This is how contracts are identified on-chain.

---

## UTxO Model

### What are UTxOs?
Unspent Transaction Outputs - discrete chunks of value that can be spent.

### UTxO vs Account Model
- **Ethereum**: Accounts with balances (account model)
- **Minima**: Coins that can be spent (UTxO model)
- **Minima coins**: Each has an amount, token ID, and address (script)

### Why This Matters
- Custom transactions require selecting specific coins (UTxOs)
- Each coin can have its own spending conditions (script)
- State is stored per-coin, not globally

---

## Transactions

### Simple Transactions
Use `send_minima()` - automatically selects coins and creates change.

### Custom Transactions
For advanced use cases:
1. Create transaction (`create_custom_transaction`)
2. Add inputs - coins you're spending (`add_transaction_input`)
3. Add outputs - new coins being created (`add_transaction_output`)
4. Sign transaction (`sign_transaction`)
5. Post to network (`post_transaction`)

### Transaction Flow
```
Inputs (old coins) → [Transaction Script] → Outputs (new coins)
```

---

## State Variables

### What are State Variables?
Key-value pairs stored in transaction outputs (coins).

### How to Use
```kissvm
// Set state
@STATE(0) = 42

// Read state
LET value = @STATE(0)

// Check if state unchanged
IF SAMESTATE(0) THEN
    RETURN TRUE
ENDIF
```

### Use Cases
- Counters
- Flags
- Contract state
- Multi-step protocols

---

## MDS (MiniDapp System)

### What is MDS?
The system for running MiniDapps (web apps) on Minima.

### MDS Architecture
- **Port 9003**: HTTPS server for MiniDapps
- **Session-based auth**: Password-protected access
- **MDS.js library**: JavaScript API for MiniDapps
- **Events**: Real-time notifications (NEWBLOCK, NEWBALANCE, etc.)

### MiniDapp Structure
```
MyDapp/
├── dapp.conf       # Manifest (name, version, etc.)
└── index.html      # Entry point with MDS.js
```

### MDS.js Pattern
```javascript
MDS.init(function(msg) {
    if(msg.event == "inited") {
        // Connected to Minima!
        MDS.cmd("balance", function(resp) {
            console.log(resp.response);
        });
    }
});
```

---

## MiniDapp Stores

### What are MiniDapp Stores?
JSON manifests that define curated collections of MiniDapps for the Minima Storefront ecosystem.

### Storefront Architecture
- **Storefront MiniDapp**: Main app (`storefront.minidapp`) that displays stores
- **Store JSON Files**: Plain JSON hosted at URLs defining MiniDapp collections
- **Zero Hosting Required**: Stores can be hosted anywhere accessible via HTTPS

### Store JSON Format
```json
{
  "name": "My DeFi Store",
  "description": "Best DeFi apps for Minima",
  "banner": "https://example.com/banner.jpg",
  "icon": "https://example.com/icon.png",
  "version": "1.0",
  "manifest_version": 2,
  "dapps": [
    {
      "file": "https://minima.global/dapps/UniswapClone.mds.zip",
      "icon": "https://example.com/uni-icon.png",
      "name": "Uniswap Clone",
      "date": "Oct 18, 2025",
      "description": "Decentralized exchange",
      "repository_url": "https://github.com/example/uni-clone",
      "version": "2.1.0",
      "about": "Full DEX functionality on Minima",
      "screenshots": [
        "https://example.com/screenshot1.jpg",
        "https://example.com/screenshot2.jpg"
      ],
      "release_notes": "# Latest Updates\n- Improved liquidity\n- Bug fixes",
      "history": [
        {
          "version": "2.1.0",
          "date": "Oct 18, 2025",
          "release_notes": "# Version 2.1.0\n- Major UI overhaul"
        }
      ]
    }
  ]
}
```

### Creating Stores with MCP
```python
from minima_mcp.server import create_minidapp_store

# Create empty store (add apps later)
result = create_minidapp_store(
    name="DeFi Hub",
    description="Best DeFi apps on Minima"
)

# Create store with initial apps
result = create_minidapp_store(
    name="Web3 Tools",
    description="Essential Web3 utilities",
    dapps=[
        {
            "name": "Token Creator",
            "file": "https://example.com/token-creator.mds.zip",
            "description": "Create custom tokens",
            "version": "1.0.0"
        }
    ]
)

# Create store by scanning installed MiniDapps
result = create_minidapp_store(
    name="My Apps",
    description="My installed MiniDapp collection",
    scan_installed=True  # Automatically include all installed MiniDapps
)

print(f"Store URL: {result['data']['public_url']}")
# Output: http://127.0.0.1:8080/my_apps.json

# Usage instructions are provided
for instruction in result['data']['usage_instructions']:
    print(instruction)
```

### Store Integration Options

#### Option 1: Direct Sharing
Share the store URL directly with users who can paste it into their Minima Storefront MiniDapp.

#### Option 2: Host on Web Server
Upload the JSON file to any web server (Apache, Nginx, GitHub Pages, IPFS) for permanent hosting.

#### Option 3: Official Registry
Submit your store to the official Minima Storefront registry for community discoverability.

### Managing Stores
Store JSON files are created in the `minidapp_stores/` directory and automatically served via HTTP. Each store gets its own URL that can be shared directly.

```python
# Stores are accessible at:
# http://127.0.0.1:8080/store_name.json

# To manage your stores:
# 1. Check minidapp_stores/ directory for JSON files
# 2. Edit JSON files directly to add/remove MiniDapps
# 3. Restart HTTP server if needed
```

### Store Format
Stores are simple JSON files following the Minima Storefront specification:
```json
{
  "name": "My Store",
  "description": "Store description",
  "version": "1.0",
  "manifest_version": 2,
  "dapps": [
    {
      "name": "App Name",
      "file": "https://example.com/app.mds.zip",
      "description": "App description",
      "version": "1.0.0"
    }
  ]
}
```

### Best Practices
1. **Descriptive Names**: Choose clear, memorable store names
2. **Rich Metadata**: Include icons, banners, and detailed descriptions
3. **Version Management**: Keep version numbers updated
4. **Regular Updates**: Refresh MiniDapp versions and add new apps
5. **Quality Curation**: Only include well-tested, reputable MiniDapps
6. **Hosting**: Use reliable hosting for production stores (GitHub Pages, IPFS, etc.)

### Quick Start Commands
When using MCP, simply say:
- "Create a MiniDapp store called 'Gaming Hub'"
- "Make a store with DeFi apps"
- "Create an empty store for Web3 tools"

The system will automatically create the JSON file and provide the public URL!

---

## Maxima

### What is Maxima?
Minima's P2P messaging layer - encrypted, decentralized communication.

### Maxima Addresses
- Similar to email addresses
- Unique per node
- Can be static (persistent) or dynamic

### Use Cases
- Messaging apps
- P2P trading
- Decentralized social
- Any app needing direct node-to-node communication

### Message Flow
```
Your Node → Maxima Network → Recipient Node
```

---

## Events

### Available Events
- **NEWBLOCK**: New block added to chain
- **NEWBALANCE**: Your balance changed (new coin received)
- **MINING**: Mining started or stopped
- **MAXIMA**: P2P message received
- **MDS_PENDING**: Transaction requires confirmation
- **MDS_TIMER_10SECONDS**: 10 second tick
- **MDS_TIMER_1HOUR**: 1 hour tick

### Why Events Matter
- Real-time monitoring
- Reactive applications
- Auto-processing transactions
- Building responsive MiniDapps

---

## Tokens

### How Tokens Work
- Created with `tokencreate` command
- Each token has unique ID (tokenid)
- Tokens use same UTxO model as Minima
- Can have custom scripts (token scripts)

### Token Scripts
```kissvm
// Token can only be spent by owner
LET owner = @PUBKEY
IF SIGNEDBY(owner) THEN
    RETURN TRUE
ENDIF
RETURN FALSE
```

---

## Common Patterns

### 1. Multisig Wallet
```kissvm
// 2-of-3 multisig
LET sigcount = 0
IF SIGNEDBY(@KEY1) THEN LET sigcount = sigcount + 1 ENDIF
IF SIGNEDBY(@KEY2) THEN LET sigcount = sigcount + 1 ENDIF
IF SIGNEDBY(@KEY3) THEN LET sigcount = sigcount + 1 ENDIF
IF sigcount GTE 2 THEN RETURN TRUE ENDIF
RETURN FALSE
```

### 2. Timelock
```kissvm
// Funds locked until block height
LET unlock_block = @UNLOCK_HEIGHT
IF @BLOCK GTE unlock_block THEN
    IF SIGNEDBY(@OWNER) THEN
        RETURN TRUE
    ENDIF
ENDIF
RETURN FALSE
```

### 3. HTLC (Hash Time Lock Contract)
```kissvm
// Atomic swap primitive
LET secret_hash = @HASH
LET timeout = @TIMEOUT_BLOCK

// Claim with secret
IF SHA3(@SECRET) EQ secret_hash THEN
    IF SIGNEDBY(@RECIPIENT) THEN
        RETURN TRUE
    ENDIF
ENDIF

// Refund after timeout
IF @BLOCK GTE timeout THEN
    IF SIGNEDBY(@SENDER) THEN
        RETURN TRUE
    ENDIF
ENDIF
RETURN FALSE
```

---

## Best Practices

### Smart Contracts
1. Always end with explicit `RETURN TRUE` or `RETURN FALSE`
2. Use meaningful variable names
3. Test with `test_contract()` before deploying
4. Validate with `validate_contract_script()` first

### Transactions
1. Use `simulate_transaction()` before posting
2. Check coin amounts match (inputs = outputs)
3. Consider transaction fees
4. For complex transactions, use custom transaction builder

### MiniDapps
1. Always use MDS.js for blockchain interaction
2. Handle `inited` event before making calls
3. Provide user feedback for all operations
4. Test locally before deploying

### Tokens
1. Choose decimals carefully (usually 8)
2. Validate token script before creation
3. Consider total supply and distribution
4. Document token purpose and rules

---

## Security Considerations

### Smart Contracts
- Test thoroughly - contracts are immutable once deployed
- Consider edge cases (what if @BLOCK is huge?)
- Check integer overflow/underflow
- Validate all state transitions

### Transactions
- Always verify outputs before signing
- Check transaction details in simulation
- Be careful with state variables
- Consider MEV (transaction ordering attacks)

### MiniDapps
- Don't store secrets in MiniDapp code
- Validate all user input
- Use HTTPS (MDS provides this)
- Consider MDS_PENDING confirmations for important actions

---

## Command Syntax

### Common Patterns
```
# Basic command
command

# Command with parameter
command param:value

# Multiple parameters
command param1:value1 param2:value2

# Script parameter (quoted)
command script:"RETURN TRUE"
```

---

## When to Use Each Tool Category

### Use Contract Studio when:
- Creating smart contracts
- Need multisig, timelock, or HTLC
- Building DeFi primitives
- Want template-based development

### Use Transaction Builder when:
- Need manual coin selection
- Building atomic swaps
- Creating complex multi-party transactions
- Need to specify exact inputs/outputs

### Use Event System when:
- Monitoring blockchain in real-time
- Building reactive applications
- Need to watch specific addresses
- Want transaction notifications

### Use Maxima Messaging when:
- Building P2P applications
- Need encrypted communication
- Creating decentralized social apps
- Building direct node-to-node protocols

### Use Token Management when:
- Analyzing token distribution
- Need holder analytics
- Want transaction history
- Checking token supply metrics

### Use Developer Tools when:
- Debugging node issues
- Performance testing
- Checking node health
- Analyzing blockchain statistics

---

## Quick Reference

### Key Concepts
- **KISSVM**: Smart contract language
- **MAST**: Merkle tree of script
- **UTxO**: Unspent transaction output (coin)
- **MDS**: MiniDapp system
- **Maxima**: P2P messaging
- **State**: Per-coin key-value storage

### Important Globals
- `@BLOCK`: Current block number
- `@AMOUNT`: Transaction amount
- `@TOKENID`: Token ID
- `@STATE(n)`: State variable n
- `SIGNEDBY(key)`: Check signature
- `SHA3(data)`: Hash data

### Tool Selection Guide
- Simple send → `send_minima()`
- Smart contract → Contract Studio tools
- Custom transaction → Transaction Builder tools
- Real-time monitoring → Event System tools
- P2P message → Maxima tools
- Token analysis → Token Management tools
- Node diagnostics → Developer tools

---

## MiniDapp Store Creation

### What are MiniDapp Stores?
MiniDapp Stores are JSON manifests that allow users to discover and install MiniDapps through the Minima Storefront MiniDapp. Stores contain metadata about available MiniDapps including download URLs, descriptions, and version info.

### When to Create a Store
- Publishing multiple MiniDapps as a collection
- Building a marketplace or app directory
- Organizing related MiniDapps by category
- Creating a branded app store

### Store Creation Process

#### Step 1: Use the create_minidapp_store MCP Tool
When a user asks to "create a store", use the `create_minidapp_store` MCP tool:

```python
# Example: Create a gaming store
result = create_minidapp_store(
    name="Gaming Hub",
    description="Collection of blockchain games and gaming utilities",
    dapps=[
        {
            "name": "Block Poker",
            "description": "Decentralized poker game with real stakes",
            "file": "https://gaming-site.com/blockpoker.mds.zip",
            "version": "1.0.0"
        },
        {
            "name": "NFT Card Game",
            "description": "Collectible card game using NFTs",
            "file": "https://gaming-site.com/cards.mds.zip",
            "version": "1.0.0"
        }
    ]
)
```

#### Step 2: Handle the Response
The tool returns:
- `public_url`: Web-accessible URL for the store JSON
- `usage_instructions`: Step-by-step instructions for users
- `store_json`: The complete store manifest

#### Step 3: Start HTTP Server (if needed)
If the store is created locally, start an HTTP server to serve it:

```bash
cd minidapp_stores
python -m http.server 8080
```

#### Step 4: Provide User Instructions
Give users clear instructions to add the store to Minima Storefront:
1. Copy the public URL (e.g., `http://127.0.0.1:8080/store_name.json`)
2. Open Minima Storefront MiniDapp
3. Click the '+' button
4. Paste the URL and load

### Store Creation Scenario

**User says:** "Create a DeFi store with 3 apps"

**Response:**
1. Call `create_minidapp_store()` with appropriate parameters
2. Start HTTP server if needed
3. Return the public URL and usage instructions

**Example Implementation:**
```python
result = create_minidapp_store(
    name="DeFi Hub",
    description="Decentralized finance applications",
    dapps=[
        {
            "name": "DEX",
            "description": "Decentralized exchange",
            "file": "https://defi-site.com/dex.mds.zip",
            "version": "1.0.0"
        },
        {
            "name": "Lending",
            "description": "P2P lending platform",
            "file": "https://defi-site.com/lending.mds.zip",
            "version": "1.0.0"
        },
        {
            "name": "Yield Farm",
            "description": "Automated yield farming",
            "file": "https://defi-site.com/yield.mds.zip",
            "version": "1.0.0"
        }
    ]
)
```

### Store Management Tools
- `create_minidapp_store()`: Create new stores
- `update_minidapp_store()`: Modify existing stores
- `list_minidapp_stores()`: View all stores

### Important Notes
- Stores must be web-accessible (localhost may not work in MiniDapp context)
- Use HTTPS URLs when possible for production stores
- Include proper metadata (icons, descriptions, versions)
- Test store loading in Minima Storefront before publishing

---

This primer provides the essential context for understanding and using Minima's unique features effectively.
"""

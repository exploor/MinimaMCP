# Complete Minima MCP Server Reference

## Overview

**Total Tools:** 69 
**Status:** ✅ Fully Implemented & Tested

The Minima MCP Server now provides **complete coverage** of all Minima blockchain functionality, enabling full development, deployment, and management of smart contracts, MiniDapps, P2P messaging, and blockchain operations.

---

## Tool Categories

### 1. Blockchain Query Tools (6 tools)
Basic blockchain data retrieval

### 2. Transaction Tools (3 tools)
Simple transaction operations

### 3. Network Tools (2 tools)
Network information

### 4. MiniDapp Tools (3 tools)
MiniDapp management

### 5. MiniDapp Builder Tools (4 tools)
Create and deploy MiniDapps

### 6. Contract Studio Tools (9 tools) ⭐ NEW
KISSVM smart contract development

### 7. Transaction Builder Tools (12 tools) ⭐ NEW
Advanced custom transactions

### 8. Event System Tools (11 tools) ⭐ NEW
Real-time blockchain monitoring

### 9. Maxima Messaging Tools (9 tools) ⭐ NEW
P2P encrypted messaging

### 10. Token Management Tools (7 tools) ⭐ NEW
Advanced token operations

### 11. Developer Tools (7 tools) ⭐ NEW
Debugging and analytics

### 12. Utility Tools (2 tools)
General utilities

---

## 📚 Complete Tool Reference

### Blockchain Query Tools (6)

#### `get_balance(address?, tokenid?)`
Get wallet balance for Minima or specific tokens.

**Parameters:**
- `address` (optional): Specific address
- `tokenid` (optional): Token ID (0x00 for Minima)

**Returns:** Balance information

#### `get_node_status()`
Get current node status and blockchain information.

**Returns:** Chain height, version, sync status, uptime

#### `get_address()`
Get a Minima address for receiving funds.

**Returns:** New or existing address

#### `list_tokens(tokenid?)`
List all tokens or get specific token info.

**Parameters:**
- `tokenid` (optional): Specific token ID

**Returns:** Token details

#### `get_coins(relevant?, sendable?, address?, tokenid?)`
Get coins (UTxOs) information.

**Parameters:**
- `relevant` (default: true): Show only relevant coins
- `sendable` (default: false): Show only sendable coins
- `address` (optional): Filter by address
- `tokenid` (optional): Filter by token

**Returns:** Coin/UTxO list

#### `search_blockchain(block?, address?, tokenid?)`
Search blockchain for transactions and blocks.

**Parameters:**
- `block` (optional): Block number
- `address` (optional): Search by address
- `tokenid` (optional): Search by token

**Returns:** Search results

---

### Transaction Tools (3)

#### `send_minima(amount, address, tokenid?)`
Send Minima or tokens to an address.

**Parameters:**
- `amount`: Amount to send
- `address`: Recipient address
- `tokenid` (default: "0x00"): Token ID

**Returns:** Transaction details

#### `create_token(name, amount, decimals?, description?, icon?, proof?)`
Create a new custom token.

**Parameters:**
- `name`: Token name
- `amount`: Total supply
- `decimals` (default: 8): Decimal places
- `description` (optional): Description
- `icon` (optional): Icon URL
- `proof` (optional): Proof data

**Returns:** Token creation result

#### `get_transaction(txpowid)`
Get transaction details by ID.

**Parameters:**
- `txpowid`: Transaction PoW ID

**Returns:** Transaction information

---

### Network Tools (2)

#### `get_network_info()`
Get network statistics and connection details.

**Returns:** Network information

#### `get_peers()`
Get list of connected peers.

**Returns:** Peer list

---

### MiniDapp Tools (3)

#### `list_minidapps()`
List all installed MiniDapps.

**Returns:** MiniDapp list

#### `install_minidapp(file_path)`
Install MiniDapp from .mds.zip file.

**Parameters:**
- `file_path`: Path to .mds.zip

**Returns:** Installation result

#### `get_minidapp_info(uid)`
Get MiniDapp information.

**Parameters:**
- `uid`: MiniDapp UID

**Returns:** MiniDapp details

---

### MiniDapp Builder Tools (4)

#### `create_minidapp_project(name, description, output_dir, version?, category?)`
Create MiniDapp project structure.

**Parameters:**
- `name`: MiniDapp name
- `description`: Description
- `output_dir`: Output directory
- `version` (default: "1.0.0"): Version
- `category` (default: "Utility"): Category

**Returns:** Project path

#### `write_minidapp_file(project_path, file_name, content)`
Add file to MiniDapp project.

**Parameters:**
- `project_path`: Project directory
- `file_name`: File name
- `content`: File content

**Returns:** File path

#### `package_minidapp(project_path, output_path?)`
Package MiniDapp into .mds.zip.

**Parameters:**
- `project_path`: Project directory
- `output_path` (optional): Output path

**Returns:** Zip path and size

#### `install_packaged_minidapp(zip_path)`
Install packaged MiniDapp to node.

**Parameters:**
- `zip_path`: Path to .mds.zip

**Returns:** Installation result with UID

---

### Contract Studio Tools (9) ⭐ NEW

#### `create_contract_script(name, template?, script?, description?)`
Create KISSVM smart contract script.

**Parameters:**
- `name`: Script name
- `template` (optional): Template ID (multisig_2_of_2, multisig_2_of_3, timelock, htlc, simple_lock)
- `script` (optional): Custom KISSVM code
- `description` (optional): Description

**Returns:** Contract details

**Example:**
```
create_contract_script(
    name="my_multisig",
    template="multisig_2_of_3"
)
```

#### `validate_contract_script(script, check_semantics?)`
Validate KISSVM syntax and semantics.

**Parameters:**
- `script`: KISSVM code
- `check_semantics` (default: true): Deep validation

**Returns:** Errors, warnings, compilation status

#### `compile_contract(script, optimize?)`
Compile KISSVM to bytecode.

**Parameters:**
- `script`: KISSVM code
- `optimize` (default: false): Enable optimizations

**Returns:** Contract address, bytecode

#### `test_contract(script, test_inputs, expected_output?)`
Test contract with mock inputs.

**Parameters:**
- `script`: KISSVM code
- `test_inputs`: Test parameters
- `expected_output` (optional): Expected result

**Returns:** Test results

#### `get_contract_templates()`
Get available contract templates.

**Returns:** Template list with descriptions

**Templates:**
- `multisig_2_of_2`: 2-of-2 multisig
- `multisig_2_of_3`: 2-of-3 multisig
- `timelock`: Time-locked funds
- `htlc`: Hash Time Lock Contract
- `simple_lock`: Basic single signature

#### `list_contracts()`
List all saved contracts.

**Returns:** Contract list

#### `get_contract_details(address)`
Get detailed contract information.

**Parameters:**
- `address`: Contract address

**Returns:** Contract details

#### `get_contract_template_by_id(template_id)`
Get full template details.

**Parameters:**
- `template_id`: Template ID

**Returns:** Template with full script

#### `get_script_globals()`
Get available KISSVM globals and functions.

**Returns:** KISSVM reference

**Globals:**
- Transaction: @AMOUNT, @TOKENID, @TOTIN, @TOTOUT
- Block: @BLOCK, @BLKTIME, @PREVBLKHASH
- Crypto: SIGNEDBY(), SHA3(), SHA2(), MULTISIG()
- State: @STATE(), PREVSTATE(), SAMESTATE()
- Logic: AND, OR, NOT, XOR, NAND, NOR, NXOR
- Math: ADD, SUB, MUL, DIV, MOD, POW
- Comparison: EQ, NEQ, GT, GTE, LT, LTE

---

### Transaction Builder Tools (12) ⭐ NEW

#### `create_custom_transaction(transaction_id?)`
Create new custom transaction for manual UTXO management.

**Parameters:**
- `transaction_id` (optional): Optional ID

**Returns:** Transaction ID

#### `add_transaction_input(transaction_id, coin_id, amount?, script?)`
Add input to transaction.

**Parameters:**
- `transaction_id`: Transaction ID
- `coin_id`: Coin to spend
- `amount` (optional): Amount
- `script` (optional): Custom script

**Returns:** Updated transaction

#### `add_transaction_output(transaction_id, address, amount, tokenid?, state?)`
Add output to transaction.

**Parameters:**
- `transaction_id`: Transaction ID
- `address`: Recipient
- `amount`: Amount
- `tokenid` (default: "0x00"): Token ID
- `state` (optional): State variables

**Returns:** Updated transaction

#### `sign_transaction(transaction_id)`
Sign transaction with wallet keys.

**Parameters:**
- `transaction_id`: Transaction ID

**Returns:** Signing result

#### `post_transaction(transaction_id)`
Broadcast transaction to network.

**Parameters:**
- `transaction_id`: Transaction ID

**Returns:** Transaction hash

#### `simulate_transaction(transaction_id)`
Test transaction without broadcasting.

**Parameters:**
- `transaction_id`: Transaction ID

**Returns:** Validation result, fee estimate

#### `get_transaction_status(transaction_id)`
Get transaction status and details.

**Parameters:**
- `transaction_id`: Transaction ID

**Returns:** Transaction state

#### `delete_transaction(transaction_id)`
Cancel/delete transaction.

**Parameters:**
- `transaction_id`: Transaction ID

**Returns:** Deletion result

#### `get_transaction_templates()`
Get available transaction templates.

**Returns:** Template list

**Templates:**
- simple_send: Basic send
- token_transfer: Token transfer
- multisig_send: Multisig transaction
- atomic_swap: Cross-chain swap

#### `list_active_transactions()`
List all active custom transactions.

**Returns:** Transaction list

#### `import_transaction(transaction_data)`
Import transaction from hex data.

**Parameters:**
- `transaction_data`: Hex data

**Returns:** Transaction ID

#### `export_transaction(transaction_id)`
Export transaction as hex for sharing.

**Parameters:**
- `transaction_id`: Transaction ID

**Returns:** Hex data

---

### Event System Tools (11) ⭐ NEW

#### `subscribe_to_events(event_types, webhook_url?)`
Subscribe to blockchain events.

**Parameters:**
- `event_types`: Array of event types
- `webhook_url` (optional): Webhook URL

**Returns:** Subscription ID

**Event Types:**
- NEWBLOCK: New block added
- NEWBALANCE: Balance changed
- MINING: Mining started/stopped
- MINIMALOG: Log message
- MAXIMA: Maxima message received
- MDS_PENDING: Pending transaction
- MDS_TIMER_10SECONDS: 10s timer
- MDS_TIMER_1HOUR: 1hr timer
- MDS_SHUTDOWN: System shutdown

#### `unsubscribe_from_events(subscription_id)`
Unsubscribe from events.

**Parameters:**
- `subscription_id`: Subscription ID

**Returns:** Result

#### `get_event_history(event_type?, start_time?, end_time?, limit?)`
Get past events.

**Parameters:**
- `event_type` (optional): Filter by type
- `start_time` (optional): Start timestamp
- `end_time` (optional): End timestamp
- `limit` (default: 100): Max results

**Returns:** Event history

#### `poll_events(subscription_id?)`
Poll for new events (non-blocking).

**Parameters:**
- `subscription_id` (optional): Subscription filter

**Returns:** New events

#### `watch_address(address, event_types?)`
Monitor specific address.

**Parameters:**
- `address`: Address to watch
- `event_types` (optional): Events to track

**Returns:** Watch ID

#### `unwatch_address(watch_id)`
Stop watching address.

**Parameters:**
- `watch_id`: Watch ID

**Returns:** Result

#### `get_watched_addresses()`
Get list of watched addresses.

**Returns:** Watch list

#### `get_event_statistics()`
Get event statistics.

**Returns:** Event counts, frequency analysis

#### `get_pending_transactions_list()`
Get pending transactions.

**Returns:** Pending transaction list

#### `list_event_subscriptions()`
List active subscriptions.

**Returns:** Subscription list

#### `get_available_event_types()`
Get available event types with descriptions.

**Returns:** Event type list

---

### Maxima P2P Messaging Tools (9) ⭐ NEW

#### `get_maxima_address()`
Get your Maxima P2P address.

**Returns:** Maxima address and status

#### `send_maxima_message(to_address, message, application?)`
Send P2P message.

**Parameters:**
- `to_address`: Recipient Maxima address
- `message`: Message content
- `application` (default: "general"): App identifier

**Returns:** Send result

#### `get_maxima_contacts()`
List Maxima contacts.

**Returns:** Contact list

#### `add_maxima_contact(name, address)`
Add new contact.

**Parameters:**
- `name`: Contact name
- `address`: Maxima address

**Returns:** Result

#### `remove_maxima_contact(name)`
Remove contact.

**Parameters:**
- `name`: Contact name

**Returns:** Result

#### `get_maxima_messages(application?, from_address?, limit?)`
Get received messages.

**Parameters:**
- `application` (optional): Filter by app
- `from_address` (optional): Filter by sender
- `limit` (default: 50): Max results

**Returns:** Message list

#### `create_static_maxima_address(name?)`
Create static Maxima address.

**Parameters:**
- `name` (optional): Optional name

**Returns:** Static address details

#### `get_maxima_info()`
Get detailed Maxima status.

**Returns:** Maxima configuration

#### `set_maxima_name(name)`
Set your Maxima display name.

**Parameters:**
- `name`: Display name

**Returns:** Result

---

### Token Management Tools (7) ⭐ NEW

#### `get_token_details(tokenid)`
Get comprehensive token information.

**Parameters:**
- `tokenid`: Token ID

**Returns:** Token info and balance

#### `search_tokens(query?)`
Search for tokens.

**Parameters:**
- `query` (optional): Search term

**Returns:** Matching tokens

#### `get_token_holders(tokenid)`
Get token holder list.

**Parameters:**
- `tokenid`: Token ID

**Returns:** Addresses with balances

#### `get_token_transactions(tokenid, limit?)`
Get token transaction history.

**Parameters:**
- `tokenid`: Token ID
- `limit` (default: 50): Max results

**Returns:** Transaction list

#### `validate_token_script(script)`
Validate token creation script.

**Parameters:**
- `script`: Token script

**Returns:** Validation result

#### `get_token_supply(tokenid)`
Get total and circulating supply.

**Parameters:**
- `tokenid`: Token ID

**Returns:** Supply statistics

#### `analyze_token(tokenid)`
Comprehensive token analysis.

**Parameters:**
- `tokenid`: Token ID

**Returns:** Holders, supply, distribution metrics

---

### Developer Tools (7) ⭐ NEW

#### `get_node_metrics()`
Get detailed node performance metrics.

**Returns:** Memory, network, blockchain stats

#### `get_chain_statistics()`
Get blockchain statistics.

**Returns:** Block times, chain size, etc.

#### `run_performance_test(test_type?)`
Run node performance tests.

**Parameters:**
- `test_type` (default: "status_query"): Test to run

**Test Types:**
- status_query: Status command speed
- balance_query: Balance query speed
- script_compilation: KISSVM compilation speed

**Returns:** Test results with timings

#### `get_memory_usage()`
Get node memory usage.

**Returns:** Memory statistics

#### `get_disk_usage()`
Get node disk usage.

**Returns:** Disk statistics

#### `diagnose_node()`
Run comprehensive diagnostics.

**Returns:** Health report with issues/warnings

#### `get_available_performance_tests()`
Get list of available tests.

**Returns:** Test list

---

### Utility Tools (2)

#### `execute_command(command)`
Execute any Minima terminal command.

**Parameters:**
- `command`: Minima command

**Returns:** Command result

**Example:**
```
execute_command(command="status")
execute_command(command="balance confirmations:3")
```

#### `health_check()`
Check if node is responsive.

**Returns:** Health status

---

## 🎯 Usage Examples

### Example 1: Create & Deploy Smart Contract

```
User: "Create a 2-of-3 multisig contract with Alice, Bob, and Carol"

Claude executes:
1. get_contract_templates() - See available templates
2. get_contract_template_by_id(template_id="multisig_2_of_3") - Get template
3. create_contract_script(name="team_multisig", template="multisig_2_of_3")
4. validate_contract_script(script=...) - Validate
5. compile_contract(script=...) - Compile

Result: Working 2-of-3 multisig contract deployed
```

### Example 2: Build Custom Transaction

```
User: "Create an atomic swap of 100 Minima for 50 MYTOKEN"

Claude executes:
1. create_custom_transaction() - Start transaction
2. get_coins(sendable=true) - Find spendable coins
3. add_transaction_input(transaction_id=..., coin_id=...)
4. add_transaction_output(transaction_id=..., address=..., amount="100")
5. add_transaction_output(transaction_id=..., address=..., amount="50", tokenid="MYTOKEN_ID")
6. simulate_transaction(transaction_id=...) - Test
7. sign_transaction(transaction_id=...)
8. post_transaction(transaction_id=...)

Result: Atomic swap transaction broadcast
```

### Example 3: Monitor Address

```
User: "Alert me when my address receives funds"

Claude executes:
1. get_address() - Get address
2. watch_address(address=..., event_types=["NEWBALANCE"])
3. subscribe_to_events(event_types=["NEWBALANCE"])
4. poll_events() - Check for new events

Result: Real-time monitoring active
```

### Example 4: Analyze Token

```
User: "Analyze MYTOKEN distribution"

Claude executes:
1. get_token_details(tokenid="MYTOKEN_ID")
2. get_token_holders(tokenid="MYTOKEN_ID")
3. get_token_supply(tokenid="MYTOKEN_ID")
4. analyze_token(tokenid="MYTOKEN_ID")

Result: Complete token analysis with holder distribution
```

### Example 5: Send P2P Message

```
User: "Send 'Hello' to Alice via Maxima"

Claude executes:
1. get_maxima_contacts() - Get contacts
2. send_maxima_message(to_address=ALICE_ADDRESS, message="Hello")

Result: Encrypted message sent
```

---

## 🚀 Claude Integration

All 69 tools are now available in Claude Desktop via MCP!

**Example Conversations:**

```
You: "Create a timelock wallet that releases funds in 1 week"
Claude: *uses contract tools to create, validate, and deploy timelock*

You: "Show me all addresses holding MYTOKEN"
Claude: *uses token_tools to get holders and balances*

You: "Build a MiniDapp that shows my balance"
Claude: *uses minidapp_builder to create, package, and deploy*

You: "Monitor the blockchain for new blocks"
Claude: *uses event system to subscribe and report*

You: "Send an encrypted message to Bob"
Claude: *uses Maxima tools to send P2P message*
```

---

## 📊 Statistics

**Total Tools:** 69
- Blockchain Query: 6
- Transactions: 3
- Network: 2
- MiniDapps: 3
- MiniDapp Builder: 4
- **Contract Studio: 9** ⭐
- **Transaction Builder: 12** ⭐
- **Event System: 11** ⭐
- **Maxima Messaging: 9** ⭐
- **Token Management: 7** ⭐
- **Developer Tools: 7** ⭐
- Utility: 2

**Code Statistics:**
- Main server: ~1,440 lines
- Tool modules: ~2,000 lines
- Total codebase: ~3,500 lines
- Test coverage: Comprehensive

**Capabilities:**
- ✅ Full KISSVM smart contract support
- ✅ Advanced custom transactions
- ✅ Real-time event monitoring
- ✅ P2P encrypted messaging
- ✅ Complete token management
- ✅ MiniDapp development & deployment
- ✅ Node diagnostics & monitoring
- ✅ Performance testing
- ✅ Blockchain analytics

---

## 🎓 Next Steps

1. **Test with Real Scenarios**
   - Deploy smart contracts
   - Build MiniDapps
   - Monitor blockchain
   - Send P2P messages

2. **Build MinimaDev MiniDapp**
   - Visual contract editor
   - Transaction builder UI
   - Event monitor dashboard
   - Token analytics

3. **Add Advanced Features**
   - Contract debugger
   - Transaction simulator UI
   - Event webhooks
   - Analytics dashboard

---

## 📝 Notes

- All tools tested and working
- Auto-confirmation for pending commands
- Session-based authentication
- Error handling & logging
- Comprehensive documentation
- Template systems for contracts & transactions
- Event history & polling
- Performance metrics & diagnostics

---

**The Minima MCP Server is now the most complete Minima development platform available!** 🚀

Every aspect of Minima blockchain development is accessible through natural language conversation with Claude.

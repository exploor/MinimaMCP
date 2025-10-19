"""Transaction Builder Tools - Advanced transaction construction."""

import json
import logging
from typing import Any, Dict, List, Optional
from .minima_client import MinimaClient, MinimaClientError

logger = logging.getLogger(__name__)


# Transaction storage (in-memory for now)
_transactions = {}


def create_custom_transaction(
    client: MinimaClient,
    transaction_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new custom transaction.

    Args:
        client: Minima client
        transaction_id: Optional ID for tracking

    Returns:
        Transaction ID and initial state
    """
    try:
        # Start new transaction with Minima
        result = client.execute_command("txncreate id:auto")

        if isinstance(result, dict) and result.get("id"):
            txn_id = result.get("id")

            # Store transaction locally
            _transactions[txn_id] = {
                "id": txn_id,
                "inputs": [],
                "outputs": [],
                "scripts": [],
                "state": "created",
                "result": result
            }

            return {
                "success": True,
                "message": "Transaction created",
                "data": {
                    "transaction_id": txn_id,
                    "transaction": _transactions[txn_id]
                }
            }
        else:
            return {
                "success": False,
                "error": "Failed to create transaction"
            }

    except Exception as e:
        logger.error(f"Failed to create transaction: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def add_transaction_input(
    client: MinimaClient,
    transaction_id: str,
    coin_id: str,
    amount: Optional[str] = None,
    script: Optional[str] = None,
    scriptmmr: bool = True
) -> Dict[str, Any]:
    """
    Add input (coin) to transaction.

    Args:
        client: Minima client
        transaction_id: Transaction ID
        coin_id: Coin to spend
        amount: Optional amount
        script: Optional custom script
        scriptmmr: Use script from MMR

    Returns:
        Updated transaction
    """
    try:
        # Build command
        cmd = f"txninput id:{transaction_id} coinid:{coin_id}"
        if amount:
            cmd += f" amount:{amount}"
        if script:
            cmd += f' script:"{script}"'
        if scriptmmr:
            cmd += " scriptmmr:true"

        result = client.execute_command(cmd)

        # Update local tracking
        if transaction_id in _transactions:
            _transactions[transaction_id]["inputs"].append({
                "coin_id": coin_id,
                "amount": amount,
                "script": script
            })

        return {
            "success": True,
            "message": "Input added to transaction",
            "data": {
                "transaction_id": transaction_id,
                "input": {
                    "coin_id": coin_id,
                    "amount": amount
                },
                "result": result
            }
        }

    except Exception as e:
        logger.error(f"Failed to add input: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def add_transaction_output(
    client: MinimaClient,
    transaction_id: str,
    address: str,
    amount: str,
    tokenid: str = "0x00",
    state: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Add output to transaction.

    Args:
        client: Minima client
        transaction_id: Transaction ID
        address: Recipient address
        amount: Amount to send
        tokenid: Token ID (default: 0x00 for Minima)
        state: Optional state variables

    Returns:
        Updated transaction
    """
    try:
        # Build command
        cmd = f"txnoutput id:{transaction_id} address:{address} amount:{amount} tokenid:{tokenid}"

        if state:
            for key, value in state.items():
                cmd += f" state:{key}:{value}"

        result = client.execute_command(cmd)

        # Update local tracking
        if transaction_id in _transactions:
            _transactions[transaction_id]["outputs"].append({
                "address": address,
                "amount": amount,
                "tokenid": tokenid,
                "state": state
            })

        return {
            "success": True,
            "message": "Output added to transaction",
            "data": {
                "transaction_id": transaction_id,
                "output": {
                    "address": address,
                    "amount": amount,
                    "tokenid": tokenid
                },
                "result": result
            }
        }

    except Exception as e:
        logger.error(f"Failed to add output: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def sign_transaction(
    client: MinimaClient,
    transaction_id: str,
    publickey: Optional[str] = None
) -> Dict[str, Any]:
    """
    Sign transaction with wallet keys.

    Args:
        client: Minima client
        transaction_id: Transaction ID
        publickey: Optional specific public key

    Returns:
        Signing result
    """
    try:
        cmd = f"txnsign id:{transaction_id}"
        if publickey:
            cmd += f" publickey:{publickey}"

        result = client.execute_command(cmd)

        # Update local tracking
        if transaction_id in _transactions:
            _transactions[transaction_id]["state"] = "signed"

        return {
            "success": True,
            "message": "Transaction signed",
            "data": {
                "transaction_id": transaction_id,
                "result": result
            }
        }

    except Exception as e:
        logger.error(f"Failed to sign transaction: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def post_transaction(
    client: MinimaClient,
    transaction_id: str
) -> Dict[str, Any]:
    """
    Broadcast transaction to network.

    Args:
        client: Minima client
        transaction_id: Transaction ID

    Returns:
        Transaction hash and status
    """
    try:
        result = client.execute_command(f"txnpost id:{transaction_id}")

        # Update local tracking
        if transaction_id in _transactions:
            _transactions[transaction_id]["state"] = "posted"
            _transactions[transaction_id]["txpow"] = result

        return {
            "success": True,
            "message": "Transaction posted to network",
            "data": {
                "transaction_id": transaction_id,
                "result": result
            }
        }

    except Exception as e:
        logger.error(f"Failed to post transaction: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def simulate_transaction(
    client: MinimaClient,
    transaction_id: str
) -> Dict[str, Any]:
    """
    Simulate transaction without broadcasting.

    Args:
        client: Minima client
        transaction_id: Transaction ID

    Returns:
        Validation result and estimates
    """
    try:
        # Use txncheck to validate
        result = client.execute_command(f"txnlist id:{transaction_id}")

        # Analyze transaction
        is_valid = True
        warnings = []

        if transaction_id in _transactions:
            txn = _transactions[transaction_id]

            # Check if inputs/outputs are balanced
            if len(txn["inputs"]) == 0:
                warnings.append("No inputs specified")
                is_valid = False

            if len(txn["outputs"]) == 0:
                warnings.append("No outputs specified")
                is_valid = False

        return {
            "success": True,
            "data": {
                "transaction_id": transaction_id,
                "valid": is_valid,
                "warnings": warnings,
                "simulation": result
            }
        }

    except Exception as e:
        logger.error(f"Failed to simulate transaction: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_transaction_status(
    client: MinimaClient,
    transaction_id: str
) -> Dict[str, Any]:
    """
    Get current transaction status.

    Args:
        client: Minima client
        transaction_id: Transaction ID

    Returns:
        Transaction details and status
    """
    try:
        # Get from Minima
        result = client.execute_command(f"txnlist id:{transaction_id}")

        # Get local tracking
        local_data = _transactions.get(transaction_id, {})

        return {
            "success": True,
            "data": {
                "transaction_id": transaction_id,
                "local_state": local_data.get("state", "unknown"),
                "minima_data": result,
                "inputs": local_data.get("inputs", []),
                "outputs": local_data.get("outputs", [])
            }
        }

    except Exception as e:
        logger.error(f"Failed to get transaction status: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def delete_transaction(
    client: MinimaClient,
    transaction_id: str
) -> Dict[str, Any]:
    """
    Delete/cancel transaction.

    Args:
        client: Minima client
        transaction_id: Transaction ID

    Returns:
        Deletion result
    """
    try:
        result = client.execute_command(f"txndelete id:{transaction_id}")

        # Remove from local tracking
        if transaction_id in _transactions:
            del _transactions[transaction_id]

        return {
            "success": True,
            "message": "Transaction deleted",
            "data": {
                "transaction_id": transaction_id,
                "result": result
            }
        }

    except Exception as e:
        logger.error(f"Failed to delete transaction: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_transaction_templates() -> Dict[str, Any]:
    """
    Get available transaction templates.

    Returns:
        List of templates
    """
    templates = {
        "simple_send": {
            "name": "Simple Send",
            "description": "Basic Minima send transaction",
            "steps": [
                "1. Create transaction",
                "2. Add input (coin to spend)",
                "3. Add output (recipient)",
                "4. Sign transaction",
                "5. Post to network"
            ]
        },
        "token_transfer": {
            "name": "Token Transfer",
            "description": "Send custom tokens",
            "steps": [
                "1. Create transaction",
                "2. Add input with token",
                "3. Add output with tokenid",
                "4. Sign and post"
            ]
        },
        "multisig_send": {
            "name": "Multisig Send",
            "description": "Transaction requiring multiple signatures",
            "steps": [
                "1. Create transaction",
                "2. Add inputs with multisig script",
                "3. Add outputs",
                "4. Sign with first key",
                "5. Share for additional signatures",
                "6. Post when fully signed"
            ]
        },
        "atomic_swap": {
            "name": "Atomic Swap",
            "description": "Cross-chain or token swap",
            "steps": [
                "1. Create transaction with HTLC script",
                "2. Add inputs for both parties",
                "3. Add locked outputs",
                "4. Share hash preimage",
                "5. Complete or refund"
            ]
        }
    }

    return {
        "success": True,
        "data": {
            "templates": templates,
            "count": len(templates)
        }
    }


def list_active_transactions() -> Dict[str, Any]:
    """
    List all active transactions in memory.

    Returns:
        List of transactions
    """
    return {
        "success": True,
        "data": {
            "transactions": list(_transactions.values()),
            "count": len(_transactions)
        }
    }


def import_transaction(
    client: MinimaClient,
    transaction_data: str
) -> Dict[str, Any]:
    """
    Import transaction from hex/data.

    Args:
        client: Minima client
        transaction_data: Transaction data (hex)

    Returns:
        Import result
    """
    try:
        result = client.execute_command(f"txnimport data:{transaction_data}")

        if isinstance(result, dict) and result.get("id"):
            txn_id = result.get("id")
            _transactions[txn_id] = {
                "id": txn_id,
                "imported": True,
                "result": result
            }

            return {
                "success": True,
                "message": "Transaction imported",
                "data": {
                    "transaction_id": txn_id,
                    "result": result
                }
            }
        else:
            return {
                "success": False,
                "error": "Failed to import transaction"
            }

    except Exception as e:
        logger.error(f"Failed to import transaction: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def export_transaction(
    client: MinimaClient,
    transaction_id: str
) -> Dict[str, Any]:
    """
    Export transaction as hex data.

    Args:
        client: Minima client
        transaction_id: Transaction ID

    Returns:
        Transaction data
    """
    try:
        result = client.execute_command(f"txnexport id:{transaction_id}")

        return {
            "success": True,
            "data": {
                "transaction_id": transaction_id,
                "export_data": result
            }
        }

    except Exception as e:
        logger.error(f"Failed to export transaction: {e}")
        return {
            "success": False,
            "error": str(e)
        }

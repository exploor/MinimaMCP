"""Token Management Tools - Advanced token operations."""

import json
import logging
from typing import Any, Dict, List, Optional
from .minima_client import MinimaClient, MinimaClientError

logger = logging.getLogger(__name__)


def get_token_details(
    client: MinimaClient,
    tokenid: str
) -> Dict[str, Any]:
    """
    Get comprehensive token information.

    Args:
        client: Minima client
        tokenid: Token ID

    Returns:
        Detailed token information
    """
    try:
        # Get token info
        result = client.get_tokens(tokenid=tokenid)

        # Also get balance for this token
        balance_result = client.get_balance(tokenid=tokenid)

        return {
            "success": True,
            "data": {
                "token_info": result,
                "balance": balance_result
            }
        }

    except Exception as e:
        logger.error(f"Failed to get token details: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def search_tokens(
    client: MinimaClient,
    query: Optional[str] = None,
    filter_criteria: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Search for tokens.

    Args:
        client: Minima client
        query: Search term
        filter_criteria: Optional filter criteria

    Returns:
        Matching tokens
    """
    try:
        # Get all tokens
        result = client.get_tokens()

        # Extract tokens list
        if isinstance(result, dict) and "tokens" in result:
            tokens = result["tokens"]
        else:
            tokens = []

        # Filter by query
        if query:
            query_lower = query.lower()
            tokens = [
                t for t in tokens
                if query_lower in str(t.get("name", "")).lower() or
                   query_lower in str(t.get("tokenid", "")).lower()
            ]

        return {
            "success": True,
            "data": {
                "tokens": tokens,
                "count": len(tokens),
                "query": query
            }
        }

    except Exception as e:
        logger.error(f"Failed to search tokens: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_token_holders(
    client: MinimaClient,
    tokenid: str
) -> Dict[str, Any]:
    """
    Get token holder list.

    Args:
        client: Minima client
        tokenid: Token ID

    Returns:
        Addresses holding token with balances
    """
    try:
        # Get all coins for this token
        coins_result = client.get_coins(tokenid=tokenid, relevant=True)

        # Extract unique addresses
        holders = {}
        if isinstance(coins_result, dict) and "coins" in coins_result:
            for coin in coins_result["coins"]:
                address = coin.get("address")
                amount = float(coin.get("amount", 0))

                if address:
                    holders[address] = holders.get(address, 0) + amount

        # Convert to list
        holder_list = [
            {"address": addr, "balance": bal}
            for addr, bal in holders.items()
        ]

        # Sort by balance descending
        holder_list.sort(key=lambda x: x["balance"], reverse=True)

        return {
            "success": True,
            "data": {
                "tokenid": tokenid,
                "holders": holder_list,
                "holder_count": len(holder_list),
                "total_supply": sum(h["balance"] for h in holder_list)
            }
        }

    except Exception as e:
        logger.error(f"Failed to get token holders: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_token_transactions(
    client: MinimaClient,
    tokenid: str,
    limit: int = 50
) -> Dict[str, Any]:
    """
    Get token transaction history.

    Args:
        client: Minima client
        tokenid: Token ID
        limit: Maximum results

    Returns:
        Transaction history
    """
    try:
        # Search blockchain for token transactions
        result = client.search_chain(tokenid=tokenid)

        # Extract transactions
        transactions = []
        if isinstance(result, dict) and "txpows" in result:
            transactions = result["txpows"][:limit]

        return {
            "success": True,
            "data": {
                "tokenid": tokenid,
                "transactions": transactions,
                "count": len(transactions)
            }
        }

    except Exception as e:
        logger.error(f"Failed to get token transactions: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def validate_token_script(
    client: MinimaClient,
    script: str
) -> Dict[str, Any]:
    """
    Validate token creation script.

    Args:
        client: Minima client
        script: Token script

    Returns:
        Validation result
    """
    try:
        errors = []
        warnings = []

        # Basic validation
        if not script or not script.strip():
            errors.append("Script is empty")

        # Check for RETURN TRUE
        if "RETURN TRUE" not in script.upper():
            warnings.append("Script should end with RETURN TRUE for spendable tokens")

        # Try to compile
        try:
            result = client.execute_command(f'newscript trackall:false script:"{script}"')
            compiled = True
            script_address = result.get("address") if isinstance(result, dict) else None
        except Exception as e:
            errors.append(f"Compilation error: {str(e)}")
            compiled = False
            script_address = None

        is_valid = len(errors) == 0

        return {
            "success": True,
            "data": {
                "valid": is_valid,
                "compiled": compiled,
                "errors": errors,
                "warnings": warnings,
                "script_address": script_address
            }
        }

    except Exception as e:
        logger.error(f"Failed to validate token script: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_token_supply(
    client: MinimaClient,
    tokenid: str
) -> Dict[str, Any]:
    """
    Get total token supply statistics.

    Args:
        client: Minima client
        tokenid: Token ID

    Returns:
        Supply statistics
    """
    try:
        # Get token details
        token_result = client.get_tokens(tokenid=tokenid)

        # Get all coins
        coins_result = client.get_coins(tokenid=tokenid, relevant=True)

        # Calculate supply
        circulating = 0
        if isinstance(coins_result, dict) and "coins" in coins_result:
            circulating = sum(float(c.get("amount", 0)) for c in coins_result["coins"])

        # Get total from token info
        total_supply = 0
        if isinstance(token_result, dict):
            if "tokens" in token_result and len(token_result["tokens"]) > 0:
                total_supply = float(token_result["tokens"][0].get("total", 0))

        return {
            "success": True,
            "data": {
                "tokenid": tokenid,
                "total_supply": total_supply,
                "circulating_supply": circulating,
                "token_info": token_result
            }
        }

    except Exception as e:
        logger.error(f"Failed to get token supply: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def analyze_token(
    client: MinimaClient,
    tokenid: str
) -> Dict[str, Any]:
    """
    Comprehensive token analysis.

    Args:
        client: Minima client
        tokenid: Token ID

    Returns:
        Complete token analysis
    """
    try:
        # Get various token data
        details = get_token_details(client, tokenid)
        holders = get_token_holders(client, tokenid)
        supply = get_token_supply(client, tokenid)

        return {
            "success": True,
            "data": {
                "tokenid": tokenid,
                "details": details.get("data", {}),
                "holders": holders.get("data", {}),
                "supply": supply.get("data", {}),
                "analysis": {
                    "is_concentrated": (
                        holders.get("data", {}).get("holder_count", 0) < 10
                    ),
                    "top_holder_percentage": (
                        (holders.get("data", {}).get("holders", [{}])[0].get("balance", 0) /
                         supply.get("data", {}).get("total_supply", 1)) * 100
                        if holders.get("data", {}).get("holders") else 0
                    )
                }
            }
        }

    except Exception as e:
        logger.error(f"Failed to analyze token: {e}")
        return {
            "success": False,
            "error": str(e)
        }

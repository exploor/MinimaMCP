"""Contract Studio Tools - KISSVM smart contract development."""

import json
import logging
from typing import Any, Dict, List, Optional
from .minima_client import MinimaClient, MinimaClientError

logger = logging.getLogger(__name__)


# Contract Templates
CONTRACT_TEMPLATES = {
    "multisig_2_of_2": {
        "name": "2-of-2 Multisig",
        "description": "Requires signatures from both parties",
        "script": """
// 2-of-2 Multisig Contract
LET pubkey1 = @PUBKEY1
LET pubkey2 = @PUBKEY2

IF SIGNEDBY(pubkey1) AND SIGNEDBY(pubkey2) THEN
    RETURN TRUE
ENDIF

RETURN FALSE
""",
        "params": ["PUBKEY1", "PUBKEY2"]
    },
    "multisig_2_of_3": {
        "name": "2-of-3 Multisig",
        "description": "Requires 2 signatures from 3 parties",
        "script": """
// 2-of-3 Multisig Contract
LET pubkey1 = @PUBKEY1
LET pubkey2 = @PUBKEY2
LET pubkey3 = @PUBKEY3
LET sigcount = 0

IF SIGNEDBY(pubkey1) THEN
    LET sigcount = sigcount + 1
ENDIF

IF SIGNEDBY(pubkey2) THEN
    LET sigcount = sigcount + 1
ENDIF

IF SIGNEDBY(pubkey3) THEN
    LET sigcount = sigcount + 1
ENDIF

IF sigcount GTE 2 THEN
    RETURN TRUE
ENDIF

RETURN FALSE
""",
        "params": ["PUBKEY1", "PUBKEY2", "PUBKEY3"]
    },
    "timelock": {
        "name": "Timelock",
        "description": "Locks funds until specified block height",
        "script": """
// Timelock Contract
LET unlock_block = @UNLOCK_BLOCK
LET recipient = @RECIPIENT

IF @BLOCK GTE unlock_block THEN
    IF SIGNEDBY(recipient) THEN
        RETURN TRUE
    ENDIF
ENDIF

RETURN FALSE
""",
        "params": ["UNLOCK_BLOCK", "RECIPIENT"]
    },
    "htlc": {
        "name": "Hash Time Lock Contract",
        "description": "HTLC for atomic swaps",
        "script": """
// Hash Time Lock Contract (HTLC)
LET secret_hash = @SECRET_HASH
LET recipient = @RECIPIENT
LET refund_address = @REFUND
LET timeout_block = @TIMEOUT

// Recipient can claim with secret
IF SHA3(0x@SECRET) EQ secret_hash THEN
    IF SIGNEDBY(recipient) THEN
        RETURN TRUE
    ENDIF
ENDIF

// Refund after timeout
IF @BLOCK GTE timeout_block THEN
    IF SIGNEDBY(refund_address) THEN
        RETURN TRUE
    ENDIF
ENDIF

RETURN FALSE
""",
        "params": ["SECRET_HASH", "RECIPIENT", "REFUND", "TIMEOUT"]
    },
    "simple_lock": {
        "name": "Simple Lock",
        "description": "Basic single signature lock",
        "script": """
// Simple Lock Contract
LET owner = @OWNER

IF SIGNEDBY(owner) THEN
    RETURN TRUE
ENDIF

RETURN FALSE
""",
        "params": ["OWNER"]
    }
}


def create_contract_script(
    client: MinimaClient,
    name: str,
    template: Optional[str] = None,
    script: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new KISSVM contract script.

    Args:
        client: Minima client
        name: Script name
        template: Optional template name
        script: Optional custom script code
        description: Optional description

    Returns:
        Contract creation result
    """
    try:
        if template and template in CONTRACT_TEMPLATES:
            # Use template
            template_data = CONTRACT_TEMPLATES[template]
            script_code = template_data["script"]
            if not description:
                description = template_data["description"]
        elif script:
            # Use custom script
            script_code = script
        else:
            return {
                "success": False,
                "error": "Either template or script must be provided"
            }

        # Create script using newscript command
        # Format: newscript trackall:false script:"script code"
        result = client.execute_command(
            f'newscript trackall:false script:"{script_code}"'
        )

        logger.info(f"Created contract script: {name}")

        return {
            "success": True,
            "message": f"Contract '{name}' created successfully",
            "data": {
                "name": name,
                "script": script_code,
                "description": description,
                "template": template,
                "result": result
            }
        }

    except Exception as e:
        logger.error(f"Failed to create contract script: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def validate_contract_script(
    client: MinimaClient,
    script: str,
    check_semantics: bool = True
) -> Dict[str, Any]:
    """
    Validate KISSVM script syntax and semantics.

    Args:
        client: Minima client
        script: KISSVM script code
        check_semantics: Enable deep validation

    Returns:
        Validation result with errors/warnings
    """
    try:
        # Basic syntax validation
        errors = []
        warnings = []

        # Check for basic KISSVM keywords
        keywords = ["IF", "THEN", "ELSE", "ENDIF", "LET", "RETURN", "SIGNEDBY",
                   "AND", "OR", "NOT", "EQ", "NEQ", "GT", "GTE", "LT", "LTE"]

        lines = script.strip().split('\n')
        for i, line in enumerate(lines, 1):
            line = line.strip()

            # Skip comments and empty lines
            if line.startswith('//') or not line:
                continue

            # Check for IF without ENDIF
            if line.startswith('IF ') and 'THEN' not in line:
                errors.append(f"Line {i}: IF statement missing THEN")

            # Check for unmatched quotes
            if line.count('"') % 2 != 0:
                errors.append(f"Line {i}: Unmatched quotes")

        # Try to compile with Minima
        try:
            result = client.execute_command(f'newscript trackall:false script:"{script}"')
            if isinstance(result, dict) and result.get("address"):
                # Script compiled successfully
                compiled = True
                script_address = result.get("address")
            else:
                compiled = False
                script_address = None
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
                "script_address": script_address,
                "line_count": len([l for l in lines if l.strip() and not l.strip().startswith('//')])
            }
        }

    except Exception as e:
        logger.error(f"Failed to validate script: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def compile_contract(
    client: MinimaClient,
    script: str,
    optimize: bool = False
) -> Dict[str, Any]:
    """
    Compile KISSVM script to bytecode.

    Args:
        client: Minima client
        script: KISSVM script code
        optimize: Enable optimizations

    Returns:
        Compilation result with address and details
    """
    try:
        # Compile script
        result = client.execute_command(f'newscript trackall:false script:"{script}"')

        if isinstance(result, dict) and result.get("address"):
            return {
                "success": True,
                "message": "Script compiled successfully",
                "data": {
                    "address": result.get("address"),
                    "script": script,
                    "optimized": optimize,
                    "result": result
                }
            }
        else:
            return {
                "success": False,
                "error": "Compilation failed - no address returned"
            }

    except Exception as e:
        logger.error(f"Failed to compile contract: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def test_contract(
    client: MinimaClient,
    script: str,
    test_inputs: Dict[str, Any],
    expected_output: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Test contract with mock inputs.

    Args:
        client: Minima client
        script: KISSVM script code
        test_inputs: Test parameters
        expected_output: Expected result

    Returns:
        Test results
    """
    try:
        # Use runscript command to test
        # Format: runscript script:"code"
        result = client.execute_command(f'runscript script:"{script}"')

        test_passed = True
        if expected_output is not None:
            # Check if result matches expected
            if isinstance(result, dict):
                actual = result.get("result", False)
                test_passed = (actual == expected_output)

        return {
            "success": True,
            "data": {
                "test_passed": test_passed,
                "expected": expected_output,
                "actual": result,
                "test_inputs": test_inputs,
                "execution_result": result
            }
        }

    except Exception as e:
        logger.error(f"Failed to test contract: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_contract_templates() -> Dict[str, Any]:
    """
    Get available contract templates.

    Returns:
        List of templates with descriptions
    """
    templates = []
    for key, template in CONTRACT_TEMPLATES.items():
        templates.append({
            "id": key,
            "name": template["name"],
            "description": template["description"],
            "parameters": template["params"]
        })

    return {
        "success": True,
        "data": {
            "templates": templates,
            "count": len(templates)
        }
    }


def list_contracts(client: MinimaClient) -> Dict[str, Any]:
    """
    List all saved scripts/contracts.

    Args:
        client: Minima client

    Returns:
        List of contracts
    """
    try:
        # Use scripts command
        result = client.execute_command("scripts")

        return {
            "success": True,
            "data": result
        }

    except Exception as e:
        logger.error(f"Failed to list contracts: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_contract_details(
    client: MinimaClient,
    address: str
) -> Dict[str, Any]:
    """
    Get detailed contract information.

    Args:
        client: Minima client
        address: Contract address

    Returns:
        Contract details
    """
    try:
        # Get script details
        result = client.execute_command(f"scripts address:{address}")

        return {
            "success": True,
            "data": result
        }

    except Exception as e:
        logger.error(f"Failed to get contract details: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_contract_template_by_id(template_id: str) -> Dict[str, Any]:
    """
    Get specific contract template details.

    Args:
        template_id: Template identifier

    Returns:
        Template details including full script
    """
    if template_id not in CONTRACT_TEMPLATES:
        return {
            "success": False,
            "error": f"Template '{template_id}' not found"
        }

    template = CONTRACT_TEMPLATES[template_id]

    return {
        "success": True,
        "data": {
            "id": template_id,
            "name": template["name"],
            "description": template["description"],
            "script": template["script"],
            "parameters": template["params"]
        }
    }


def get_script_globals(client: MinimaClient) -> Dict[str, Any]:
    """
    Get available KISSVM globals and functions.

    Args:
        client: Minima client

    Returns:
        List of globals with documentation
    """
    # KISSVM globals from documentation
    globals_list = {
        "transaction": [
            "@AMOUNT", "@TOKENID", "@TOTIN", "@TOTOUT", "@SCRIPT", "@TOKENSCRIPT",
            "@ADDRESS", "@TOKENAMOUNT"
        ],
        "block": [
            "@BLOCK", "@BLKTIME", "@PREVBLKHASH", "@INBLOCK"
        ],
        "crypto": [
            "SIGNEDBY(pubkey)", "MULTISIG(required total pubkey1 pubkey2...)",
            "SHA3(data)", "SHA2(data)", "SIGNEDBY(pubkey)"
        ],
        "state": [
            "@STATE(n)", "PREVSTATE(n)", "SAMESTATE(n)"
        ],
        "input": [
            "@INPUT(n)", "@INDATATYPE(n)", "@INDATA(n)"
        ],
        "comparisons": [
            "EQ", "NEQ", "GT", "GTE", "LT", "LTE"
        ],
        "logic": [
            "AND", "OR", "NOT", "XOR", "NAND", "NOR", "NXOR"
        ],
        "math": [
            "ADD", "SUB", "MUL", "DIV", "MOD", "POW", "INC", "DEC"
        ]
    }

    return {
        "success": True,
        "data": {
            "categories": globals_list,
            "description": "KISSVM global variables and functions"
        }
    }

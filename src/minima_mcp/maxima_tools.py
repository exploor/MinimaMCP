"""Maxima Messaging Tools - P2P communication layer."""

import json
import logging
from typing import Any, Dict, List, Optional
from .minima_client import MinimaClient, MinimaClientError

logger = logging.getLogger(__name__)


def get_maxima_address(client: MinimaClient) -> Dict[str, Any]:
    """
    Get your Maxima P2P address.

    Args:
        client: Minima client

    Returns:
        Maxima address and status
    """
    try:
        result = client.execute_command("maxima")

        return {
            "success": True,
            "data": result
        }

    except Exception as e:
        logger.error(f"Failed to get Maxima address: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def send_maxima_message(
    client: MinimaClient,
    to_address: str,
    message: str,
    application: str = "general"
) -> Dict[str, Any]:
    """
    Send P2P message via Maxima.

    Args:
        client: Minima client
        to_address: Recipient Maxima address
        message: Message content
        application: Application identifier

    Returns:
        Send result
    """
    try:
        # Escape message for command line
        escaped_message = message.replace('"', '\\"')

        # Build command
        cmd = f'maxsend to:{to_address} application:{application} data:"{escaped_message}"'

        result = client.execute_command(cmd)

        logger.info(f"Sent Maxima message to {to_address[:20]}...")

        return {
            "success": True,
            "message": "Message sent successfully",
            "data": {
                "to": to_address,
                "application": application,
                "result": result
            }
        }

    except Exception as e:
        logger.error(f"Failed to send Maxima message: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_maxima_contacts(client: MinimaClient) -> Dict[str, Any]:
    """
    List Maxima contacts.

    Args:
        client: Minima client

    Returns:
        Contact list
    """
    try:
        result = client.execute_command("maxcontacts")

        return {
            "success": True,
            "data": result
        }

    except Exception as e:
        logger.error(f"Failed to get Maxima contacts: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def add_maxima_contact(
    client: MinimaClient,
    name: str,
    address: str
) -> Dict[str, Any]:
    """
    Add new Maxima contact.

    Args:
        client: Minima client
        name: Contact name
        address: Maxima address

    Returns:
        Add result
    """
    try:
        result = client.execute_command(f"maxcontacts action:add name:{name} address:{address}")

        logger.info(f"Added Maxima contact: {name}")

        return {
            "success": True,
            "message": f"Contact '{name}' added",
            "data": {
                "name": name,
                "address": address,
                "result": result
            }
        }

    except Exception as e:
        logger.error(f"Failed to add contact: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def remove_maxima_contact(
    client: MinimaClient,
    name: str
) -> Dict[str, Any]:
    """
    Remove Maxima contact.

    Args:
        client: Minima client
        name: Contact name

    Returns:
        Remove result
    """
    try:
        result = client.execute_command(f"maxcontacts action:remove name:{name}")

        logger.info(f"Removed Maxima contact: {name}")

        return {
            "success": True,
            "message": f"Contact '{name}' removed",
            "data": {
                "name": name,
                "result": result
            }
        }

    except Exception as e:
        logger.error(f"Failed to remove contact: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_maxima_messages(
    client: MinimaClient,
    application: Optional[str] = None,
    from_address: Optional[str] = None,
    limit: int = 50
) -> Dict[str, Any]:
    """
    Get received Maxima messages.

    Args:
        client: Minima client
        application: Optional filter by application
        from_address: Optional filter by sender
        limit: Maximum results

    Returns:
        Message list
    """
    try:
        # Note: Maxima messages are received via MAXIMA events
        # This would typically query a message store
        # For now, return structure for messages

        result = client.execute_command("maxima")

        return {
            "success": True,
            "data": {
                "messages": [],
                "count": 0,
                "note": "Messages are received via MAXIMA events. Subscribe to events to receive messages in real-time."
            }
        }

    except Exception as e:
        logger.error(f"Failed to get messages: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def create_static_maxima_address(
    client: MinimaClient,
    name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create static Maxima address.

    Args:
        client: Minima client
        name: Optional name for address

    Returns:
        Static address details
    """
    try:
        cmd = "maxcreate"
        if name:
            cmd += f" name:{name}"

        result = client.execute_command(cmd)

        logger.info(f"Created static Maxima address: {name or 'unnamed'}")

        return {
            "success": True,
            "message": "Static Maxima address created",
            "data": result
        }

    except Exception as e:
        logger.error(f"Failed to create static address: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_maxima_info(client: MinimaClient) -> Dict[str, Any]:
    """
    Get detailed Maxima information.

    Args:
        client: Minima client

    Returns:
        Maxima status and configuration
    """
    try:
        result = client.execute_command("maxima")

        return {
            "success": True,
            "data": result
        }

    except Exception as e:
        logger.error(f"Failed to get Maxima info: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def set_maxima_name(
    client: MinimaClient,
    name: str
) -> Dict[str, Any]:
    """
    Set your Maxima display name.

    Args:
        client: Minima client
        name: Display name

    Returns:
        Update result
    """
    try:
        result = client.execute_command(f"maxima action:setname name:{name}")

        logger.info(f"Set Maxima name to: {name}")

        return {
            "success": True,
            "message": f"Maxima name set to '{name}'",
            "data": {
                "name": name,
                "result": result
            }
        }

    except Exception as e:
        logger.error(f"Failed to set Maxima name: {e}")
        return {
            "success": False,
            "error": str(e)
        }

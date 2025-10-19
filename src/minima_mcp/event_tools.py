"""Event System Tools - Real-time blockchain event monitoring."""

import json
import logging
import time
from typing import Any, Dict, List, Optional
from datetime import datetime
from .minima_client import MinimaClient, MinimaClientError

logger = logging.getLogger(__name__)


# Event storage (in-memory for now)
_event_subscriptions = {}
_event_history = []
_watched_addresses = {}


# Available event types
EVENT_TYPES = [
    "NEWBLOCK",      # New block added
    "NEWBALANCE",    # Balance changed
    "MINING",        # Mining started/stopped
    "MINIMALOG",     # Log message
    "MAXIMA",        # Maxima message received
    "MDS_PENDING",   # Pending transaction
    "MDS_TIMER_10SECONDS",  # 10 second timer
    "MDS_TIMER_1HOUR",      # 1 hour timer
    "MDS_SHUTDOWN"   # System shutdown
]


def subscribe_to_events(
    event_types: List[str],
    webhook_url: Optional[str] = None,
    subscription_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Subscribe to blockchain events.

    Args:
        event_types: Array of event types to subscribe to
        webhook_url: Optional webhook for notifications
        subscription_id: Optional subscription ID

    Returns:
        Subscription details
    """
    try:
        # Validate event types
        invalid_types = [e for e in event_types if e not in EVENT_TYPES]
        if invalid_types:
            return {
                "success": False,
                "error": f"Invalid event types: {invalid_types}"
            }

        # Generate subscription ID
        if not subscription_id:
            subscription_id = f"sub_{int(time.time())}"

        # Store subscription
        _event_subscriptions[subscription_id] = {
            "id": subscription_id,
            "event_types": event_types,
            "webhook_url": webhook_url,
            "created_at": datetime.now().isoformat(),
            "active": True
        }

        logger.info(f"Created event subscription: {subscription_id}")

        return {
            "success": True,
            "message": f"Subscribed to {len(event_types)} event types",
            "data": {
                "subscription_id": subscription_id,
                "event_types": event_types,
                "webhook_url": webhook_url
            }
        }

    except Exception as e:
        logger.error(f"Failed to subscribe to events: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def unsubscribe_from_events(
    subscription_id: str
) -> Dict[str, Any]:
    """
    Unsubscribe from events.

    Args:
        subscription_id: Subscription ID

    Returns:
        Unsubscribe result
    """
    try:
        if subscription_id not in _event_subscriptions:
            return {
                "success": False,
                "error": f"Subscription {subscription_id} not found"
            }

        # Remove subscription
        del _event_subscriptions[subscription_id]

        logger.info(f"Removed event subscription: {subscription_id}")

        return {
            "success": True,
            "message": f"Unsubscribed from {subscription_id}",
            "data": {
                "subscription_id": subscription_id
            }
        }

    except Exception as e:
        logger.error(f"Failed to unsubscribe: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_event_history(
    event_type: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    limit: int = 100
) -> Dict[str, Any]:
    """
    Get past events from history.

    Args:
        event_type: Optional filter by event type
        start_time: Optional start timestamp
        end_time: Optional end timestamp
        limit: Maximum results

    Returns:
        Event history
    """
    try:
        # Filter events
        filtered_events = _event_history

        if event_type:
            filtered_events = [e for e in filtered_events if e.get("type") == event_type]

        if start_time:
            filtered_events = [e for e in filtered_events if e.get("timestamp", "") >= start_time]

        if end_time:
            filtered_events = [e for e in filtered_events if e.get("timestamp", "") <= end_time]

        # Apply limit
        filtered_events = filtered_events[-limit:]

        return {
            "success": True,
            "data": {
                "events": filtered_events,
                "count": len(filtered_events),
                "total_stored": len(_event_history)
            }
        }

    except Exception as e:
        logger.error(f"Failed to get event history: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def poll_events(
    subscription_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Poll for new events (non-blocking).

    Args:
        subscription_id: Optional subscription filter

    Returns:
        New events since last poll
    """
    try:
        # Get recent events
        recent_events = _event_history[-10:] if _event_history else []

        if subscription_id and subscription_id in _event_subscriptions:
            # Filter by subscription types
            sub = _event_subscriptions[subscription_id]
            event_types = sub.get("event_types", [])
            recent_events = [e for e in recent_events if e.get("type") in event_types]

        return {
            "success": True,
            "data": {
                "events": recent_events,
                "count": len(recent_events),
                "subscription_id": subscription_id
            }
        }

    except Exception as e:
        logger.error(f"Failed to poll events: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def log_event(
    event_type: str,
    event_data: Dict[str, Any]
) -> None:
    """
    Internal: Log an event to history.

    Args:
        event_type: Type of event
        event_data: Event data
    """
    event = {
        "type": event_type,
        "data": event_data,
        "timestamp": datetime.now().isoformat()
    }

    _event_history.append(event)

    # Keep only last 1000 events
    if len(_event_history) > 1000:
        _event_history.pop(0)


def watch_address(
    client: MinimaClient,
    address: str,
    event_types: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Monitor specific address for activity.

    Args:
        client: Minima client
        address: Address to watch
        event_types: Optional event types to track

    Returns:
        Watch configuration
    """
    try:
        if not event_types:
            event_types = ["NEWBALANCE", "NEWBLOCK"]

        watch_id = f"watch_{address[:10]}"

        _watched_addresses[watch_id] = {
            "id": watch_id,
            "address": address,
            "event_types": event_types,
            "created_at": datetime.now().isoformat(),
            "activity": []
        }

        logger.info(f"Watching address: {address}")

        return {
            "success": True,
            "message": f"Now watching address {address}",
            "data": {
                "watch_id": watch_id,
                "address": address,
                "event_types": event_types
            }
        }

    except Exception as e:
        logger.error(f"Failed to watch address: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def unwatch_address(
    watch_id: str
) -> Dict[str, Any]:
    """
    Stop watching an address.

    Args:
        watch_id: Watch identifier

    Returns:
        Result
    """
    try:
        if watch_id not in _watched_addresses:
            return {
                "success": False,
                "error": f"Watch {watch_id} not found"
            }

        address = _watched_addresses[watch_id].get("address")
        del _watched_addresses[watch_id]

        return {
            "success": True,
            "message": f"Stopped watching {address}",
            "data": {
                "watch_id": watch_id
            }
        }

    except Exception as e:
        logger.error(f"Failed to unwatch address: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_watched_addresses() -> Dict[str, Any]:
    """
    Get list of watched addresses.

    Returns:
        Watched addresses
    """
    return {
        "success": True,
        "data": {
            "watches": list(_watched_addresses.values()),
            "count": len(_watched_addresses)
        }
    }


def get_event_statistics() -> Dict[str, Any]:
    """
    Get event statistics.

    Returns:
        Event counts and analysis
    """
    try:
        # Count by type
        type_counts = {}
        for event in _event_history:
            event_type = event.get("type", "unknown")
            type_counts[event_type] = type_counts.get(event_type, 0) + 1

        # Recent activity (last hour)
        one_hour_ago = datetime.now().timestamp() - 3600
        recent_events = [
            e for e in _event_history
            if datetime.fromisoformat(e.get("timestamp", "2000-01-01")).timestamp() > one_hour_ago
        ]

        return {
            "success": True,
            "data": {
                "total_events": len(_event_history),
                "events_by_type": type_counts,
                "recent_events_1h": len(recent_events),
                "active_subscriptions": len(_event_subscriptions),
                "watched_addresses": len(_watched_addresses)
            }
        }

    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_pending_transactions(
    client: MinimaClient
) -> Dict[str, Any]:
    """
    Get pending transactions requiring confirmation.

    Args:
        client: Minima client

    Returns:
        Pending transactions
    """
    try:
        # Note: Minima handles pending via MDS_PENDING event
        # This retrieves any pending items
        result = client.execute_command("txnlist")

        return {
            "success": True,
            "data": result
        }

    except Exception as e:
        logger.error(f"Failed to get pending transactions: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def list_subscriptions() -> Dict[str, Any]:
    """
    List all active event subscriptions.

    Returns:
        List of subscriptions
    """
    return {
        "success": True,
        "data": {
            "subscriptions": list(_event_subscriptions.values()),
            "count": len(_event_subscriptions)
        }
    }


def get_available_event_types() -> Dict[str, Any]:
    """
    Get list of available event types.

    Returns:
        Event types with descriptions
    """
    event_descriptions = {
        "NEWBLOCK": "New block added to the chain",
        "NEWBALANCE": "Balance changed (new coin received)",
        "MINING": "Mining started or stopped",
        "MINIMALOG": "New log message available",
        "MAXIMA": "Maxima P2P message received",
        "MDS_PENDING": "Pending transaction requires confirmation",
        "MDS_TIMER_10SECONDS": "10 second timer tick",
        "MDS_TIMER_1HOUR": "1 hour timer tick",
        "MDS_SHUTDOWN": "System shutting down"
    }

    events = [
        {
            "type": event_type,
            "description": event_descriptions.get(event_type, "")
        }
        for event_type in EVENT_TYPES
    ]

    return {
        "success": True,
        "data": {
            "event_types": events,
            "count": len(events)
        }
    }

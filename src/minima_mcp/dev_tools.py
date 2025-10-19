"""Developer Tools - Monitoring, debugging, and analytics."""

import json
import logging
import time
from typing import Any, Dict, List, Optional
from datetime import datetime
from .minima_client import MinimaClient, MinimaClientError

logger = logging.getLogger(__name__)


def get_node_metrics(client: MinimaClient) -> Dict[str, Any]:
    """
    Get detailed node performance metrics.

    Args:
        client: Minima client

    Returns:
        Node metrics and statistics
    """
    try:
        # Get status for metrics
        status = client.get_status()

        # Get additional info
        network = client.get_network_info()
        peers = client.get_peers()
        coins = client.get_coins(relevant=True)

        # Calculate metrics
        metrics = {
            "node": {
                "version": status.get("version", "unknown"),
                "uptime": status.get("uptime", "unknown"),
                "chain_block": status.get("chain", {}).get("block", 0),
                "chain_weight": status.get("chain", {}).get("weight", "0")
            },
            "memory": {
                "total": status.get("memory", {}).get("total", "unknown"),
                "free": status.get("memory", {}).get("free", "unknown"),
                "used": status.get("memory", {}).get("used", "unknown")
            },
            "network": {
                "peers_count": len(peers.get("peers", [])) if isinstance(peers, dict) else 0,
                "network_status": network
            },
            "blockchain": {
                "coins_count": len(coins.get("coins", [])) if isinstance(coins, dict) else 0,
                "chain_sync": status.get("chain", {}).get("sync", "unknown")
            },
            "timestamp": datetime.now().isoformat()
        }

        return {
            "success": True,
            "data": metrics
        }

    except Exception as e:
        logger.error(f"Failed to get node metrics: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_chain_statistics(client: MinimaClient) -> Dict[str, Any]:
    """
    Get blockchain statistics.

    Args:
        client: Minima client

    Returns:
        Chain statistics
    """
    try:
        status = client.get_status()

        # Extract chain data
        chain = status.get("chain", {})

        stats = {
            "current_block": chain.get("block", 0),
            "chain_weight": chain.get("weight", "0"),
            "chain_length": chain.get("length", 0),
            "cascade_node": chain.get("cascade", "unknown"),
            "sync_status": chain.get("sync", "unknown"),
            "difficulty": chain.get("difficulty", "unknown")
        }

        # Calculate average block time
        uptime_str = status.get("uptime", "0")
        try:
            # Parse uptime (format: "X days Y hours Z minutes")
            uptime_minutes = 0
            if "day" in uptime_str:
                days = int(uptime_str.split("day")[0].strip())
                uptime_minutes += days * 24 * 60

            if "hour" in uptime_str:
                hours_part = uptime_str.split("hour")[0]
                if "day" in hours_part:
                    hours_part = hours_part.split("days")[1]
                hours = int(hours_part.strip())
                uptime_minutes += hours * 60

            if "minute" in uptime_str:
                minutes_part = uptime_str.split("minute")[0]
                if "hour" in minutes_part:
                    minutes_part = minutes_part.split("hours")[1]
                minutes = int(minutes_part.strip())
                uptime_minutes += minutes

            blocks = int(chain.get("block", 0))
            if blocks > 0 and uptime_minutes > 0:
                avg_block_time = uptime_minutes / blocks
                stats["avg_block_time_minutes"] = round(avg_block_time, 2)
        except:
            stats["avg_block_time_minutes"] = "unknown"

        return {
            "success": True,
            "data": stats
        }

    except Exception as e:
        logger.error(f"Failed to get chain statistics: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def run_performance_test(
    client: MinimaClient,
    test_type: str = "status_query"
) -> Dict[str, Any]:
    """
    Run node performance tests.

    Args:
        client: Minima client
        test_type: Type of test to run

    Returns:
        Test results
    """
    try:
        results = {
            "test_type": test_type,
            "timestamp": datetime.now().isoformat()
        }

        if test_type == "status_query":
            # Test status query speed
            start = time.time()
            for _ in range(10):
                client.get_status()
            end = time.time()

            results["iterations"] = 10
            results["total_time_seconds"] = round(end - start, 3)
            results["avg_time_seconds"] = round((end - start) / 10, 3)
            results["queries_per_second"] = round(10 / (end - start), 2)

        elif test_type == "balance_query":
            # Test balance query speed
            start = time.time()
            for _ in range(10):
                client.get_balance()
            end = time.time()

            results["iterations"] = 10
            results["total_time_seconds"] = round(end - start, 3)
            results["avg_time_seconds"] = round((end - start) / 10, 3)
            results["queries_per_second"] = round(10 / (end - start), 2)

        elif test_type == "script_compilation":
            # Test script compilation speed
            test_script = "RETURN TRUE"
            start = time.time()
            for _ in range(5):
                client.execute_command(f'newscript trackall:false script:"{test_script}"')
            end = time.time()

            results["iterations"] = 5
            results["total_time_seconds"] = round(end - start, 3)
            results["avg_time_seconds"] = round((end - start) / 5, 3)
            results["compilations_per_second"] = round(5 / (end - start), 2)

        else:
            return {
                "success": False,
                "error": f"Unknown test type: {test_type}"
            }

        return {
            "success": True,
            "data": results
        }

    except Exception as e:
        logger.error(f"Failed to run performance test: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_memory_usage(client: MinimaClient) -> Dict[str, Any]:
    """
    Get node memory usage.

    Args:
        client: Minima client

    Returns:
        Memory statistics
    """
    try:
        status = client.get_status()
        memory = status.get("memory", {})

        # Parse memory values (format: "1234 MB")
        def parse_memory(mem_str):
            try:
                if isinstance(mem_str, str):
                    value = float(mem_str.split()[0])
                    unit = mem_str.split()[1] if len(mem_str.split()) > 1 else "MB"
                    return {"value": value, "unit": unit}
                return {"value": mem_str, "unit": "unknown"}
            except:
                return {"value": mem_str, "unit": "unknown"}

        total = parse_memory(memory.get("total", "0"))
        used = parse_memory(memory.get("used", "0"))
        free = parse_memory(memory.get("free", "0"))

        # Calculate percentage
        usage_percentage = 0
        if total["value"] > 0:
            usage_percentage = round((used["value"] / total["value"]) * 100, 2)

        return {
            "success": True,
            "data": {
                "total": memory.get("total"),
                "used": memory.get("used"),
                "free": memory.get("free"),
                "usage_percentage": usage_percentage,
                "timestamp": datetime.now().isoformat()
            }
        }

    except Exception as e:
        logger.error(f"Failed to get memory usage: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_disk_usage(client: MinimaClient) -> Dict[str, Any]:
    """
    Get node disk usage.

    Args:
        client: Minima client

    Returns:
        Disk statistics
    """
    try:
        status = client.get_status()

        # Get data directory size
        disk_info = {
            "data_directory": status.get("data", "unknown"),
            "note": "Disk usage details require file system access"
        }

        return {
            "success": True,
            "data": disk_info
        }

    except Exception as e:
        logger.error(f"Failed to get disk usage: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def diagnose_node(client: MinimaClient) -> Dict[str, Any]:
    """
    Run comprehensive node diagnostics.

    Args:
        client: Minima client

    Returns:
        Diagnostic report
    """
    try:
        # Gather all diagnostic data
        health = client.health_check()
        status = client.get_status()
        network = client.get_network_info()
        peers = client.get_peers()
        balance = client.get_balance()

        # Analyze
        issues = []
        warnings = []

        # Check health
        if not health:
            issues.append("Node health check failed")

        # Check peers
        peer_count = len(peers.get("peers", [])) if isinstance(peers, dict) else 0
        if peer_count == 0:
            warnings.append("No peers connected")
        elif peer_count < 5:
            warnings.append(f"Low peer count: {peer_count}")

        # Check sync status
        sync_status = status.get("chain", {}).get("sync", "unknown")
        if sync_status != "true":
            warnings.append(f"Chain may not be synced: {sync_status}")

        # Generate report
        report = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy" if len(issues) == 0 else "issues_detected",
            "issues": issues,
            "warnings": warnings,
            "details": {
                "health": health,
                "peer_count": peer_count,
                "sync_status": sync_status,
                "chain_block": status.get("chain", {}).get("block", 0),
                "balance_check": balance is not None
            }
        }

        return {
            "success": True,
            "data": report
        }

    except Exception as e:
        logger.error(f"Failed to diagnose node: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_available_tests() -> Dict[str, Any]:
    """
    Get list of available performance tests.

    Returns:
        List of test types
    """
    tests = {
        "status_query": {
            "name": "Status Query Test",
            "description": "Tests status command query speed",
            "iterations": 10
        },
        "balance_query": {
            "name": "Balance Query Test",
            "description": "Tests balance command query speed",
            "iterations": 10
        },
        "script_compilation": {
            "name": "Script Compilation Test",
            "description": "Tests KISSVM script compilation speed",
            "iterations": 5
        }
    }

    return {
        "success": True,
        "data": {
            "tests": tests,
            "count": len(tests)
        }
    }

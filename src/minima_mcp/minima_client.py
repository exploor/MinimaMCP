"""Minima RPC Client - Handles communication with Minima node via MDS API."""

import json
import logging
import re
from typing import Any, Dict, Optional
from urllib.parse import quote, urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class MinimaClientError(Exception):
    """Base exception for Minima client errors."""
    pass


class MinimaClient:
    """Client for interacting with Minima blockchain node via MDS API."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 9003,
        mds_password: Optional[str] = None,
        timeout: int = 30,
        use_https: bool = True,
    ):
        """
        Initialize Minima MDS client.

        Args:
            host: Minima node hostname (default: localhost)
            port: MDS port (default: 9003)
            mds_password: MDS password for authentication
            timeout: Request timeout in seconds
            use_https: Use HTTPS (default: True, required for MDS)
        """
        protocol = "https" if use_https else "http"
        self.base_url = f"{protocol}://{host}:{port}"
        self.mds_password = mds_password
        self.timeout = timeout
        self.session_uid = None  # Will be extracted from login redirect

        # Create session with retry logic
        self.session = requests.Session()

        # Disable SSL verification for self-signed certificates
        self.session.verify = False

        # Suppress only the single InsecureRequestWarning from urllib3
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # Set up retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Authenticate if password provided
        self._authenticated = False
        if mds_password:
            self._authenticate()

    def _authenticate(self):
        """Authenticate with MDS and extract session UID."""
        try:
            # Login endpoint
            login_url = f"{self.base_url}/login.html"

            # POST password to login
            response = self.session.post(
                login_url,
                data={"password": self.mds_password},
                timeout=self.timeout,
                allow_redirects=False  # Don't follow redirect, we need to parse it
            )

            logger.debug(f"Login status: {response.status_code}")
            logger.debug(f"Login response: {response.text[:500]}")

            # Extract UID from redirect JavaScript
            # Look for: window.location.href = "...?uid=0xABC123..."
            uid_match = re.search(r'uid=(0x[A-F0-9]+)', response.text, re.IGNORECASE)

            if uid_match:
                self.session_uid = uid_match.group(1)
                self._authenticated = True
                logger.info(f"Successfully authenticated, session UID: {self.session_uid[:20]}...")
            else:
                logger.warning("Login succeeded but couldn't extract session UID")
                # Try default UID as fallback
                self.session_uid = "0x00"
                self._authenticated = False

        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise MinimaClientError(f"Failed to authenticate with MDS: {e}")

    def _make_request(self, command: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make request to Minima MDS API.

        Args:
            command: Minima command to execute
            params: Optional parameters for the command

        Returns:
            Response data from Minima node

        Raises:
            MinimaClientError: If request fails
        """
        if not self.session_uid:
            raise MinimaClientError("Not authenticated - no session UID")

        try:
            # Build full command
            if params:
                filtered = {k: str(v) for k, v in params.items() if v is not None}
                param_str = " ".join(f"{k}:{v}" for k, v in filtered.items())
                full_command = f"{command} {param_str}"
            else:
                full_command = command

            logger.debug(f"Command: {full_command}")

            # URL encode the command
            encoded_command = quote(full_command, safe='')

            # MDS command endpoint with session UID
            cmd_url = f"{self.base_url}/mdscommand_/cmd?uid={self.session_uid}"

            logger.debug(f"URL: {cmd_url}")
            logger.debug(f"Encoded command: {encoded_command}")

            # POST the encoded command as plain text body
            response = self.session.post(
                cmd_url,
                data=encoded_command,
                headers={"Content-Type": "text/plain"},
                timeout=self.timeout
            )

            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response: {response.text[:500]}")

            if response.status_code != 200:
                raise MinimaClientError(
                    f"Request failed [{response.status_code}]: {response.text[:200]}"
                )

            # Parse JSON response
            try:
                data = response.json()
            except json.JSONDecodeError:
                raise MinimaClientError(f"Invalid JSON: {response.text[:200]}")

            # Check response status
            if isinstance(data, dict):
                # Handle pending commands (requires confirmation)
                if data.get("pending") is True and data.get("pendinguid"):
                    pending_uid = data.get("pendinguid")
                    logger.info(f"Command pending, auto-confirming with UID: {pending_uid}")

                    # Auto-confirm the pending command
                    confirm_command = f"mds action:confirm uid:{pending_uid}"
                    encoded_confirm = quote(confirm_command, safe='')

                    confirm_response = self.session.post(
                        cmd_url,
                        data=encoded_confirm,
                        headers={"Content-Type": "text/plain"},
                        timeout=self.timeout
                    )

                    if confirm_response.status_code != 200:
                        raise MinimaClientError(
                            f"Confirmation failed [{confirm_response.status_code}]: {confirm_response.text[:200]}"
                        )

                    try:
                        confirm_data = confirm_response.json()
                    except json.JSONDecodeError:
                        raise MinimaClientError(f"Invalid JSON in confirmation: {confirm_response.text[:200]}")

                    logger.info("Command confirmed successfully")
                    # Return the confirmation result
                    return confirm_data.get("response", confirm_data)

                if data.get("status") is False:
                    error_msg = data.get("message", data.get("error", "Unknown error"))
                    raise MinimaClientError(f"Command failed: {error_msg}")

                # Return response payload
                return data.get("response", data)

            return data

        except requests.exceptions.RequestException as e:
            raise MinimaClientError(f"Connection failed: {str(e)}")
        except MinimaClientError:
            raise
        except Exception as e:
            raise MinimaClientError(f"Unexpected error: {str(e)}")

    def _make_text_request(self, command: str, params: Optional[Dict[str, Any]] = None) -> str:
        """
        Make request to Minima MDS API and return plain text response.

        Args:
            command: Minima command to execute
            params: Optional parameters for the command

        Returns:
            Plain text response from Minima node

        Raises:
            MinimaClientError: If request fails
        """
        if not self.session_uid:
            raise MinimaClientError("Not authenticated - no session UID")

        try:
            # Build full command
            if params:
                filtered = {k: str(v) for k, v in params.items() if v is not None}
                param_str = " ".join(f"{k}:{v}" for k, v in filtered.items())
                full_command = f"{command} {param_str}"
            else:
                full_command = command

            logger.debug(f"Text command: {full_command}")

            # URL encode the command
            encoded_command = quote(full_command, safe='')

            # MDS command endpoint with session UID
            cmd_url = f"{self.base_url}/mdscommand_/cmd?uid={self.session_uid}"

            logger.debug(f"Text URL: {cmd_url}")
            logger.debug(f"Encoded command: {encoded_command}")

            # POST the encoded command as plain text body
            response = self.session.post(
                cmd_url,
                data=encoded_command,
                headers={"Content-Type": "text/plain"},
                timeout=self.timeout
            )

            logger.debug(f"Text response status: {response.status_code}")
            logger.debug(f"Text response: {response.text[:500]}")

            if response.status_code != 200:
                raise MinimaClientError(
                    f"Request failed [{response.status_code}]: {response.text[:200]}"
                )

            # Return plain text response (don't try to parse JSON)
            return response.text

        except requests.exceptions.RequestException as e:
            raise MinimaClientError(f"Connection failed: {str(e)}")
        except MinimaClientError:
            raise
        except Exception as e:
            raise MinimaClientError(f"Unexpected error: {str(e)}")

    def execute_command(self, command: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a Minima command with parameters.

        Args:
            command: Minima command to execute
            **kwargs: Command parameters

        Returns:
            Command response
        """
        return self._make_request(command, kwargs)

    def execute_command_text(self, command: str, **kwargs) -> str:
        """
        Execute a Minima command with parameters (returns plain text response).

        Args:
            command: Minima command to execute
            **kwargs: Command parameters

        Returns:
            Plain text command response
        """
        return self._make_text_request(command, kwargs)

    # Blockchain commands

    def get_balance(
        self,
        address: Optional[str] = None,
        tokenid: Optional[str] = None,
        confirmations: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get balance of Minima or specific token.

        Args:
            address: Optional specific address to check
            tokenid: Optional token ID (0x00 for Minima)
            confirmations: Required confirmations (default: None uses Minima default)

        Returns:
            Balance information
        """
        params = {
            "address": address,
            "tokenid": tokenid,
            "confirmations": confirmations
        }
        return self._make_request("balance", params)

    def get_status(self) -> Dict[str, Any]:
        """
        Get node status and blockchain information.

        Returns:
            Node status
        """
        return self._make_request("status")

    def send(
        self,
        amount: str,
        address: str,
        tokenid: str = "0x00",
        state: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Send Minima or tokens to an address.

        Args:
            amount: Amount to send
            address: Recipient address
            tokenid: Token ID (default: 0x00 for Minima)
            state: Optional state variables

        Returns:
            Transaction details
        """
        params = {
            "amount": amount,
            "address": address,
            "tokenid": tokenid
        }
        if state:
            params["state"] = json.dumps(state)

        return self._make_request("send", params)

    def create_token(
        self,
        name: str,
        amount: str,
        decimals: int = 8,
        description: Optional[str] = None,
        icon: Optional[str] = None,
        proof: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new token on Minima.

        Args:
            name: Token name
            amount: Total token amount
            decimals: Decimal places (default: 8)
            description: Optional token description
            icon: Optional icon URL/path
            proof: Optional proof data

        Returns:
            Token creation details
        """
        params = {
            "name": name,
            "amount": amount,
            "decimals": decimals,
            "description": description,
            "icon": icon,
            "proof": proof
        }
        return self._make_request("tokencreate", params)

    def get_tokens(self, tokenid: Optional[str] = None) -> Dict[str, Any]:
        """
        Get information about tokens.

        Args:
            tokenid: Optional specific token ID

        Returns:
            Token information
        """
        params = {"tokenid": tokenid} if tokenid else None
        return self._make_request("tokens", params)

    def get_address(self) -> Dict[str, Any]:
        """
        Get a new or existing Minima address.

        Returns:
            Address information
        """
        return self._make_request("getaddress")

    def get_coins(
        self,
        relevant: bool = True,
        sendable: bool = False,
        address: Optional[str] = None,
        tokenid: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get coins (UTxOs) information.

        Args:
            relevant: Show only relevant coins (default: True)
            sendable: Show only sendable coins
            address: Filter by address
            tokenid: Filter by token ID

        Returns:
            Coins information
        """
        params = {
            "relevant": str(relevant).lower(),
            "sendable": str(sendable).lower(),
            "address": address,
            "tokenid": tokenid
        }
        return self._make_request("coins", params)

    # MiniDapp commands

    def list_minidapps(self) -> Dict[str, Any]:
        """
        List all installed MiniDapps.

        Returns:
            List of MiniDapps
        """
        return self._make_request("mds")

    def install_minidapp(self, file_path: str) -> Dict[str, Any]:
        """
        Install a MiniDapp from .mds.zip file.

        Args:
            file_path: Path to .mds.zip file

        Returns:
            Installation result
        """
        return self._make_request("mds", {"action": "install", "file": file_path})

    def install_minidapp_text(self, file_path: str) -> str:
        """
        Install a MiniDapp from .mds.zip file (returns plain text response).

        Args:
            file_path: Path to .mds.zip file

        Returns:
            Plain text installation result
        """
        return self._make_text_request("mds", {"action": "install", "file": file_path})

    def get_minidapp_info(self, uid: str) -> Dict[str, Any]:
        """
        Get information about a specific MiniDapp.

        Args:
            uid: MiniDapp UID

        Returns:
            MiniDapp information
        """
        return self._make_request("mds", {"action": "info", "uid": uid})

    # Network commands

    def get_network_info(self) -> Dict[str, Any]:
        """
        Get network information.

        Returns:
            Network details
        """
        return self._make_request("network")

    def get_peers(self) -> Dict[str, Any]:
        """
        Get connected peers.

        Returns:
            Peer information
        """
        return self._make_request("peers")

    # Transaction commands

    def get_txpow(self, txpowid: str) -> Dict[str, Any]:
        """
        Get transaction proof of work details.

        Args:
            txpowid: Transaction PoW ID

        Returns:
            Transaction details
        """
        return self._make_request("txpow", {"txpowid": txpowid})

    def search_chain(
        self,
        block: Optional[int] = None,
        address: Optional[str] = None,
        tokenid: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search the blockchain.

        Args:
            block: Specific block number
            address: Search by address
            tokenid: Search by token ID

        Returns:
            Search results
        """
        params = {
            "block": block,
            "address": address,
            "tokenid": tokenid
        }
        return self._make_request("search", params)

    def health_check(self) -> bool:
        """
        Check if Minima node is responsive.

        Returns:
            True if node is healthy, False otherwise
        """
        try:
            result = self.get_status()
            return result is not None
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
            return False

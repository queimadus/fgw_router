"""Support for Altice FGW routers."""
import logging
import re
import telnetlib

import voluptuous as vol

from homeassistant.components.device_tracker import (
    DOMAIN,
    PLATFORM_SCHEMA,
    DeviceScanner,
)
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_PASSWORD, CONF_USERNAME
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

_DEVICES_REGEX = re.compile(
    r"(?P<mac>(([0-9A-F]{2}[:-]){5}([0-9A-F]{2})))\s*\|\s*Yes"
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_PORT): cv.port,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Required(CONF_USERNAME): cv.string,
    }
)


def get_scanner(hass, config):
    """Validate the configuration and return a FGW scanner."""
    scanner = FGWDeviceScanner(config[DOMAIN])

    return scanner if scanner.success_init else None


class FGWDeviceScanner(DeviceScanner):
    """This class queries a router running FGW firmware."""

    def __init__(self, config):
        """Initialize the scanner."""
        self.host = config[CONF_HOST]
        self.port = config[CONF_PORT]
        self.username = config[CONF_USERNAME]
        self.password = config[CONF_PASSWORD]
        self.interfaces = [0, 1]
        self.last_results = []

        # Test the router is accessible.
        data = self.get_fgw_data()
        self.success_init = data is not None

    def scan_devices(self):
        """Scan for new devices and return a list with found device IDs."""
        self._update_info()
        return self.last_results

    def get_device_name(self, device):
        """Return the name of the given device or None if we don't know."""
        return None

    def _update_info(self):
        """Ensure the information from the FGW router is up to date.

        Return boolean if scanning successful.
        """
        if not self.success_init:
            return False

        _LOGGER.info("Checking ARP")
        data = self.get_fgw_data()
        if not data:
            return False

        self.last_results = data
        return True

    def get_fgw_data(self):
        """Retrieve data from FGW and return parsed result."""
        try:
            telnet = telnetlib.Telnet(self.host, self.port)
            telnet.read_until(b"Login: ")
            telnet.write((self.username + "\r\n").encode("ascii"))
            telnet.read_until(b"Password: ")
            telnet.write((self.password + "\r\n").encode("ascii"))
            telnet.read_until(b"cli> ")
            devices_result = []
            for i in self.interfaces:
                telnet.write(("wireless/show-stationinfo --wifi-index=" + str(i) + "\r\n").encode("ascii"))
                devices_result = devices_result + telnet.read_until(b"cli> ").split(b"\r\n")
            telnet.write("quit\r\n".encode("ascii"))
        except EOFError:
            _LOGGER.exception("Unexpected response from router")
            return
        except ConnectionRefusedError:
            _LOGGER.exception("Connection refused by router. Telnet enabled?")
            return

        devices = []
        for device in devices_result:
            match = _DEVICES_REGEX.search(device.decode("utf-8"))
            if match:
	            devices.append(match.group("mac").upper())

        return devices

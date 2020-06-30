import re
from typing import List

import requests
from halo import Halo
from requests import Timeout

VALID_IP = re.compile(
    r'^' + r'(25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])\.' +
    r'(25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])\.' +
    r'(25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])\.' +
    r'(25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])$'
)


class ResolverError(Exception):
    """Resolver Exception"""

    pass


class Resolver:
    """Resolve the current dynamic IP asigned."""
    def __init__(self, providers: List[str], spinner: Halo):
        """Resolve the current dynamic IP asigned .

        The resolver use extenal providers to retrieve the current dynamic IP
        and parses the response.

        Args:
            providers (list[str]): list of providers, the providers are used
            in round robin fashion as a fallback in case of timeout or error.

        Returns:
            None

        Raises:
            None"""
        if not providers:
            raise ResolverError('the list of providers can not be None')

        self._providers = providers
        self._spinner = spinner

    @property
    def ip(self) -> str:
        """Return the IP parsed from a provider.

        Args:
            None

        Return:
            (str): The IP parsed from the provider.

        Raises:
            ResolverError: in case all providers fail in retrieve the IP."""
        for provider in self._providers:
            try:
                provider = self._providers.pop(0)

                r = requests.get(provider, timeout=30.0)

                if r.ok:
                    match = re.search(VALID_IP, r.text)

                    if match:
                        return '.'.join(match.group(1, 2, 3, 4))

                    self._spinner.warn(
                        f"No valid IP found on '{provider}', trying next one"
                    )
            except Timeout:
                self._spinner.warn(f"Provider: '{provider}' timeout, trying next one")

        raise ResolverError('all provider failed or timeout')

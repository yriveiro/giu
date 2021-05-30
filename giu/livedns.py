from typing import Dict
from typing import List
from typing import Optional

import requests
from halo import Halo
from requests import Timeout
from requests.utils import requote_uri

DEFAULT_TTL = 1800


class LiveDNSException(Exception):
    """LiveDNS client exception."""

    pass


class LiveDNS:
    def __init__(self, url: str, key: str, spinner: Halo, **kwargs) -> None:
        """Gandi LiveDNS API client.

        Arg:
            url (str): Gandi LiveDNS API url
            key (str): Gandi key to access the Live DNS API.

        Optional:
            dry_run (bool): disable any update operation.

        Return:
            None.

        Raises:
            None"""
        self._url = url
        self._key = key
        self._spinner = spinner

        self._headers = {
            'Authorization': f'Apikey {self._key}',
            'Accept': 'application/json',
        }

        self._dry_run = kwargs.get('dry_run')

    def _send(self,
              endpoint: str,
              method: str = 'GET',
              data: Optional[Dict] = None) -> Optional[Dict]:
        """Send a HTTP request to Gandi Live DNS API.

        Args:
            endpoint (str): Live DNS API enpoint.
            method (str): HTTP method.
            data (str): payload to attach to the request.

        Returns:
            None on error.
            JSON object representing the response of Live DNS API

        Raises:
            None."""
        headers = self._headers.copy()

        # parameters
        if not self._url.endswith('/') and not endpoint.startswith('/'):
            endpoint = f'/{endpoint}'

        url = requote_uri(f'{self._url}{endpoint}')

        if data:
            headers['Content-type'] = 'application/json'

        # request
        try:
            r = requests.request(
                method=method, url=url, headers=headers, json=data, timeout=60.0
            )
        except Timeout:
            return None

        if not r.ok:
            return None

        if r.status_code == 204:  # HTTP/204 No content (on success)
            return {'code': 204, 'message': 'ok'}

        return r.json()

    def _snapshot(self, domain: str, name: str) -> Optional[Dict[str, str]]:
        """Snapshot the current state of the DNS.

        Gandi Live DNS will store this snapshot as a backup if a manual rollback
        is needed.

        Args:
            domain (str): domain where we will perform the snapshot.
            name (str): the name of the snapshot.

        Returns:
            None in case of error otherwise a JSON object representing the response.

        Raises:
            None."""
        return self._send(
            endpoint=f'domains/{domain}/snapshots', method='POST', data={'name': name}
        )

    def _delete_snapshot(self, domain: str, uuid: str) -> Optional[Dict]:
        """Delete the given snapshot.

        Args:
            domain (str): domain where we will delete the snapshot.
            uuid (str): unique identifier of the snapshot to delete.

        Returns:
            None in case of error otherwise a JSON object representing the response.

        Raises:
            None."""
        return self._send(
            endpoint=f'domains/{domain}/snapshots/{uuid}', method='DELETE'
        )

    def _domain_exists(self, domain: str) -> Optional[Dict]:
        """Check if the given domain exists in Live DNS table.

        Args:
            domain (str): domain to check.

        Returns:
            None in case of error otherwise a JSON object representing the response.

        Raises:
            None."""
        return self._send(endpoint=f'domains/{domain}')

    def _get_record(self, domain: str, record: Dict[str, str]) -> Optional[Dict]:
        """Retrieve the selecte record from given domain.

        Args:
            domain (str): domain name.
            record (Dict[srt, str]): DNS record to retrieve.

        Returns:
            None in case of error otherwise a JSON object representing the response.

        Raises:
            None."""
        return self._send(
            endpoint=f"domains/{domain}/records/{record['name']}/{record['type']}"
        )

    def _update_record(self, domain: str, record: Dict[str, str],
                       value: str) -> Optional[Dict]:
        """Update the DNS record for the defined domain.

        Args:
            domain (str): domain name.
            record (Dict[srt, str]): DNS record to retrieve.
            value (srt): value to update in Gandi LiveDNS record

        Returns:
            None in case of error otherwise a JSON object representing the response.

        Raises:
            None."""

        data = {
            'rrset_ttl': record['ttl'] or DEFAULT_TTL,
            'rrset_values': [value],
        }

        return self._send(
            endpoint=f"domains/{domain}/records/{record['name']}/{record['type']}",
            method='PUT',
            data=data,
        )

    def _diff(self, ip: str, ttl: int, r: Dict) -> bool:
        """Checks if exists differences between config and Gandi state"""
        return (ttl != r['rrset_ttl']) or (ip != r['rrset_values'][0])

    def _sync(self, ip: str, domain: str, record: Dict[str, str]) -> None:
        """Sync a single record to Gandi

        Args:
            ip (str): the current ip
            domain (str): domain name.
            record (Dict[srt, str]): DNS record to update.

        Returns:
            None.

        Raises:
            Exception on case of failure."""
        self._spinner.info(
            f"TTL for 'A' record '{record['name']}' on config: {record['ttl']}"
        )

        snapshot = None

        try:
            self._spinner.start(
                f"Getting A record '{record['name']}' info for {domain} from Gandi LiveDNS"
            )

            r = self._get_record(domain, record)

            if not r:
                raise RuntimeError('record not found')

            self._spinner.succeed(
                f"'A' record '{record['name']}' for {domain} from Gandi LiveDNS"
            )
            self._spinner.info(
                f"IP for 'A' record '{record['name']}' on Gandi LiveDNS: {''.join(r['rrset_values'])}"
            )
            self._spinner.info(
                f"TTL for 'A' record '{record['name']}' on Gandi LiveDNS: {r['rrset_ttl']}"
            )

            if not self._diff(ip, int(record['ttl']), r):
                self._spinner.info('Dynamic IP and TTL are up to date on Gandi LiveDNS')
            else:
                if self._dry_run:
                    self._spinner.info('Update needed, dry run mode, no update done.')
                else:
                    self._spinner.start('Creating LiveDNS snapshot')
                    snapshot = self._snapshot(domain, 'giu')

                    if not snapshot:
                        raise RuntimeError('snapshot: operation failed, update aborted')

                    self._spinner.succeed(f"Snapshot {snapshot['message']} created")

                    self._spinner.start(
                        f"Updating 'A' record '{record['name']}' on Gandi LiveDNS"
                    )
                    self._update_record(domain, record, ip)
                    self._spinner.succeed(
                        f"'A' record '{record['name']}' on Gandi LiveDNS updated"
                    )
        except Exception as exc:
            raise Exception('sync failed') from exc
        finally:
            if not self._dry_run and snapshot:
                self._spinner.start(f"Deleting snapshot {snapshot['message']}")
                self._delete_snapshot(domain, snapshot['message'])
                self._spinner.succeed(f"Snapshot {snapshot['message']} deleted")

    def sync(self, ip: str, domain: str, records: List[Dict[str, str]]) -> None:
        """Sync all A records on config file to Gandi

        Args:
            ip (str): the current ip
            domain (str): domain name.
            records (List[Dict[srt, str]]): DNS records to update.

        Returns:
            None.

        Raises:
            Exception on case of failure."""
        if not self._domain_exists(domain):
            raise RuntimeError(f"requested domain: '{domain}' does not exists")

        _records = filter(lambda r: r['type'] == 'A', records)

        if not _records:
            raise LiveDNSException("no 'A' record for {domain} in config")

        for r in _records:
            self._sync(ip, domain, r)

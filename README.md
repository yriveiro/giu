# py-gdu
Gandi LiveDNS Updater - commnand line tool to keep your dynamic ip up to date.

## Prequisites

* A valid key fro Gandi LiveDNS API. Use https://account.gandi.net/en/users/USER/security
(`USER` is your Gandi user account).
* Python 3.

## Installation

The recommended way to install this package is through [pip](https://pip.pypa.io/en/stable/).

```shell
pip install --user py-gdu
```

## Usage

To use `gdu` you need to create a `config.toml` file to hold the minimal set of
configurations.

```toml
[api]
url = 'https://dns.api.gandi.net/api/v5'
key = 'YOUR_KEY'

[dns]
domain = 'example.com'
records = [
    {'type' = 'A', 'name' = '@', 'ttl' = 18000},
]

[resolver]
providers = [
    'http://ipecho.net/plain',
    'https://ifconfig.me/ip',
    'http://www.mon-ip.fr'
]
```

### One shot
In this example the config file was created on `$HOME/.gdu/config.toml`.

```shell
gdu sync --conf $HOME/.gdu/config.toml
```

### Cronjob

```shell
$ crontab -e
* */2 * * * gdu sync --conf $HOME/.gdu/config.toml
```

# GIU
Gandi LiveDNS Updater - Command line tool to keep your dynamic ip up to date.

[![yriveiro](https://circleci.com/gh/yriveiro/giu.svg?style=svg)](https://circleci.com/gh/yriveiro/giu)

[![Downloads/Week](https://static.pepy.tech/personalized-badge/giu?period=week&units=international_system&left_color=black&right_color=orange&left_text=Downloads/Week)](https://pepy.tech/project/giu) [![Downloadsi/Month](https://static.pepy.tech/personalized-badge/giu?period=month&units=international_system&left_color=black&right_color=orange&left_text=Downloads/Month)](https://pepy.tech/project/giu) [![Downloads](https://static.pepy.tech/personalized-badge/giu?period=total&units=international_system&left_color=black&right_color=orange&left_text=Downloads)](https://pepy.tech/project/giu)

## Prequisites

* A valid key fro Gandi LiveDNS API. Use https://account.gandi.net/en/users/USER/security
(`USER` is your Gandi user account).
* Python 3.

## Installation

The recommended way to install this package is through [pip](https://pip.pypa.io/en/stable/).

```shell
pip install --user giu
```

## Usage

To use `giu` you need to create a `config.toml` file to hold the minimal set of
configurations.

```toml
[api]
url = 'https://dns.api.gandi.net/v5/livedns'
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
In this example the config file was created on `$HOME/.giu/example.com.toml`.

```shell
giu sync --conf $HOME/.giu/example.com.toml
```

### Cronjob
In this example the config file was created on `$HOME/.giu/example.com.toml`.

```shell
$ crontab -e
* */2 * * * giu sync --conf $HOME/.giu/example.com.toml
```

### Docker
In this example the config is mounted as part of a config folder.

```shell
docker run -it --rm -v config-folder:/tmp/ yriveiro/giu:latest giu sync --config /tmp/config.toml
```

## Improvements

Some improvements that I have ff the top of my head:

* `put` command to create entries like CNAMES and so on.
* `delete` command to delete entries
* `backup` command to do backups
* --Docker Image to run giu with docker compose or as a Cronjob on Kubernetes.--

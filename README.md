# Python-monobankua
[![PyPI](https://img.shields.io/pypi/v/monobankua.svg)](https://pypi.org/project/monobankua/) [![Build Status](https://travis-ci.org/inbalboa/python-monobankua.svg?branch=master)](https://travis-ci.org/inbalboa/python-monobankua) [![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

Python client library for [Monobank](https://monobank.ua/) [API](https://api.monobank.ua/docs/).

## Installation

```
pip3 install monobankua
```

## Requirements
* python >= 3.7
* requests >= 2.21
* ecdsa >= 0.13.2

## Usage

### Personal API

Full personal API description see at https://api.monobank.ua/docs/

1. Create your token at https://api.monobank.ua/
2. Use it to initialize client.

#### Code snippet

```python
from datetime import datetime, timedelta
from monobankua import Monobank, MonobankError, MonobankRateLimitError, MonobankUnauthorizedError

try:
    currencies_info = Monobank.currencies_info() # you don't need token to get an exchange rates
    print(*currencies_info, sep='\n')

    token = 'xxxxxxxxxxxxxxxxxxxxx'
    monobank = Monobank(token)

    client_name, webhook_url, accounts = monobank.client_info()
    print(client_name)
    print(webhook_url)

    for account in accounts:
        print(f'{account.card}: {account}')
        statements = monobank.statements(account.id, (datetime.now() - timedelta(days=6)).date())
        print(*statements, sep='\n')
except MonobankRateLimitError:
	print('Too many requests. Wait 1 minute, please')
except MonobankUnauthorizedError as e:
	print(f'Some authorization problem: {e}')
except MonobankError as e:
	print(e)
```

### Corporate API

Corporate API has the same methods as personal API, but doesn't have rate limitation.

Corporate API is the only way for non-personal use of open Monobank API.

Full description see at https://api.monobank.ua/docs/corporate.html

1. Generate private key. Sample shell command:
```bash
openssl ecparam -genkey -name secp256k1 -rand /dev/urandom -out priv.key
```

2. Generate public key. Sample shell command:
```bash
openssl ec -in priv.key -pubout -out pub.key
```

3. Request API access. Send brief description of your service to api@monobank.ua with attached pub.key (be careful - not priv.key!).

4. Since Monobank approved your access, you should request user access.

5. Now, save request id to your DB or something else, and show the accept URL to user.

6. Check user acceptance & use all the same methods as for personal API.

#### Code snippet

```python
from monobankua import MonobankCorporate

private_key = 'xxxxxxxxxxxxxxxxxxxxx' # from priv.key
request_id, accept_url = MonobankCorporate.access_request(private_key, statement=True, personal=True)
 # you can set webhook URL to be notified about user acceptance:
 # request_id, accept_url = MonobankCorporate.access_request(private_key, statement=True, personal=True, webhook_url='https://yourservice.com/hook/')
monobank_corporate = MonobankCorporate(private_key, request_id)
if monobank_corporate.access_check():
	... # normal use the same way as for personal API
```

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

## Usage

1. Create your token at https://api.monobank.ua/
2. Use it to initialize client. Sample code:

```python
from datetime import datetime
from monobankua import Monobank
  
TOKEN = "xxxxxxxxxxxxxxxxxxxxx"

monobank = Monobank(TOKEN)

currencies_info = monobank.currencies_info()
print(*currencies_info, sep='\n')

client_name, webhook_url, accounts = monobank.client_info()
print(client_name)
print(webhook_url)

for account in accounts:
    print(f'{account.currency.name}: {account}')
    statements = monobank.statements(account.id, datetime(2019, 6, 25))
    print(*statements, sep='\n')
```

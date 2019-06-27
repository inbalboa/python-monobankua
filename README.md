# python-monobankua

Python client library for [Monobank](https://monobank.ua/) [API](https://api.monobank.ua/docs/)

## Installation

```
pip3 install monobankua
```

## Requirements
```
* python >= 3.7
* requests >= 2.21
```

## Usage

1. Create your token at https://api.monobank.ua/
2. Use it to initialize client. Sample code:

```python
from datetime import datetime
from monobankua import Monobank
  
TOKEN = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

monobank = Monobank(TOKEN)

currencies_info = monobank.currencies_info()
print(*currencies_info, sep='\n')

client_name, accounts = monobank.client_info()
print(client_name)

for account in accounts:
    print(f'{account.currency.name}: {account}')
    statements = monobank.statements(account.id, datetime(2019, 6, 25))
    print(*statements, sep='\n')
```

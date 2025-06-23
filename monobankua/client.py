#!/usr/bin/env python3

import operator
from abc import ABC, abstractmethod
from collections import namedtuple
from collections.abc import Generator
from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

import requests

from monobankua.sign import SignKey


class MonobankError(Exception):
    pass


class MonobankRateLimitError(MonobankError):
    pass


class MonobankUnauthorizedError(MonobankError):
    pass


class MonobankBase(ABC):
    API = 'https://api.monobank.ua'
    UA = 'github.com/inbalboa/python-monobankua'
    TZ = ZoneInfo('Europe/Kyiv')

    @staticmethod
    def _currency_helper(currency_code):
        Currency = namedtuple('Currency', ('code', 'name', 'symbol'))
        currencies = {
            124: Currency(124, 'CAD', 'cad'),
            203: Currency(203, 'CZK', 'czk'),
            208: Currency(208, 'DKK', 'dkk'),
            348: Currency(348, 'HUF', 'huf'),
            643: Currency(643, 'RUB', '₽'),
            756: Currency(756, 'CHF', 'chf'),
            826: Currency(826, 'GBP', '£'),
            933: Currency(933, 'BYN', 'byn'),
            949: Currency(949, 'TRY', '₺'),
            985: Currency(985, 'PLN', 'pln'),
            978: Currency(978, 'EUR', '€'),
            840: Currency(840, 'USD', '$'),
            980: Currency(980, 'UAH', '₴')
        }
        return currencies.get(currency_code, Currency(currency_code, str(currency_code), str(currency_code)))

    @dataclass
    class CurrencyInfo:
        currencyCodeA: int  # noqa: N815
        currencyCodeB: int  # noqa: N815
        date: int
        rateSell: float = 0  # noqa: N815
        rateBuy: float = 0  # noqa: N815
        rateCross: float = 0  # noqa: N815

        @property
        def currency_a(self):
            return MonobankBase._currency_helper(self.currencyCodeA)

        @property
        def currency_b(self):
            return MonobankBase._currency_helper(self.currencyCodeB)

        @property
        def datetime(self):
            return datetime.fromtimestamp(self.date, tz=MonobankBase.TZ)

        def __str__(self):
            rate = {
                'продаж': self.rateSell,
                'купівля': self.rateBuy,
                'крос-курс': self.rateCross
            }
            rate_view = ', '.join([f'{k} {v}' for k, v in rate.items() if v])
            return f'{self.datetime} {self.currency_a.name} -> {self.currency_b.name}: {rate_view}'

    @dataclass
    class ClientInfo:

        @dataclass
        class Account:
            id: str
            sendId: str  # noqa: N815
            balance: int
            creditLimit: int  # noqa: N815
            type: str
            currencyCode: int  # noqa: N815
            cashbackType: str  # noqa: N815
            maskedPan: list[str]  # noqa: N815
            iban: str

            @property
            def currency(self):
                return MonobankBase._currency_helper(self.currencyCode)

            @property
            def send_link(self):
                return f'https://send.monobank.ua/{self.sendId}'

            def __str__(self):
                return f'{self.currency.name} {self.maskedPan[0]} {self.type}'

        @dataclass
        class Jar:
            id: str
            sendId: str  # noqa: N815
            title: str
            description: str
            currencyCode: int  # noqa: N815
            balance: int
            goal: int

            @property
            def currency(self):
                return MonobankBase._currency_helper(self.currencyCode)

            @property
            def send_link(self):
                return f'https://send.monobank.ua/{self.sendId}'

            def __str__(self):
                return self.title

        clientId: str  # noqa: N815
        name: str
        webHookUrl: str  # noqa: N815
        permissions: str
        accounts: Generator[Account]
        jars: Generator[Jar]

        def __str__(self):
            return self.name

    @dataclass
    class Statement:
        id: str
        time: int
        description: str
        mcc: int
        originalMcc: int  # noqa: N815
        hold: bool
        amount: int
        operationAmount: int  # noqa: N815
        currencyCode: int  # noqa: N815
        commissionRate: int  # noqa: N815
        cashbackAmount: int  # noqa: N815
        balance: int
        comment: str = ''
        receiptId: str = None  # noqa: N815
        invoiceId: str = None  # noqa: N815
        counterEdrpou: str = None  # noqa: N815
        counterIban: str = None  # noqa: N815
        counterName: str = None  # noqa: N815

        @property
        def datetime(self):
            return datetime.fromtimestamp(self.time, tz=MonobankBase.TZ)

        @property
        def income(self):
            return self.amount > 0

        @property
        def currency(self):
            return MonobankBase._currency_helper(self.currencyCode)

        @property
        def category(self):
            return self._mcc_helper(self.mcc)

        @staticmethod
        def _mcc_helper(mcc):  # noqa: C901
            Category = namedtuple('Category', ('name', 'symbol'))
            if mcc in (4011, 4111, 4112, 4131, 4304, 4411, 4415, 4418, 4457, 4468, 4511, 4582, 4722, 4784, 4789, 5962,
                       6513, 7011, 7032, 7033, 7512, 7513, 7519) or mcc in range(3000, 4000):
                return Category('Подорожі', '🚆')
            if mcc in (4119, 5047, 5122, 5292, 5295, 5912, 5975, 5976, 5977, 7230, 7297, 7298, 8011, 8021, 8031, 8049,
                         8050, 8062, 8071, 8099) or mcc in range(8041, 8044):
                return Category('Краса та медицина', '🏥')
            if mcc in (5733, 5735, 5941, 7221, 7333, 7395, 7929, 7932, 7933, 7941, 7991, 7995, 8664)\
                    or mcc in range(5970, 5974) or mcc in range(5945, 5948) or mcc in range(5815, 5819)\
                    or mcc in range(7911, 7923) or mcc in range(7991, 7995) or mcc in range(7996, 8000):
                return Category('Розваги та спорт', '🎾')
            if mcc in range(5811, 5815):
                return Category('Кафе та ресторани', '🍴')
            if mcc in (5297, 5298, 5300, 5311, 5331, 5399, 5411, 5412, 5422, 5441, 5451, 5462, 5499, 5715, 5921):
                return Category('Продукти й супермаркети', '🏪')
            if mcc in (7829, 7832, 7841):
                return Category('Кіно', '🎞')
            if mcc in (5172, 5511, 5541, 5542, 5983, 7511, 7523, 7531, 7534, 7535, 7538, 7542, 7549)\
                    or mcc in range(5531, 5534):
                return Category('Авто та АЗС', '⛽')
            if mcc in (5131, 5137, 5139, 5611, 5621, 5631, 5641, 5651, 5655, 5661, 5681, 5691, 5697, 5698, 5699, 5931,
                         5948, 5949, 7251, 7296):
                return Category('Одяг і взуття', '👖')
            if mcc == 4121:
                return Category('Таксі', '🚕')
            if mcc in (742, 5995):
                return Category('Тварини', '🐈')
            if mcc in (2741, 5111, 5192, 5942, 5994):
                return Category('Книги', '📚')
            if mcc in (5992, 5193):
                return Category('Квіти', '💐')
            if mcc == 4814:
                return Category('Поповнення мобільного', '📞')
            if mcc == 4829:
                return Category('Грошові перекази', '💸')
            if mcc == 4900:
                return Category('Комунальні послуги', '🚰')
            return Category('Інше', '❓')

        def __str__(self):
            currency = self.currency.symbol
            amount = f'{self.amount / 100:n} {currency}'
            balance = f'{self.balance / 100:n} {currency}'
            cashback = f', кешбек {self.cashbackAmount / 100:n} {currency}' if self.cashbackAmount else ''
            commission = f', комісія {self.commissionRate / 100:n} {currency}' if self.commissionRate else ''
            category_symbol = '💸' if self.income else self.category.symbol
            datetime = self.datetime.strftime('%d.%m.%Y %H:%M')
            comment = (f' «{self.comment}»' if self.comment else '').replace('\n', ' ')
            description = self.description.replace('\n', ' ')
            return (
                f'{datetime} {category_symbol} '
                f'{description}{comment}: {amount}{cashback}{commission}. Баланс: {balance}'
            )

    @classmethod
    def _get_url(cls, path):
        return f'{cls.API}{path}'

    @abstractmethod
    def _get_headers(self, path):
        ...

    @classmethod
    def _make_request(cls, path, method=None, headers=None, body=None):
        headers_ = headers or {}
        headers_['User-Agent'] = cls.UA
        response = requests.request(method or 'GET', cls._get_url(path), headers=headers_, json=body, timeout=10)
        raw_data = response.json() if response.content else {}
        status_code = response.status_code
        if status_code != requests.codes.ok:
            error_description = raw_data.get('errorDescription', str(raw_data))
            message = f'Error {status_code}: {error_description}'
            if status_code == requests.codes.too_many_requests:
                raise MonobankRateLimitError(message)
            if status_code in (requests.codes.unauthorized, requests.codes.forbidden, requests.codes.not_found):
                raise MonobankUnauthorizedError(message)
            raise MonobankError(message)
        return raw_data

    @classmethod
    def currencies_info(cls):
        currency_info_data = cls._make_request('/bank/currency')
        return [cls.CurrencyInfo(**x) for x in currency_info_data]

    def client_info(self):
        path = '/personal/client-info'
        client_info_data = MonobankBase._make_request(path, headers=self._get_headers(path))
        accounts = (self.ClientInfo.Account(**x) for x in client_info_data['accounts'])
        jars = (self.ClientInfo.Jar(**x) for x in client_info_data['jars']) if ('jars' in client_info_data.keys()) else None
        return self.ClientInfo(
            clientId=client_info_data['clientId'],
            name=client_info_data['name'],
            webHookUrl=client_info_data.get('webHookUrl', ''),
            permissions=client_info_data.get('permissions', ''),
            accounts=accounts,
            jars=jars
        )

    def statements(self, account_id, date_from, date_to=None):
        if date_to and date_from > date_to:
            msg = 'Error: begin date > end date'
            raise ValueError(msg)

        date_from_ = date_from.strftime('%s')
        date_to_ = date_to.strftime('%s') if date_to else ''
        path = f'/personal/statement/{account_id}/{date_from_}/{date_to_}'
        statements_data = MonobankBase._make_request(path, headers=self._get_headers(path))
        return (self.Statement(**x) for x in sorted(statements_data, key=operator.itemgetter('time'), reverse=True))


class Monobank(MonobankBase):
    def __init__(self, token=None):
        self.token = token

    def _get_headers(self, path=None):  # noqa: ARG002
        header = {}
        if self.token:
            header['X-Token'] = self.token
        return header

    def set_webhook(self, webhook_url):
        Monobank._make_request('/personal/webhook', method='POST', headers=self._get_headers(), body={'webHookUrl': webhook_url})


class MonobankCorporate(MonobankBase):
    def __init__(self, private_key, request_id):
        self.key = SignKey(private_key)
        self.request_id = request_id

    def _get_headers(self, path):
        headers = {
            'X-Key-Id': self.key.key_id,
            'X-Time': datetime.now(tz=MonobankBase.TZ).strftime('%s'),
            'X-Request-Id': self.request_id
        }
        str_to_sign = ''.join((headers['X-Time'], headers['X-Request-Id'], path))
        headers['X-Sign'] = self.key.sign(str_to_sign)
        return headers

    def access_check(self):
        try:
            path = '/personal/auth/request'
            MonobankCorporate._make_request(path, headers=self._get_headers(path))
        except MonobankUnauthorizedError:
            return False
        return True

    @staticmethod
    def access_request(private_key, statement=None, personal=None, webhook_url=None):
        permissions = ''
        if statement:
            permissions = 's'
        if personal:
            permissions += 'p'
        if not permissions:
            msg = 'Neither statement nor personal permission are requested'
            raise MonobankError(msg)
        headers = {
            'X-Time': datetime.now(tz=MonobankBase.TZ).strftime('%s'),
            'X-Permissions': permissions
        }
        if webhook_url:
            headers['X-Callback'] = webhook_url
        path = '/personal/auth/request'
        key = SignKey(private_key)
        str_to_sign = ''.join((headers['X-Time'], headers['X-Permissions'], path))
        headers['X-Sign'] = key.sign(str_to_sign)
        headers['X-Key-Id'] = key.key_id
        raw_data = MonobankCorporate._make_request(path, method='POST', headers=headers)
        request_id = raw_data['tokenRequestId']
        accept_url = raw_data['acceptUrl']
        return request_id, accept_url

#!/usr/bin/env python3

from abc import ABC, abstractmethod
from collections import namedtuple
from dataclasses import dataclass
from datetime import datetime
import operator
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
        currencyCodeA: int
        currencyCodeB: int
        date: int
        rateSell: int = 0
        rateBuy: int = 0
        rateCross: int = 0

        @property
        def currencyA(self):
            return Monobank._currency_helper(self.currencyCodeA)

        @property
        def currencyB(self):
            return Monobank._currency_helper(self.currencyCodeB)

        @property
        def datetime(self):
            return datetime.fromtimestamp(self.date)

        def __str__(self):
            rate = {
                'продаж': self.rateSell,
                'купівля': self.rateBuy,
                'крос-курс': self.rateCross
            }
            rate_view = ', '.join([f'{k} {v}' for k, v in rate.items() if v])
            return f'{self.datetime} {self.currencyA.name} -> {self.currencyB.name}: {rate_view}'

    @dataclass
    class Account:
        id: str
        currencyCode: int
        cashbackType: str
        balance: int
        creditLimit: int
        maskedPan: str
        type: str

        @property
        def currency(self):
            return Monobank._currency_helper(self.currencyCode)

        @property
        def card(self):
            return f'{self.currency.name} {self.maskedPan[0]} {self.type}'

        def __str__(self):
            return f'{self.balance // 100:g} {self.currency.symbol}'

    @dataclass
    class Statement:
        id: str
        time: int
        description: str
        mcc: int
        hold: bool
        amount: int
        operationAmount: int
        currencyCode: int
        commissionRate: int
        cashbackAmount: int
        balance: int
        comment: str = ''

        @property
        def datetime(self):
            return datetime.fromtimestamp(self.time)

        @property
        def income(self):
            return self.amount > 0

        @property
        def currency(self):
            return Monobank._currency_helper(self.currencyCode)

        @property
        def category(self):
            return self._mcc_helper(self.mcc)

        @staticmethod
        def _mcc_helper(mcc):
            Category = namedtuple('Category', ('name', 'symbol'))
            if mcc in (4011, 4111, 4112, 4131, 4304, 4411, 4415, 4418, 4457, 4468, 4511, 4582, 4722, 4784, 4789, 5962,
                       6513, 7011, 7032, 7033, 7512, 7513, 7519) or mcc in range(3000, 4000):
                return Category('Подорожі', '🚆')
            elif mcc in (4119, 5047, 5122, 5292, 5295, 5912, 5975, 5976, 5977, 7230, 7297, 7298, 8011, 8021, 8031, 8049,
                         8050, 8062, 8071, 8099) or mcc in range(8041, 8044):
                return Category('Краса та медицина', '🏥')
            elif mcc in (5733, 5735, 5941, 7221, 7333, 7395, 7929, 7932, 7933, 7941, 7991, 7995, 8664)\
                    or mcc in range(5970, 5974) or mcc in range(5945, 5948) or mcc in range(5815, 5819)\
                    or mcc in range(7911, 7923) or mcc in range(7991, 7995) or mcc in range(7996, 8000):
                return Category('Розваги та спорт', '🎾')
            elif mcc in range(5811, 5815):
                return Category('Кафе та ресторани', '🍴')
            elif mcc in (5297, 5298, 5300, 5311, 5331, 5399, 5411, 5412, 5422, 5441, 5451, 5462, 5499, 5715, 5921):
                return Category('Продукти й супермаркети', '🏪')
            elif mcc in (7829, 7832, 7841):
                return Category('Кіно', '🎞')
            elif mcc in (5172, 5511, 5541, 5542, 5983, 7511, 7523, 7531, 7534, 7535, 7538, 7542, 7549)\
                    or mcc in range(5531, 5534):
                return Category('Авто та АЗС', '⛽')
            elif mcc in (5131, 5137, 5139, 5611, 5621, 5631, 5641, 5651, 5655, 5661, 5681, 5691, 5697, 5698, 5699, 5931,
                         5948, 5949, 7251, 7296):
                return Category('Одяг і взуття', '👖')
            elif mcc == 4121:
                return Category('Таксі', '🚕')
            elif mcc in (742, 5995):
                return Category('Тварини', '🐈')
            elif mcc in (2741, 5111, 5192, 5942, 5994):
                return Category('Книги', '📚')
            elif mcc in (5992, 5193):
                return Category('Квіти', '💐')
            elif mcc == 4814:
                return Category('Поповнення мобільного', '📞')
            elif mcc == 4829:
                return Category('Грошові перекази', '💸')
            elif mcc == 4900:
                return Category('Комунальні послуги', '🚰')
            else:
                return Category('Інше', '❓')

        def __str__(self):
            currency = self.currency.symbol
            amount = f'{self.amount / 100:g} {currency}'
            balance = f'{self.balance / 100:g} {currency}'
            cashback = f', кешбек {self.cashbackAmount / 100:g} {currency}' if self.cashbackAmount else ''
            commission = f', комісія {self.commissionRate / 100:g} {currency}' if self.commissionRate else ''
            category_symbol = '💸' if self.income else self.category.symbol
            datetime = self.datetime.strftime('%d.%m.%Y %H:%M')
            comment = (f' «{self.comment}»' if self.comment else '').replace('\n', ' ')
            description = self.description.replace('\n', ' ')
            return f'{datetime} {category_symbol} '\
                f'{description}{comment}: {amount}{cashback}{commission}. Баланс: {balance}'

    @classmethod
    def _get_url(cls, path):
        return f'{cls.API}{path}'

    @abstractmethod
    def _get_headers(self, path):
        pass

    @classmethod
    def _make_request(cls, path, method=None, headers=None, body=None):
        headers_ = headers or {}
        headers_['User-Agent'] = cls.UA
        response = requests.request(method or 'GET', cls._get_url(path), headers=headers_, json=body)
        raw_data = response.json() if response.content else {}
        status_code = response.status_code
        if status_code != requests.codes.ok:
            error_description = raw_data.get('errorDescription', str(raw_data))
            message = f'Error {status_code}: {error_description}'
            if status_code == requests.codes.too_many_requests:
                raise MonobankRateLimitError(message)
            elif status_code in (requests.codes.unauthorized, requests.codes.forbidden, requests.codes.not_found):
                raise MonobankUnauthorizedError(message)
            else:
                raise MonobankError(message)
        return raw_data

    @classmethod
    def currencies_info(cls):
        currency_info_data = cls._make_request('/bank/currency')
        currencies_info = [cls.CurrencyInfo(**x) for x in currency_info_data]
        return currencies_info

    def client_info(self):
        path = '/personal/client-info'
        client_info_data = MonobankBase._make_request(path, headers=self._get_headers(path))
        client_name = client_info_data['name']
        webhook_url = client_info_data.get('webHookUrl', '')
        accounts = [self.Account(**x) for x in client_info_data['accounts']]
        return client_name, webhook_url, accounts

    def statements(self, account_id, date_from, date_to=None):
        if date_to and date_from > date_to:
            raise ValueError('Error: begin date > end date')

        date_from_ = date_from.strftime('%s')
        date_to_ = date_to.strftime('%s') if date_to else ''
        path = f'/personal/statement/{account_id}/{date_from_}/{date_to_}'
        statements_data = MonobankBase._make_request(path, headers=self._get_headers(path))
        statements = [self.Statement(**x) for x in sorted(statements_data, key=operator.itemgetter('time'))]
        return statements


class Monobank(MonobankBase):
    def __init__(self, token=None):
        self.token = token

    def _get_headers(self, path=None):
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
            'X-Time': datetime.now().strftime('%s'),
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
            raise MonobankError('Neither statement nor personal permission are requested')
        headers = {
            'X-Time': datetime.now().strftime('%s'),
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

#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
from collections import Mapping
import unicodedata


def isbn13to10(isbn13):
    digits = re.sub(r'\d{3}(\d{9})\d', r'\1', isbn13)
    checkdigit = 11 - sum(int(digits[i]) * (10 - i) for i in range(len(digits))) % 11
    if checkdigit == 10:
        checkdigit = 'X'
    elif checkdigit == 11:
        checkdigit = 0
    return digits + str(checkdigit)


def isbn10to13(isbn10):
    digits = '978' + isbn10[:-1]
    checkdigit = 10 - sum(int(digits[i]) * (1 + 2 * (i % 2)) for i in range(len(digits))) % 10
    if checkdigit == 10:
        checkdigit = 0
    return digits + str(checkdigit)


def normalize(text):
    if not isinstance(text, str):
        return text
    return unicodedata.normalize('NFKC', text)

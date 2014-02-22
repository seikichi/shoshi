#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from shoshi import ndl
from shoshi.metadata import Title, TitleElement, Series, Creator


class TestNDL(unittest.TestCase):
    def test_title(self):
        actual = ndl.create_title_from_strings(
            'ほげ = FUGA = POYO : みょーん : ほっほ = HOHHO',
            'ホゲ : ミョーン : ホッホ')
        expected = Title(
            name='ほげ',
            transcription='ホゲ',
            parallels=['FUGA', 'POYO'],
            related_information=[
                TitleElement(
                    name='みょーん',
                    transcription='ミョーン',
                    parallels=[]),
                TitleElement(
                    name='ほっほ',
                    transcription='ホッホ',
                    parallels=['HOHHO'])
            ])
        self.assertEqual(expected, actual)

    def test_series(self):
        actual = ndl.create_series_from_strings(
            'ほげ文庫 = HOGE BUNKO ; 1111. ふが',
            'ホゲ ブンコ ; 1111. フガ')
        expected = [
            Series(
                number='1111',
                title=Title(
                    name='ほげ文庫',
                    transcription='ホゲ ブンコ',
                    related_information=[],
                    parallels=['HOGE BUNKO']
                )),
            Series(
                number=None,
                title=Title(
                    name='ふが',
                    transcription='フガ',
                    related_information=[],
                    parallels=[]
                )),
        ]
        self.assertEqual(expected, actual)

    def test_dcteerms_creator(self):
        actual = ndl.create_creator_from_dcterms_creator(
            '近藤, せいきち, 1989-',
            'コンドウ, セイキチ')
        expected = Creator(
            '近藤せいきち',
            'コンドウ セイキチ',
            None,
            '1989',
            None)
        self.assertEqual(expected, actual)

    def test_dc_creator(self):
        actual = ndl.create_creators_from_dc_creator(
            '近藤せいきち, ほげふが太郎 [著]', [
                ndl.create_creator_from_dcterms_creator(
                    '近藤, せいきち, 1989-', 'コンドウ, セイキチ')])
        expected = [
            Creator('近藤せいきち', 'コンドウ セイキチ', '著', '1989', None),
            Creator('ほげふが太郎', None, '著', None, None)]
        self.assertEqual(expected, actual)

#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import requests
from .util import isbn10to13, isbn13to10
from .metadata import Metadata, Title, Creator, Volume, Series
from .metadata import TitleElement, Publisher


def metadata_from_isbn(isbn, application_id):
    isbn = isbn.replace('-', '')
    if len(isbn) == 10:
        isbn10, isbn13 = isbn, isbn10to13(isbn)
    else:
        isbn10, isbn13 = isbn13to10(isbn), isbn

    URL = 'https://app.rakuten.co.jp/services/api/BooksBook/Search/20130522'
    params = {'isbn': isbn, 'applicationId': application_id}
    response = requests.get(URL, params=params)
    data = response.json()
    if 'error' in data or data['count'] == 0:
        return Metadata()
    item = data['Items'][0]['Item']

    creators = creators_from_strings(
        item.get('author', ''), item.get('authorKana', ''))
    title, volume = title_and_volume_from_strings(
        item.get('title', ''), item.get('titleKana', ''))
    series = series_from_strings(
        item.get('seriesName'), item.get('seriesNameKana'))
    description = item.get('itemCaption', '') or None
    thumbnails = thumbnails_from_item(item)
    price = price_from_string(item.get('itemPrice'))
    date = date_from_string(item.get('salesDate'))
    identifiers = {'ISBN10': isbn10, 'ISBN13': isbn13}
    publishers = [Publisher(item.get('publisherName'), None, None)]
    links = [item.get('itemUrl')]

    if item.get('subtitle'):
        subtitle, _ = title_and_volume_from_strings(
            item.get('subtitle'), item.get('subtitleKana'))
        title.related_information.append(TitleElement(
            name=subtitle.name,
            transcription=subtitle.transcription,
            parallels=[]))

    return Metadata(
        title=title,
        volume=volume,
        creators=creators,
        series=series,
        description=description,
        thumbnails=thumbnails,
        price=price,
        published_date=date,
        identifiers=identifiers,
        publishers=publishers,
        links=links)


def metadata_from_magazine_code(jan, application_id):
    URL = 'https://app.rakuten.co.jp/services/api/BooksMagazine/Search/20130522'
    params = {'jan': jan, 'applicationId': application_id}
    response = requests.get(URL, params=params)
    data = response.json()
    if 'error' in data or data['count'] == 0:
        return Metadata()
    item = data['Items'][0]['Item']

    title = Title(item.get('title', ''), item.get('titleKana', ''), [], [])
    description = item.get('itemCaption', '') or None
    thumbnails = thumbnails_from_item(item)
    price = price_from_string(item.get('itemPrice'))
    date = date_from_string(item.get('salesDate'))
    identifiers = {'EAN': jan}
    publishers = [Publisher(item.get('publisherName'), None, None)]
    links = [item.get('itemUrl')]
    return Metadata(
        title=title,
        description=description,
        thumbnails=thumbnails,
        price=price,
        published_date=date,
        identifiers=identifiers,
        publishers=publishers,
        links=links)


def price_from_string(price):
    # 楽天のAPI結果には消費税が追加されている
    return str(int(int(price) / 1.05))


def date_from_string(sales_date):
    date = '-'.join(x for x in re.split(r'\D+', sales_date) if x)
    date = date or None
    return date


def thumbnails_from_item(item):
    thumbnails = {}
    for size in ('small', 'medium', 'large'):
        thumbnails[size] = item.get(size + 'ImageUrl', None)
    return thumbnails


def series_from_strings(series, series_kana):
    if series:
        return [Series(title=Title(series, series_kana, [], []), number=None)]
    return []


def title_and_volume_from_strings(title, title_kana):
    # 注: 巻次は全角丸括弧で囲まれている
    NO_PAREN = r'[^\（\）]'
    # 入れ子は一重まで許可
    volume_title_pattern = re.compile(
        r'\（({0}+(\（{0}*\）{0}*)*)\）$'.format(NO_PAREN), re.U)
    value_match = volume_title_pattern.search(title)
    if value_match is None:
        volume = None
    else:
        volume = Volume(value_match.groups()[0], None)

    title = volume_title_pattern.sub('', title)
    return Title(title, title_kana, [], []), volume


def creators_from_strings(author, author_kana):
    creators = []
    for name, transcription in zip(author.split('/'),
                                   author_kana.split('/')):
        creators.append(Creator(
            name,
            ' '.join(transcription.split(',')),
            None, None, None))
    return creators


if __name__ == '__main__':
    import json
    import argparse
    from .util import namedtuple2dict
    parser = argparse.ArgumentParser(
        description='find book metadata from Rakuten')
    parser.add_argument('--application-id', action='store', dest='application_id',
                        required=True)
    parser.add_argument('--isbn', action="store", dest="isbn")
    parser.add_argument('--magazine', action="store", dest="jan")
    parser.add_argument('--delete-false-items', action='store_true',
                        dest='delete_false_items')
    args = parser.parse_args()
    metadata = Metadata()
    if args.isbn:
        metadata = metadata_from_isbn(args.isbn, args.application_id)
    elif args.jan:
        metadata = metadata_from_magazine_code(args.jan, args.application_id)
    print(json.dumps(namedtuple2dict(metadata, args.delete_false_items),
                     ensure_ascii=False))

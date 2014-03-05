#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import division, print_function
from __future__ import absolute_import, unicode_literals

import re
import requests
import mwparserfromhell
import unicodedata
import itertools
from .util import isbn10to13, isbn13to10
from .metadata import Metadata, Series, Title


def make_search_keyword_from_isbn(isbn):
    '''与えられた ISBN (isbn) で wikipedia のページを検索するためのクエリを作成する'''
    # ハイフン等(-)を一旦削除
    isbn = re.sub(r'[^xX\d]', '', isbn)
    # wikipedia のページには ISBN10 や ISBN13 が入り交じっている
    if len(isbn) == 10:
        isbn10 = isbn
        isbn13 = isbn10to13(isbn10)
    elif len(isbn) == 13:
        isbn13 = isbn
        isbn10 = isbn13to10(isbn13)
    else:
        return None

    # wikipedia のページに書かれている ISBN には，ハイフンの入れ方が数パターンある模様
    candidates = [
        re.sub(r'(\d)(\d{4})(\d{4})(\d|X)', r'\1-\2-\3-\4', isbn10),
        re.sub(r'(\d)(\d{2})(\d{6})(\d|X)', r'\1-\2-\3-\4', isbn10),
        re.sub(r'(\d{3})(\d)(\d{2})(\d{6})(\d)', r'\1-\2-\3-\4-\5', isbn13),
        re.sub(r'(\d{3})(\d)(\d{4})(\d{4})(\d)', r'\1-\2-\3-\4-\5', isbn13),
    ]
    # 全てを OR でまとめてクエリ完成
    return ' OR '.join('"ISBN {0}"'.format(c) for c in candidates)


def find_page_about_series(isbn):
    '''与えられたISBN (isbn) が指す書籍のシリーズに関係する Wikipedia のページを取得する'''
    URL = 'http://ja.wikipedia.org/w/api.php'
    # ISBN を用いて Wikipedia のページを検索し，ページのタイトルを取得
    search_keyword = make_search_keyword_from_isbn(isbn)
    res = requests.get(URL, params={
        'format': 'json',
        'action': 'query',
        'list': 'search',
        'srsearch': search_keyword,
        'srprop': 'timestamp',
    })
    # 面倒なので最大5タイトルしか調べない方向で
    titles = [page['title'] for page in res.json()['query']['search']][:5]

    # "hogehogeシリーズ" というタイトルのページがあるならそちらを優先する
    # NOTE: 有名な小説や漫画のシリーズだと単巻ごとにページが存在することがある
    for title in itertools.chain((title for title in titles if title.endswith('シリーズ')),
                                 (title for title in titles if not title.endswith('シリーズ'))):
        res = requests.get(URL, params={
            'format': 'json',
            'action': 'query',
            'titles': title,
            'prop': 'revisions',
            'rvprop': 'content',
        })
        # Infobox animanga を含まなければ無視
        try:
            response_data = res.json()
            pages = response_data['query']['pages']
            content = list(pages.values())[0]['revisions'][0]['*']
            wikicode = mwparserfromhell.parse(content)
            if wikicode.filter_templates(matches=r'{{Infobox\s+animanga/(Novel|Manga)'):
                return wikicode, title
        except:
            pass
    return None, None


def metadata_from_isbn(isbn, title, authors):
    '''
    Wikipedia の API を利用して，与えられたISBN (isbn) が指す書籍のメタデータを取得する
    タイトルや著者情報が必要な理由はファンブックや解説書対策
    例:
      『化物語アニメコンプリートガイドブック ひたぎクラブ』のISBN (ISBN 978-4-06-216226-5) が
      「〈物語〉シリーズ」のページに含まれているが，この書籍を "〈物語〉シリーズ" 見なしたくない．
    '''
    authors_set = set([re.sub(r'\s', '', a) for a in authors])
    wikicode, page_title = find_page_about_series(isbn)

    if not wikicode:
        return Metadata()

    def remove_tags(code):
        for tag in code.ifilter_tags():
            code.remove(tag)
        return code

    def get_first_text(code):
        texts = remove_tags(code.value).filter_text()
        if not texts:
            return ''
        return texts[0].strip()

    def get_text_list(code):
        return [text.strip() for text in remove_tags(code.value).ifilter_text() if text.strip()]

    # Infobox animanga のヘッダを処理
    # ヘッダにタイトルが含まれていない場合は，ページ自身のタイトルをシリーズ名として利用する
    headers = wikicode.filter_templates(matches=r'^{{Infobox\s+animanga/Header')
    series_name = page_title
    genre = []
    if headers:
        header = headers[0]
        if header.has('タイトル'):
            series_name = get_first_text(header.get('タイトル'))
        if header.has('ジャンル'):
            genre = []
            genre_code = remove_tags(header.get('ジャンル').value)
            # # "[[サイエンス・フィクション|SF]]" というジャンルの場合
            # # "サイエンス・フィクション" だけ抜き出す => やめた
            # for link in genre_code.filter_wikilinks():
            #     genre.append(str(link.title).strip())
            #     genre_code.remove(link)
            for text in genre_code.filter_text():
                text = text.strip()
                if re.search(r'\w', text, re.U) is None:
                    continue
                text = re.sub(r'、|，', '', text, re.U)
                # "経済（商業・商取引・金融・流通 他）" で "他）"
                # がジャンルに含まれてしまう問題に場当たり的に対処...
                if (text.endswith('他）')):
                    continue
                genre.append(text)

    # Infobox animanga 内には，ノベライズやコミカライズ版の情報も入っている
    # これらの情報をそれぞれ adaptations に格納
    # adaptations を利用して，与えられたISBNが指し示す書籍が，どのシリーズに含まれるのか推測したい
    # 動機:
    #   「"文学少女" と死にたがりの道化【ピエロ】」のISBN (ISBN 4-7577-2806-9) で Wikipeida を検索
    # => "文学少女" シリーズ のページが出てくる
    # => Infobox animanga には小説と漫画4種類で計5作品の情報が入っている
    # => 与えられたISBNが指し示す書籍は一体どれに属するのだろう???
    adaptations = []
    for infobox in wikicode.ifilter_templates(matches=r'{{Infobox\s+animanga/([Mm]anga|[Nn]ovel)'):
        match = re.match(r'^Infobox\s+animanga/([Mm]anga|[Nn]ovel)', str(infobox.name))
        if match is None:
            continue
        adaptation_type = match.group(1).lower()
        # タイトルが明示されていれば，そちらを優先
        adaptation_title = series_name
        if infobox.has('タイトル'):
            adaptation_title = get_first_text(infobox.get('タイトル'))

        adaptation_authors = []
        for prop in ('作者', '作画', '著者', 'イラスト'):
            if not infobox.has(prop):
                continue
            adaptation_authors.extend(get_text_list(infobox.get(prop)))
        # 名前の後ろに必要ない情報があったりするので消しておく
        adaptation_authors = [re.sub(r'(\(.+\)$)|(（.+）$)|\s', '', author)
                              for author in adaptation_authors]
        adaptations.append({
            'type': adaptation_type,
            'title': adaptation_title,
            'authors': adaptation_authors,
        })

    def contais_adaptation_title(title, adaptation_title):
        # 括弧で囲まれた補足情報とか面倒なので消す
        pattern = re.compile(r'(\(.+?\))|(（.+?）)|(【.+?】)|\W')
        title = pattern.sub('', unicodedata.normalize('NFKC', title))
        # 末尾の「シリーズ」を削除
        adaptation_title = re.sub(r'シリーズ$', '', adaptation_title, re.U)
        adaptation_title = pattern.sub('', unicodedata.normalize('NFKC', adaptation_title))
        return title.find(adaptation_title) >= 0

    # まずは著者情報を確認．真部分集合でない場合は候補から除く
    adaptations = [ad for ad in adaptations if authors_set <= set(ad['authors'])]
    # # 引数のタイトルを含むシリーズ名があれば，それを優先
    # if any(contais_adaptation_title(title, ad['title']) for ad in adaptations):
    #     adaptations = [ad for ad in adaptations if contais_adaptation_title(title, ad['title'])]
    if not adaptations:
        return Metadata()
    # 一番著者情報が近そうなシリーズを採用
    adaptation = sorted(adaptations, key=lambda ad: len(set(ad['authors']) & authors_set))[0]

    metadata = Metadata(tags=genre, links=[
        'http://ja.wikipedia.org/wiki/' + requests.utils.quote(page_title)
    ])
    if adaptation['title'].endswith('シリーズ'):
        metadata.series.append(Series(
            title=Title(
                name=adaptation['title'],
                transcription=None,
                parallels=[],
                related_information=[]),
            number=None))
    return metadata


if __name__ == '__main__':
    import json
    import argparse
    from . import ndl

    parser = argparse.ArgumentParser(
        description='find book metadata from Wikipedia')
    parser.add_argument('--isbn', action="store", dest="isbn", required=True)
    args = parser.parse_args()
    metadata = ndl.metadata_from_isbn(args.isbn)

    wikipedia_metadata = Metadata()
    if metadata.title:
        wikipedia_metadata = metadata_from_isbn(
            args.isbn,
            metadata.title.name,
            [c.name for c in metadata.creators])
    print(json.dumps(wikipedia_metadata.todict(), ensure_ascii=False))

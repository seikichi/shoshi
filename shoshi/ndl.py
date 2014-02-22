#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import requests
import lxml.objectify
from .metadata import Metadata, Title, TitleElement, Creator
from .metadata import Publisher, Series, Volume, Content
from .util import isbn13to10, isbn10to13, normalize


def create_metadata_from_xml_root(root):
    return Metadata(
        title=create_title_from_root(root),
        volume=create_volume_from_root(root),
        creators=create_creators_from_root(root),
        series=create_series_from_root(root),
        publishers=create_publishers_from_root(root),
        contents=create_contents_from_root(root),
        identifiers=create_identifiers_from_root(root),
        price=price_from_root(root),
        page_count=page_count_from_root(root),
        published_date=published_date_from_root(root),
        links=links_from_root(root),
        tags=tags_from_root(root))


def tags_from_root(root):
    tags = []
    for sub in root.xpath('//dcterms:subject/rdf:Description/rdf:value/text()',
                          namespaces=root.nsmap):
        tags.extend(sub.split('--'))
    return tags


def links_from_root(root):
    return root.xpath('//dcndl:BibAdminResource/@rdf:about', namespaces=root.nsmap)


def published_date_from_root(root):
    for d in root.xpath('//dcterms:date//text()', namespaces=root.nsmap):
        if re.match(r'(\d+)(.\d+)*', d):
            return '-'.join(x for x in re.split(r'\D+', d) if d)
    return None


def price_from_root(root):
    prices = root.xpath('//dcndl:price//text()', namespaces=root.nsmap)
    if len(prices) == 0:
        return None
    return normalize(re.sub(r'\D', '', prices[0])) if len(prices) != 0 else None


def page_count_from_root(root):
    for es in root.xpath('//dcterms:extent//text()', namespaces=root.nsmap):
        for e in es.split(' ; '):
            if re.match(r'\d+p', e):
                return re.sub(r'\D', '', e)
    return None


def create_title_from_root(root):
    title_value_elem = root.find(
        'dcndl:BibResource/dc:title/rdf:Description/rdf:value', root.nsmap)
    title_value_elem = (title_value_elem if title_value_elem is not None
                        else root.find('dcndl:BibResource/dcterms:title',
                                       root.nsmap))
    title_value = title_value_elem.text if title_value_elem is not None else ''
    title_transcription_elem = root.find(
        'dcndl:BibResource/dc:title/rdf:Description/dcndl:transcription',
        root.nsmap)
    title_transcription = (title_transcription_elem.text
                           if title_transcription_elem is not None else '')
    title = create_title_from_strings(title_value, title_transcription)

    parallel_candidates = (alternatives_from_root(root) +
                           descriptions_from_root(root))
    for p in parallel_candidates:
        if p.startswith('並列タイトル:') or p.startswith('原タイトル:'):
            for parallel in map(str.strip, p.split(':')[1:]):
                if parallel not in title.parallels:
                    title.parallels.append(parallel)
    return title


def create_publishers_from_root(root):
    publishers = []
    for agent in root.xpath('dcndl:BibResource/dcterms:publisher/foaf:Agent',
                            namespaces=root.nsmap):
        name_elem = agent.find('foaf:name', root.nsmap)
        transcription_elem = agent.find('dcndl:transcription', root.nsmap)
        location_elem = agent.find('dcndl:location', root.nsmap)
        name = name_elem.text if name_elem is not None else None
        transcription = (transcription_elem.text
                         if transcription_elem is not None else None)
        location = location_elem.text if location_elem is not None else None
        if not name:
            continue
        publishers.append(Publisher(name=name,
                                    transcription=transcription,
                                    location=location))
    return publishers


def create_volume_from_root(root):
    volume_value_elem = root.find(
        'dcndl:BibResource/dcndl:volume/rdf:Description/rdf:value',
        root.nsmap)
    value = volume_value_elem.text if volume_value_elem is not None else ''
    volume_transcription_elem = root.find(
        'dcndl:BibResource/dcndl:volume/rdf:Description/dcndl:transcription',
        root.nsmap)
    transcription = (volume_transcription_elem.text
                     if volume_transcription_elem is not None else '')
    volume = create_volume_from_strings(value, transcription)

    # if volume.title is not None:
    #     for p in descriptions_from_root(root) + alternatives_from_root(root):
    #         if p.startswith('各巻の並列タイトル:'):
    #             for parallel in map(str.strip, p.split(':')[1:]):
    #                 if parallel not in volume.title.parallels:
    #                     volume.title.parallels.append(parallel)
    return volume


def create_dcterms_creators_from_root(root):
    dcterms_creators = []
    for creator in root.xpath('dcndl:BibResource/dcterms:creator',
                              namespaces=root.nsmap):
        name_elem = creator.find('.//foaf:name', root.nsmap)
        transcription_elem = creator.find('.//dcndl:transcription', root.nsmap)
        name = (normalize(re.sub(r'\s+', '', name_elem.text))
                if name_elem is not None else '')
        transcription = (transcription_elem.text
                         if transcription_elem is not None else '')
        dcterms_creators.append(
            create_creator_from_dcterms_creator(name, transcription))
    return dcterms_creators


def create_creators_from_root(root):
    dcterms_creators = create_dcterms_creators_from_root(root)
    creators = []
    for creator in root.xpath('dcndl:BibResource/dc:creator/text()',
                              namespaces=root.nsmap):
        creators.extend(
            create_creators_from_dc_creator(creator, dcterms_creators))

    for p in descriptions_from_root(root):
        if p.startswith('イラスト:'):
            name = re.sub(r'\s+', '', p.split(':', maxsplit=1)[1].strip())
            creators.append(Creator(name=name, transcription=None, role='イラスト',
                                    date_of_birth=None, date_of_death=None))
    return creators


def create_series_from_root(root):
    series_description_elem = root.find(
        'dcndl:BibResource/dcndl:seriesTitle/rdf:Description', root.nsmap)
    if series_description_elem is None:
        return []
    value_elem = series_description_elem.find('rdf:value', root.nsmap)
    transcription_elem = series_description_elem.find('dcndl:transcription',
                                                      root.nsmap)
    value = value_elem.text if value_elem is not None else ''
    transcription = (transcription_elem.text
                     if transcription_elem is not None else '')
    series = create_series_from_strings(value, transcription)

    if len(series) == 1:
        for p in descriptions_from_root(root) + alternatives_from_root(root):
            if p.startswith('並列シリーズ名:'):
                for parallel in map(str.strip, p.split(':')[1:]):
                    if parallel not in series[0].title.parallels:
                        series[0].title.parallels.append(parallel)
    return series


def create_contents_from_root(root):
    contents = []
    dcterms_creators = create_dcterms_creators_from_root(root)
    for desc in root.xpath('//dcndl:partInformation//rdf:Description',
                           namespaces=root.nsmap):
        title_elem = desc.find('dcterms:title', root.nsmap)
        transcription_elem = desc.find('dcndl:transcription', root.nsmap)
        title = title_elem.text if title_elem is not None else None
        transcription = transcription_elem.text if transcription_elem else None
        creators = desc.xpath('./dc:creator/text()', namespaces=root.nsmap)
        if not title:
            continue
        contents.append(create_content_from_strings(
            title,
            transcription,
            creators,
            dcterms_creators))
    return contents


def create_identifiers_from_root(root):
    identifiers = {}
    path = ('//dcterms:identifier' +
            '[@rdf:datatype="http://ndl.go.jp/dcndl/terms/ISBN"]//text()')
    for isbn in root.xpath(path, namespaces=root.nsmap):
        isbn = re.sub(r'-', '', isbn)
        if len(isbn) == 10:
            identifiers['ISBN10'] = isbn
            identifiers['ISBN13'] = isbn10to13(isbn)
        if len(isbn) == 13:
            identifiers['ISBN13'] = isbn
            identifiers['ISBN10'] = isbn13to10(isbn)
    path = ('//dcterms:identifier' +
            '[@rdf:datatype="http://ndl.go.jp/dcndl/terms/JPNO"]//text()')
    for jpno in root.xpath(path, namespaces=root.nsmap):
        identifiers['JPNO'] = jpno
    return identifiers


def create_title_from_strings(value, transcription):
    value = normalize(value or '')
    transcription = normalize(transcription or '')
    titles = []
    related_delimiter = ' : '
    parallel_delimiter = ' = '
    for v, t in zip(value.split(related_delimiter),
                    transcription.split(related_delimiter)):
        parallels = v.split(parallel_delimiter)
        v, p = parallels[0], parallels[1:]
        titles.append({'value': v, 'transcription': t, 'parallels': p})
    title_elements = [
        TitleElement(name=t['value'],
                     transcription=t['transcription'],
                     parallels=t['parallels'])
        for t in titles]
    main, related_information = title_elements[0], title_elements[1:]
    return Title(
        name=main.name,
        transcription=main.transcription,
        parallels=main.parallels,
        related_information=related_information)


def create_series_from_strings(value, transcription):
    value = normalize(value or '')
    transcription = normalize(transcription or '')
    series = []
    series_delimiter = '. '
    number_delimiter = ' ; '
    for v, t in zip(value.split(series_delimiter),
                    transcription.split(series_delimiter)):
        number = None
        if v.find(number_delimiter) >= 0:
            v, number = v.split(number_delimiter)
            t = t.split(number_delimiter)[0]
        if t.find(number_delimiter) >= 0:
            t, number = t.split(number_delimiter)
        title = create_title_from_strings(v, t)
        series.append(Series(title=title, number=number))
    return series


def create_volume_from_strings(value, transcription):
    # # 巻次タイトルには括弧() の入れ子を一重まで許可する
    # NO_PAREN = r'[^\(\)]'
    # volume_title_pattern = re.compile(
    #     r'\(({0}+(\({0}*\){0}*)*)\)$'.format(NO_PAREN), re.U)
    # value_match = volume_title_pattern.search(value)
    # transcription_match = volume_title_pattern.search(transcription)
    # title = None
    # if (value_match is not None) and (transcription_match is not None):
    #     title = create_title_from_strings(value_match.groups()[0],
    #                                       transcription_match.groups()[0])
    #     value = value[:value_match.start()].strip()
    #     transcription = transcription[:transcription_match.start()].strip()
    # elif value_match is not None:
    #     value = value[:value_match.start()].strip()
    #     if transcription.startswith(value):
    #         # value = "1 (ほげ)", transcription = "1 ホゲ"
    #         volume_title_transcription = transcription[len(value):].strip()
    #         title = create_title_from_strings(value_match.groups()[0],
    #                                           volume_title_transcription)
    #         transcription = transcription[:len(value)]
    #     else:
    #         title = create_title_from_strings(value_match.groups()[0], '')
    # return Volume(name=value, transcription=transcription, title=title)
    value = normalize(value or '')
    transcription = normalize(transcription or '')
    if not value:
        return None
    if transcription == '':
        transcription = None
    return Volume(name=value, transcription=transcription)


def create_creators_from_dc_creator(value, dcterms_creators):
    role_pattern = re.compile(
        r'(?: |／)' +
        r'(?:\[ほか\])?' +
        r'(?P<bracket>\[|\［)?' +
        r'(?P<role>[一-龠ぁ-んァ-ヶ]+?)' +
        r'(?(bracket)(?:\]|\］))$', re.U)
    role_match = role_pattern.search(value)
    role = None
    if role_match is not None:
        role = role_match.group('role')
        value = role_pattern.sub('', value)
    name_delimiter = ', '
    creators = []
    for v in value.split(name_delimiter):
        v = re.sub(r'\s+', '', normalize(v))
        transcription = None
        date_of_birth = None
        date_of_death = None
        for c in dcterms_creators:
            if c.name == v:
                transcription = c.transcription
                date_of_birth = c.date_of_birth
                date_of_death = c.date_of_death
                break
        transcription = None if transcription == '' else transcription
        creators.append(Creator(
            name=normalize(v).replace(' ', ''),
            transcription=normalize(transcription),
            role=normalize(role),
            date_of_birth=date_of_birth,
            date_of_death=date_of_death))
    return creators


def create_creator_from_dcterms_creator(name, transcription):
    name, transcription = normalize(name), normalize(transcription)
    name_pattern = re.compile(
        r'^(?P<name>.+?)' +
        r'(, (?P<date_of_birth>\d{4})-(?P<date_of_death>\d{4})?)?$',
        re.U)
    name_delimiter_pattern = re.compile(r'‖|,\s*')
    match = name_pattern.match(name)
    if match is None:
        return Creator(name, transcription, '', '', '')
    return Creator(
        name=name_delimiter_pattern.sub('', match.group('name')),
        transcription=' '.join(name_delimiter_pattern.split(transcription)),
        role=None,
        date_of_birth=match.group('date_of_birth'),
        date_of_death=match.group('date_of_death'))


def create_content_from_strings(title, transcription,
                                creators, dcterms_creators):
    cs = []
    for c in creators:
        cs.extend(create_creators_from_dc_creator(c, dcterms_creators))
    return Content(
        title=create_title_from_strings(title, transcription),
        creators=cs
    )


def alternatives_from_root(root):
    return root.xpath(
        'dcndl:BibResource/dcndl:alternative/rdf:Description/rdf:value/text()',
        namespaces=root.nsmap)


def descriptions_from_root(root):
    return root.xpath(
        'dcndl:BibResource/dcterms:description/text()',
        namespaces=root.nsmap)


def metadata_from_jpno(jpno):
    URL = 'http://iss.ndl.go.jp/api/opensearch'
    jpno = re.sub(r'-', '', normalize(jpno))
    response = requests.get(URL, params={'jpno': jpno})
    return metadata_from_opensearch_response(response)


def metadata_from_isbn(isbn):
    URL = 'http://iss.ndl.go.jp/api/opensearch'
    isbn = re.sub(r'-', '', normalize(isbn))
    if len(isbn) == 10:
        isbn = isbn10to13(isbn)
    response = requests.get(URL, params={'isbn': isbn})
    return metadata_from_opensearch_response(response)


def metadata_from_opensearch_response(response):
    root = lxml.objectify.fromstring(response.content)
    item = None
    # 国立国会図書館を優先
    bib_record_categories = ['R100000002', 'R100000001']
    for category in bib_record_categories:
        for it in getattr(root.channel, 'item', []):
            if it.link.text.startswith('http://iss.ndl.go.jp/books/' +
                                       category):
                item = it
        if item is not None:
            break
    else:
        item = getattr(root.channel, 'item', None)
    if item is None:
        return Metadata()
    dcndl_rdf_url = item.guid.text + '.rdf'
    response = requests.get(dcndl_rdf_url)
    return create_metadata_from_xml_root(
        lxml.objectify.fromstring(response.content))


if __name__ == '__main__':
    import json
    import argparse
    from .util import namedtuple2dict
    parser = argparse.ArgumentParser(description='find book metadata from NDL')
    parser.add_argument('--isbn', action="store", dest="isbn")
    parser.add_argument('--jpno', action="store", dest="jpno")
    parser.add_argument('--delete-false-items', action='store_true',
                        dest='delete_false_items')
    args = parser.parse_args()
    metadata = Metadata()
    if args.isbn:
        metadata = metadata_from_isbn(args.isbn)
    elif args.jpno:
        metadata = metadata_from_jpno(args.jpno)
    print(json.dumps(namedtuple2dict(metadata, args.delete_false_items),
                     ensure_ascii=False))

#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import bottlenose
from lxml import objectify
import lxml.html
from .util import isbn10to13, isbn13to10, normalize
from .metadata import Metadata, Title, Creator, Publisher
from .metadata import Volume
from .amazon_magazine import parse_magazine_title


def normalize_author(author):
    return re.sub(r'\s+', '', normalize(author))


def metadata_from_asin(ASIN, access_key_id, secret_access_key, associate_tag):
    return metadata_from_ean(ASIN,
                             access_key_id,
                             secret_access_key,
                             associate_tag)


def metadata_from_ean(EAN, access_key_id, secret_access_key, associate_tag):
    EAN = EAN.replace('-', '')
    if re.match(r'^\d{9}(\d|X|x)$', EAN):
        EAN = isbn10to13(EAN)

    try:
        amazon = bottlenose.Amazon(str(access_key_id),
                                   str(secret_access_key),
                                   str(associate_tag), Region='JP')
        root = objectify.fromstring(amazon.ItemLookup(
            ItemId=EAN,
            SearchIndex='Books',
            IdType='ISBN',
            ResponseGroup='EditorialReview,Images,ItemAttributes'))
    except:
        return Metadata()

    if not hasattr(root.Items, 'Item'):
        return Metadata()

    # Kindle 版ではなく紙媒体を優先する
    Item = None
    for _Item in root.Items.Item:
        binding = getattr(_Item.ItemAttributes, 'Binding', None)
        binding = binding.text if binding else ''
        if binding.lower().startswith('kindle'):
            Item = _Item
    else:
        Item = root.Items.Item

    # 各種メタデータ取得
    identifiers = {'ASIN': Item.ASIN.text}
    title_elem = getattr(Item.ItemAttributes, 'Title', None)
    title = (Title(normalize(title_elem.text), None, [], [])
             if title_elem else None)
    published_date_elem = getattr(Item.ItemAttributes, 'PublicationDate', '')
    published_date = published_date_elem.text if published_date_elem else None
    price = None
    list_price_elem = getattr(Item.ItemAttributes, 'ListPrice', None)
    if list_price_elem is not None:
        price = str(int(int(list_price_elem.Amount.text) / 1.05))
    page_count = str(getattr(Item.ItemAttributes, 'NumberOfPages', '')) or None

    creators = []
    for author in getattr(root.Items.Item.ItemAttributes, 'Author', []):
        creators.append(Creator(name=normalize_author(author.text),
                                transcription=None, role='著',
                                date_of_birth=None,
                                date_of_death=None))
    for creator in getattr(root.Items.Item.ItemAttributes, 'Creator', []):
        creators.append(Creator(name=normalize_author(creator.text),
                                transcription=None,
                                role=creator.get('Role', '著'),
                                date_of_birth=None,
                                date_of_death=None))

    thumbnails = {}
    for size in ('small', 'medium', 'large'):
        field = size.title() + 'Image'
        if hasattr(Item, field):
            thumbnails[size] = getattr(Item, field).URL.text

    if hasattr(Item.ItemAttributes, 'ISBN'):
        ISBN = Item.ItemAttributes.ISBN.text
        if len(ISBN) == 10:
            identifiers['ISBN10'] = ISBN
            identifiers['ISBN13'] = isbn10to13(ISBN)
        elif len(ISBN) == 13:
            identifiers['ISBN10'] = isbn13to10(ISBN)
            identifiers['ISBN13'] = ISBN
    if hasattr(Item.ItemAttributes, 'EAN'):
        identifiers['EAN'] = Item.ItemAttributes.EAN.text

    publishers = []
    for p in getattr(Item.ItemAttributes, 'Publisher', []):
        publishers.append(Publisher(name=p.text,
                                    transcription=None, location=None))

    # Editorial Review を取得する (こちらは Kindle の方にしか無いことが多い ...)
    description = None
    content_cand = root.xpath('//ns:EditorialReviews//ns:Content[1]//text()',
                              namespaces={'ns': root.nsmap[None]})
    if content_cand:
        description = lxml.html.fromstring(content_cand[0]).text_content()

    links = ['http://www.amazon.co.jp/dp/{0}'.format(identifiers['ASIN'])]

    volume = None
    magazine_metadata = parse_magazine_title(title.name)
    if magazine_metadata.get('title'):
        title = Title(magazine_metadata.get('title'),
                      None,
                      parallels=[],
                      related_information=[])
        # if magazine_metadata.get('subtitle'):
        #     title.related_information.append(TitleElement(
        #         name=magazine_metadata.get('subtitle'),
        #         transcription=None,
        #         parallels=[]))
    if magazine_metadata.get('volume'):
        volume = Volume(magazine_metadata.get('volume'), None)

    return Metadata(
        title=title,
        volume=volume,
        identifiers=identifiers,
        creators=creators,
        thumbnails=thumbnails,
        published_date=published_date,
        publishers=publishers,
        price=price,
        description=description,
        page_count=page_count,
        links=links)


if __name__ == '__main__':
    import json
    import argparse
    parser = argparse.ArgumentParser(
        description='find book metadata from Amazon')
    parser.add_argument('--ean', action="store", dest="ean")
    parser.add_argument('--asin', action="store", dest="asin")
    parser.add_argument('--amazon-auth-info', action="store",
                        dest="amazon_auth_info", required=True)
    parser.add_argument('--include-null-value-field', action='store_true',
                        dest='include_none_value_field')
    args = parser.parse_args()
    metadata = Metadata()
    if args.ean:
        metadata = metadata_from_ean(
            args.ean, *re.split(r',\s*', args.amazon_auth_info))
    elif args.asin:
        metadata = metadata_from_asin(
            args.asin, *re.split(r',\s*', args.amazon_auth_info))
    print(json.dumps(metadata.todict(args.include_none_value_field),
                     ensure_ascii=False))

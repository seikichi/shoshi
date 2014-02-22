#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import namedtuple

Title = namedtuple('Title', ['name', 'transcription',
                             'parallels', 'related_information'])
TitleElement = namedtuple('TitleElement', ['name', 'transcription', 'parallels'])
Publisher = namedtuple('Publisher', ['name', 'transcription', 'location'])
Series = namedtuple('Series', ['title', 'number'])
Volume = namedtuple('Volume', ['name', 'transcription'])
Creator = namedtuple('Creator', ['name', 'transcription', 'role',
                                 'date_of_birth', 'date_of_death'])
Content = namedtuple('Content', ['title', 'creators'])
_Metadata = namedtuple('Metadata', [
    'title',
    'volume',
    'series',
    'publishers',
    'creators',
    'contents',
    'identifiers',
    'description',
    'tags',
    'thumbnails',
    'price',
    'published_date',
    'page_count',
    'links'
])


class Metadata(_Metadata):
    def __new__(klass,
                title=None,
                volume=None,
                series=[],
                publishers=[],
                creators=[],
                contents=[],
                identifiers={},
                description=None,
                tags=[],
                thumbnails={},
                price=None,
                published_date=None,
                page_count=None,
                links=[]):
        return super(Metadata, klass).__new__(
            klass,
            title,
            volume,
            series,
            publishers,
            creators,
            contents,
            identifiers,
            description,
            tags,
            thumbnails,
            price,
            published_date,
            page_count,
            links)

#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import namedtuple, Mapping


class Title(namedtuple('Title', ['name', 'transcription',
                                 'parallels', 'related_information'])):
    def __new__(klass, name, transcription=None,
                parallels=[], related_information=[]):
        return super(Title, klass).__new__(klass, name, transcription,
                                           parallels, related_information)


class TitleElement(namedtuple('TitleElement', [
        'name', 'transcription', 'parallels'])):
    def __new__(klass, name, transcription=None, parallels=[]):
        return super(TitleElement, klass).__new__(
            klass, name, transcription, parallels)


class Publisher(namedtuple('Publisher', ['name', 'transcription', 'location'])):
    def __new__(klass, name, transcription=None, location=None):
        return super(Publisher, klass).__new__(
            klass, name, transcription, location)


class Volume(namedtuple('Volume', ['name', 'transcription'])):
    def __new__(klass, name, transcription=None):
        return super(Volume, klass).__new__(klass, name, transcription)


class Creator(namedtuple('Creator', ['name', 'transcription', 'role',
                                     'date_of_birth', 'date_of_death'])):
    def __new__(klass,
                name,
                transcription=None,
                role=None,
                date_of_birth=None,
                date_of_death=None):
        return super(Creator, klass).__new__(
            klass, name, transcription, role,
            date_of_birth, date_of_death)


class Content(namedtuple('Content', ['title', 'creators'])):
    def __new__(klass, title, creators=[]):
        return super(Content, klass).__new__(klass, title, creators)


class Series(namedtuple('Series', ['title', 'number'])):
    def __new__(klass, title, number=None):
        return super(Series, klass).__new__(klass, title, number)


class Metadata(namedtuple('Metadata', [
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
        'links'])):
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

    def todict(self, include_none_value_field=True, to_camel_case=True):
        return namedtuple2dict(self, include_none_value_field, to_camel_case)


def snake2camel(snake_str):
    components = snake_str.split('_')
    return components[0] + "".join(x.title() for x in components[1:])


def namedtuple2dict(o, include_none_value_field, to_camel_case):
    if hasattr(o, '_asdict'):
        return namedtuple2dict(o._asdict(),
                               include_none_value_field,
                               to_camel_case)
    elif isinstance(o, (set, list)):
        return [namedtuple2dict(item,
                                include_none_value_field,
                                to_camel_case)
                for item in o]
    elif isinstance(o, Mapping):
        pairs = []
        for key in o:
            value = namedtuple2dict(o[key],
                                    include_none_value_field,
                                    to_camel_case)
            if to_camel_case:
                key = snake2camel(key)
            pairs.append((key, value))
        d = dict(pairs)
        if include_none_value_field:
            delete_keys = [k for k in d if d[k] is None]
            for k in delete_keys:
                d.pop(k)
        return d
    else:
        return o

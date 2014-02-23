#!/usr/bin/python
# -*- coding: utf-8 -*-


class Title(object):
    def __init__(self, name, transcription=None,
                 parallels=[], related_information=[]):
        self.name = name
        self.transcription = transcription
        self.parallels = parallels
        self.related_information = related_information


class TitleElement(object):
    def __init__(self, name, transcription=None, parallels=[]):
        self.name = name
        self.transcription = transcription
        self.parallels = parallels


class Publisher(object):
    def __init__(self, name, transcription=None, location=None):
        self.name = name
        self.transcription = transcription
        self.location = location


class Volume(object):
    def __init__(self, name, transcription=None):
        self.name = name
        self.transcription = transcription


class Creator(object):
    def __init__(self,
                 name,
                 transcription=None,
                 role=None,
                 date_of_birth=None,
                 date_of_death=None):
        self.name = name
        self.transcription = transcription
        self.role = role
        self.date_of_birth = date_of_birth
        self.date_of_death = date_of_death


class Content(object):
    def __init__(self, title, creators=[]):
        self.title = title
        self.creators = creators


class Series(object):
    def __init__(self, title, number=None):
        self.title = title
        self.number = number


class Metadata(object):
    def __init__(self,
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
        self.title = title
        self.volume = volume
        self.series = series
        self.publishers = publishers
        self.creators = creators
        self.contents = contents
        self.identifiers = identifiers
        self.description = description
        self.tags = tags
        self.thumbnails = thumbnails
        self.price = price
        self.published_date = published_date
        self.page_count = page_count
        self.links = links

    def todict(self, include_none_value_field=True, to_camel_case=True):
        return object2dict(self, include_none_value_field, to_camel_case)


def snake2camel(snake_str):
    components = snake_str.split('_')
    return components[0] + "".join(x.title() for x in components[1:])


def object2dict(o, include_none_value_field, to_camel_case):
    if hasattr(o, '__dict__'):
        return object2dict(o.__dict__,
                           include_none_value_field,
                           to_camel_case)
    elif isinstance(o, (list, set)):
        return [object2dict(item, include_none_value_field, to_camel_case)
                for item in o]
    elif isinstance(o, dict):
        pairs = []
        for key in o:
            value = object2dict(o[key], include_none_value_field, to_camel_case)
            if to_camel_case:
                key = snake2camel(key)
            pairs.append((key, value))
        d = dict(pairs)
        if not include_none_value_field:
            delete_keys = [k for k in d if d[k] is None]
            for k in delete_keys:
                d.pop(k)
        return d
    else:
        return o

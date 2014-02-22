#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import division, print_function
from __future__ import absolute_import, unicode_literals

import json
import argparse
import sys
import os

path = os.path.dirname(sys.modules[__name__].__file__)
path = os.path.join(path, '..')
sys.path.insert(0, path)

from .__init__ import metadata_from_isbn, metadata_from_ean, metadata_from_jpno
from .util import namedtuple2dict
from .metadata import Metadata

parser = argparse.ArgumentParser(
    description='find book metadata')

parser.add_argument('--isbn', action="store", dest="isbn")
parser.add_argument('--ean', action="store", dest="ean")
parser.add_argument('--jpno', action="store", dest="jpno")

parser.add_argument('--rakuten-application-id', action="store",
                    dest="rakuten_application_id")
parser.add_argument('--amazon-auth-info', action="store",
                    dest="amazon_auth_info")
parser.add_argument('--use-wikipedia', action="store_true",
                    default=False, dest="use_wikipedia")

parser.add_argument('--prettyprint', action="store_true",
                    default=False, dest="prettyprint")
parser.add_argument('--delete-false-items', action="store_true",
                    default=False, dest="delete_false_items")

args = parser.parse_args()
amazon_auth_info = None
if args.amazon_auth_info:
    amazon_auth_info = args.amazon_auth_info.split(',')
rakuten_application_id = None
if args.rakuten_application_id:
    rakuten_application_id = args.rakuten_application_id
use_wikipedia = args.use_wikipedia

metadata = Metadata()
if args.isbn:
    metadata = metadata_from_isbn(
        args.isbn,
        amazon_auth_info=amazon_auth_info,
        rakuten_application_id=rakuten_application_id,
        use_wikipedia=use_wikipedia)
elif args.ean:
    metadata = metadata_from_ean(
        args.ean,
        amazon_auth_info=amazon_auth_info,
        rakuten_application_id=rakuten_application_id,
        use_wikipedia=use_wikipedia)
elif args.jpno:
    metadata = metadata_from_jpno(
        args.jpno,
        amazon_auth_info=amazon_auth_info,
        rakuten_application_id=rakuten_application_id,
        use_wikipedia=use_wikipedia)


print(json.dumps(namedtuple2dict(metadata, args.delete_false_items),
                 ensure_ascii=False, indent=2 if args.prettyprint else None))

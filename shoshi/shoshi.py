#!/usr/bin/python
# -*- coding: utf-8 -*-

from .metadata import Metadata, Creator
from . import ndl, rakuten, amazon, wikipedia


def metadata_from_isbn(isbn,
                       amazon_auth_info=None,
                       rakuten_application_id=None,
                       use_wikipedia=False):
    return metadata_from_ean(isbn,
                             amazon_auth_info,
                             rakuten_application_id,
                             use_wikipedia)


def metadata_from_ean(ean,
                      amazon_auth_info=None,
                      rakuten_application_id=None,
                      use_wikipedia=False):
    ean = ean.replace('-', '')
    amazon_metadata = Metadata()
    rakuten_metadata = Metadata()
    wikipedia_metadata = Metadata()
    ndl_metadata = ndl.metadata_from_isbn(ean)
    if not ndl_metadata.identifiers:
        ndl_metadata.identifiers['EAN'] = ean

    if amazon_auth_info:
        amazon_metadata = amazon.metadata_from_ean(
            ean, *amazon_auth_info)
    if rakuten_application_id:
        if ean.startswith('491') and len(ean) == 13:
            rakuten_metadata = rakuten.metadata_from_magazine_code(
                ean, rakuten_application_id)
        else:
            rakuten_metadata = rakuten.metadata_from_isbn(
                ean, rakuten_application_id)
    if use_wikipedia:
        title = None
        creator_names = []
        for M in (ndl_metadata, amazon_metadata, rakuten_metadata):
            if M.title:
                title = M.title.name
                creator_names = [c.name for c in M.creators]
                break
        if title:
            wikipedia_metadata = wikipedia.metadata_from_isbn(
                ean, title, creator_names)

    return merge(ndl_metadata, amazon_metadata,
                 rakuten_metadata, wikipedia_metadata)


def metadata_from_jpno(jpno,
                       amazon_auth_info=None,
                       rakuten_application_id=None,
                       use_wikipedia=False):
    jpno = jpno.replace('-', '')
    metadata = ndl.metadata_from_jpno(jpno)
    if not metadata.identifiers:
        metadata.identifiers['JPNO'] = jpno
    if 'ISBN13' in metadata.identifiers:
        return metadata_from_isbn(metadata.identifiers['ISBN13'],
                                  amazon_auth_info,
                                  rakuten_application_id,
                                  use_wikipedia)
    return metadata


def merge(ndl_metadata, amazon_metadata, rakuten_metadata, wikipedia_metadata):
    nm = ndl_metadata
    am = amazon_metadata
    rm = rakuten_metadata
    wm = wikipedia_metadata

    # タイトルは NDL => Rakuten => Amazon の順に優先
    title = nm.title or rm.title or am.title
    # NDL にタイトルが含まれていない場合，Rakuten の巻次を考慮する
    # NDL だとタイトル関連情報に含まれる内容が，楽天では巻次に入ることがあるため
    # Amazon の雑誌は正規表現で号数を取得し，巻次に入れている
    volume = nm.volume
    if not nm.title:
        volume = volume or rm.volume or am.volume
    # シリーズ情報
    # - NDL ではタイトルだが，Rakuten ではシリーズ，みたいな例が存在する
    # - NDL のタイトルが無い場合のみ Rakuten のシリーズを許可
    series = nm.series
    if not nm.title:
        series = series or rm.series
    series.extend(wm.series)
    # 出版社
    publishers = (nm.publishers or rm.publishers or am.publishers)
    # 内容細目はNDLにしか存在しない
    contents = nm.contents
    # 詳細情報は Rakuten or Amazon にしか存在しない
    description = rm.description or am.description
    # タグ情報は NDL or wikipedia
    tags = list(set(nm.tags + wm.tags))
    # サムネイルは Amazon 優先．Rakuten は画質がクソ
    thumbnails = am.thumbnails or rm.thumbnails
    # 値段は NDL => Amazon => Rakuten
    price = nm.price or am.price or rm.price
    # リンク
    links = nm.links + am.links + rm.links + wm.links
    # 出版開始日は Amazon => Rakuten => NDL (NDL からは年と月しか得られない)
    published_date = am.published_date or rm.published_date or nm.published_date
    # ページ数
    page_count = nm.page_count or rm.page_count or am.page_count
    # 識別子
    identifiers = {}
    for m in (nm, am, rm):
        for key in m.identifiers:
            if key not in identifiers:
                identifiers[key] = m.identifiers[key]
    # 著者
    # - NDL には読みが不足していたり，そもそも作者が足りなかったり様々
    # - Amazon には読みがない．役割表示は割とある．作者は大体のってる．
    # - Rakuten には読みがある．役割表示は全くない．作者はたまに欠けてる．
    creators = []
    # 翻訳モノは名前の表記がカタカナだったりそうじゃなかったりマチマチ
    # になるので，各メタデータの統合は諦める
    if nm.creators and any('訳' in c.role for c in nm.creators if c):
        creators = nm.creators
    else:
        for m in (nm, am, rm):
            for cm in m.creators:
                for i in range(len(creators)):
                    ci = creators[i]
                    if ci.name == cm.name:
                        # 同じ名前の著者を追加済み
                        # => 属性アップデート
                        c = Creator(
                            name=ci.name,
                            transcription=ci.transcription or cm.transcription,
                            role=ci.role or cm.role,
                            date_of_birth=ci.date_of_birth or cm.date_of_birth,
                            date_of_death=ci.date_of_death or cm.date_of_death)
                        creators.pop(i)
                        creators.insert(i, c)
                        break
                else:
                    creators.append(cm)

    return Metadata(
        title=title,
        volume=volume,
        series=series,
        publishers=publishers,
        creators=creators,
        contents=contents,
        identifiers=identifiers,
        description=description,
        tags=tags,
        thumbnails=thumbnails,
        price=price,
        published_date=published_date,
        page_count=page_count,
        links=links)

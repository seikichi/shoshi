#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import unicodedata

MAGAZINE_PATTERN = r'''
# 以下メンテナンスできなくなった巨大な正規表現の例

# 大まかなイメージ:
# - "[雑誌]" という文字が...
# -- 含まれている場合: "号" があれば割と雑誌っぽい
# -- 含まれていない場合: "\d{4}年" と "号" があれば割と雑誌っぽい

# 行頭
^
# 空白を strip
\s*

# * ノイズ除去
# ごくまれに，タイトル名の先頭に "【特別付録つき】"
# といった文字列が存在することがある
(?:【.+?】\s*)?

# * タイトル名
# その雑誌を一意に識別できる文字列が欲しい
# ただし "[雑誌]" のような，付いていたりいなかったりする余分な文字列は除きたい
# e.g.: ex.1 "ユリイカ 2013年12月号 特集=高畑勲「かぐや姫の物語」の世界"
#       => "ユリイカ 2013年12月号"
#       ex.2 "ちゃお DX (デラックス) 秋の超大増刊号 2013年 10月号 [雑誌]"
#       => "ちゃお DX (デラックス) 秋の超大増刊号 2013年 10月号"
# Note: 上記の "ちゃお DX" 例の場合
#       "先の超大増刊号" をタイトルに入れるか悩んだが，
#       series と number の情報があれば簡単に消すことができるので，
#       そのままにしておくことにする
(?P<title>
  # * シリーズ名
  # シリーズ名は空白以外の文字から始まり空白以外の文字で終わる
  # 最短マッチにしないと，後続する号数の部分にもマッチしてしまう
  (?P<series>\S(?:.*?\S)?)
  \s*
  # * 雑誌番号
  # シリーズ名の直後には "Vol.11" や "なんとか増刊号" といった番号がつくことがある
  (?P<series_number>
    # "Vol.1" や "No.10" といったナンバリングの次には必ず区切り文字が出現
    # 例: "精神科治療学 Vol.28増刊号" は "Vol.28増刊号" を ?P<number> の値とする
    (?:(?:\s*(?:VOL\.|Vol\.|vol\.|NO\.|No\.)\d+\s+)
        # "号" のあとは区切り文字が存在すると仮定している
        # "ESSE (エッセ) 2013年12月2014年01月号合併号" という文字列に対して
        # "2013年12月2014年01月号" は seriese_number にマッチさせない
        |(?:\s*\S+号\b)
        # "電撃ラブライブ! 1学期 2013年 3/16号" 対策 ;-p
        |(?:\s+\d+学期\s+))*)?

  # 注: "...号" の前に空白が存在しないケースもある
  # 例: "ユリイカ2011年11月臨時増刊号"
  \s*

  # * 号数
  # 重要: 雑誌タイトルには必ず "...号" が含まれていると仮定している
  (?P<number>
    # (年|月|日) からナンバリングが始まるのはおかしい
    # TODO (seikichi): そもそもこのチェックが必要ない気もする
    (?!年|月|日)

    # 注意: release_date がマッチせず，"[雑誌]" という文字列も
    #       含まない場合は雑誌でないと見なす
    (?P<release_date>
      # "年" は必ず存在すると仮定している
      # "2012年 1/6号" や "2013年 01月号" などが有り得るので，
      # "月" と "日" はオプション
      (?:\d{4}\s*年)\s*
      (?:\d{1,2}\s*月)?\s*
      (?:\d{1,2}\s*日)?\s*)?
    # "5・6合併号" や "増刊号"，"特別号" などへの対処
    # release_date にマッチしていない場合は，
    # 号の前に空白以外の文字とマッチしないとおかしい (...気がする)
    (?(release_date)\S*|\S+)号\b) # "号" の後ろは空白文字だと仮定
) # ここまでタイトル名

# * 注釈
# 雑誌の号数のあとに "特別付録 DVD バレリーナ・ストレッチ"
# などの文字列が続くことがある
# <annotation> に "[雑誌]" を含めたくないので \[ はマッチさせない
\s*(?P<annotation>[^\[]+)?\s*

# * ノイズ除去
# "ほげ年.*号" という文字列を見かけて*いない*場合は
# "[雑誌]" が含まれていると仮定している
# 例: "Dancin' (ダンシン) 第1号 [雑誌]"
(?(release_date)
  (?:\s*\[雑誌\])?
  |\s*\[雑誌\])
# "[雑誌]" のあとに "[2013.10.25]" や
# "(特別付録【SKE48 オリジナル写真集】)"
# という文字列が続くことがある
(:?\s*\(.+\))?
(:?\s*\[[\d\.]+\])?
$ # 行末
'''


def parse_magazine_title(title):
    # 全角数字や全角括弧の取り扱いが面倒なので，
    # タイトルの文字列は事前に正規化しておく
    normalized_title = unicodedata.normalize('NFKC', title)
    r = re.search(MAGAZINE_PATTERN, normalized_title, re.U | re.VERBOSE)
    if r is None:
        return {}
    d = r.groupdict()
    metadata = {}
    if d.get('series') and d.get('number'):
        metadata['title'] = d['series']
        metadata['volume'] = d['number']
        if 'annotation' in d and d['annotation']:
            metadata['volume_title'] = d['annotation']
        subtitle_start = title.find(d['series']) + len(d['series'])
        subtitle_end = title.find(d['number'])
        subtitle = title[subtitle_start:subtitle_end].strip()
        if subtitle:
            metadata['subtitle'] = subtitle
    return metadata

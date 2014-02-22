# shoshi

shoshi は国立国会図書館，Amazon，楽天，Wikipedia のAPIを組み合わせて，
書籍のISBN (or 雑誌コード，JPNO) から，その書籍のメタデータを取得するプログラム/ライブラリです．

## インストール
注: Python 2系列はサポートしてません
```
% pip install git+https://github.com/seikichi/shoshi.git
```

## 特徴
- 各種API の結果をいい感じに統合します．「国立国会図書館が提供するデータには挿絵を描いた人の情報が含まれておらず，Amazon のAPIが提供するデータには挿絵を描いた人の情報が含まれているものの読み仮名が振られておらず，楽天のAPI結果には挿絵を描いた人の読み仮名が含まれているものの，その人が挿絵を描いた人であるという情報が抜けている」みたいな場合でも安心
- Wikipedia API を利用して，書籍のジャンル ("涼宮ハルヒの消失" なら "セカイ系"，"学園小説"，"SF"，etc.) やシリーズ名 ("涼宮ハルヒの消失" なら "涼宮ハルヒシリーズ"，"氷菓" なら "古典部シリーズ" みたいな感じ) といった情報を取得できます

## 実行例
```
% python -m shoshi --isbn 4-04-429204-3 \
  --rakuten-application-id=${RAKUTEN_APPLICATION_ID} \
  --amazon-auth-info=${ACCESS_KEY},${SECRET_KEY},${ASSOCIATE_TAG} \
  --use-wikipedia --prettyprint
{
  "title": {
    "transcription": "スズミヤ ハルヒ ノ ショウシツ", 
    "relatedInformation": [], 
    "name": "涼宮ハルヒの消失", 
    "parallels": []
  }, 
  "series": [
    {
      "title": {
        "transcription": "カドカワ ブンコ", 
        "relatedInformation": [], 
        "name": "角川文庫", 
        "parallels": []
      }
    }, 
    {
      "title": {
        "relatedInformation": [], 
        "name": "涼宮ハルヒシリーズ", 
        "parallels": []
      }
    }
  ], 
  "tags": [
    "セカイ系", 
    "学園小説", 
    "サイエンス・フィクション", 
    "恋愛漫画", 
    "恋愛", 
    "SF"
  ],
  "publishers": [
    {
      "transcription": "カドカワ ショテン", 
      "name": "角川書店", 
      "location": "東京"
    }
  ], 
  "description": "「涼宮ハルヒ?それ誰?」って、国木田よ、そう思いたくなる気持ちは解らんでもないが、そんなに真顔で言うことはないだろう。だが他のやつらもハルヒなんか最初からいなかったような口ぶりだ。混乱する俺に追い打ちをかけるようにニコニコ笑顔で教室に現れた女は、俺を殺そうとし、消失したはずの委員長・朝倉涼子だった!どうやら俺はちっとも笑えない状況におかれてしまったらしいな。大人気シリーズ第4巻、驚愕のスタート。", 
  "publishedDate": "2004-07", 
  "price": "514", 
  "identifiers": {
    "ASIN": "4044292043", 
    "JPNO": "20647414", 
    "ISBN10": "4044292043", 
    "ISBN13": "9784044292041", 
    "EAN": "9784044292041"
  }, 
  "links": [
    "http://iss.ndl.go.jp/books/R100000002-I000007442470-00", 
    "http://www.amazon.co.jp/dp/4044292043", 
    "http://books.rakuten.co.jp/rb/1696409/", 
    "http://ja.wikipedia.org/wiki/%E6%B6%BC%E5%AE%AE%E3%83%8F%E3%83%AB%E3%83%92%E3%82%B7%E3%83%AA%E3%83%BC%E3%82%BA"
  ], 
  "pageCount": "254", 
  "creators": [
    {
      "transcription": "タニガワ ナガル", 
      "role": "著", 
      "name": "谷川流"
    }, 
    {
      "role": "イラスト", 
      "name": "いとうのいぢ"
    }
  ], 
  "contents": [], 
  "thumbnails": {
    "small": "http://ecx.images-amazon.com/images/I/51xQDemuC0L._SL75_.jpg", 
    "large": "http://ecx.images-amazon.com/images/I/51xQDemuC0L.jpg", 
    "medium": "http://ecx.images-amazon.com/images/I/51xQDemuC0L._SL160_.jpg"
  }
}

```

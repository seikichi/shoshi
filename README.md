# shoshi

shoshi は国立国会図書館，Amazon，楽天，Wikipedia のAPIを組み合わせて，
与えられた書籍のISBNから，その書籍のメタデータを取得するプログラム/ライブラリです．

## インストール
注: Python 2系列はサポートしてません
```
% pip install git+https://github.com/seikichi/shoshi.git
```

## 実行例
```
% python -m shoshi --isbn 978-4-04-474839-5 \
  --rakuten-application-id=${RAKUTEN_APPLICATION_ID} \
  --amazon-auth-info=${ACCESS_KEY},${SECRET_KEY},${ASSOCIATE_TAG} \
  --use-wikipedia --prettyprint
{
  "publishers": [
    {
      "transcription": "カドカワショテン", 
      "name": "角川書店", 
      "location": "東京"
    }, 
    {
      "transcription": "カドカワグループパブリッシング", 
      "name": "角川グループパブリッシング", 
      "location": "東京"
    }
  ], 
  "description": "世界に飽きていた逆廻十六夜に届いた一通の招待状。『全てを捨て、“箱庭”に来られたし』と書かれた手紙を読んだ瞬間ー完全無欠な異世界にいました!そこには猫を連れた無口な少女と高飛車なお嬢さま、そして彼らを呼んだ張本人の黒ウサギ。ウサギが箱庭世界のルールを説明しているさなか「魔王を倒そうぜ!」と十六夜が言いだして!?そんなこと黒ウサギは頼んでいないのですがっ!!超問題児3人と黒ウサギの明日はどっちだ。", 
  "publishedDate": "2011-03-31", 
  "title": {
    "transcription": "モンダイジタチ ガ イセカイ カラ クルソウデスヨ", 
    "relatedInformation": [
      {
        "transcription": "YES ウサギ ガ ヨビマシタ", 
        "name": "YES!ウサギが呼びました!", 
        "parallels": []
      }
    ], 
    "name": "問題児たちが異世界から来るそうですよ?", 
    "parallels": []
  }, 
  "series": [
    {
      "number": "16763", 
      "title": {
        "transcription": "カドカワ ブンコ", 
        "relatedInformation": [], 
        "name": "角川文庫", 
        "parallels": []
      }
    }, 
    {
      "title": {
        "transcription": "カドカワ スニーカー ブンコ", 
        "relatedInformation": [], 
        "name": "[角川スニーカー文庫]", 
        "parallels": []
      }
    }
  ], 
  "price": "590", 
  "identifiers": {
    "ASIN": "404474839X", 
    "JPNO": "21929841", 
    "ISBN10": "404474839X", 
    "ISBN13": "9784044748395", 
    "EAN": "9784044748395"
  }, 
  "links": [
    "http://iss.ndl.go.jp/books/R100000002-I000011168394-00", 
    "http://www.amazon.co.jp/dp/404474839X", 
    "http://books.rakuten.co.jp/rb/11132773/", 
    "http://ja.wikipedia.org/wiki/%E5%95%8F%E9%A1%8C%E5%85%90%E3%81%9F%E3%81%A1%E3%81%8C%E7%95%B0%E4%B8%96%E7%95%8C%E3%81%8B%E3%82%89%E6%9D%A5%E3%82%8B%E3%81%9D%E3%81%86%E3%81%A7%E3%81%99%E3%82%88%3F"
  ], 
  "tags": [
    "喜劇", 
    "コメディ", 
    "ファンタジー"
  ], 
  "pageCount": "295", 
  "creators": [
    {
      "transcription": "タツノコ タロウ", 
      "role": "著", 
      "name": "竜ノ湖太郎"
    }, 
    {
      "transcription": "アマノユウ", 
      "role": "イラスト", 
      "name": "天之有"
    }
  ], 
  "contents": [], 
  "thumbnails": {
    "small": "http://ecx.images-amazon.com/images/I/51ZEynGf6PL._SL75_.jpg", 
    "large": "http://ecx.images-amazon.com/images/I/51ZEynGf6PL.jpg", 
    "medium": "http://ecx.images-amazon.com/images/I/51ZEynGf6PL._SL160_.jpg"
  }
}
```

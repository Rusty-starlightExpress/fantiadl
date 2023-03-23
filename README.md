bitbybyte/fantiadl (https://github.com/bitbybyte/fantiadl) 
fantiadl V1.8.4をベースに改修

POST_IDのみのフォルダ名だったため
・POST_ID + タイトル名/コンテンツ名

使用方法：
python3 fantiadl.py -c {取得した cookie} -o {保存先(/mnt/fantia} -f -t

fanList.json  は  fanclub_id ：最終記録(ここまで取り込んだ)POST_id(最初から全てを取得の場合0を指定)：fanclub作成者(見て把握できる確認用)
{
    "fantiadata": [
        "17269:0:ありすLIA",
        "16490:0:岡田ゆい",
        "29318:0:くろこげママ",
        "17185:0:隣人ちゃん",
        "1470:0:せっくすフレンズ",
        "17779:0:咲鵺まこ",
        "34904:0:月山月子",
        "44103:0:はんぺん",
        "2311:0:しりー",
        "88257:0:あい",
        "13378:0:見世肉小屋"
    ]

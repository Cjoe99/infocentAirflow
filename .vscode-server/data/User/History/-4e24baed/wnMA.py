import os
import pandas as pd
import pymongo
import mysql.connector
import jieba
import re #正規表示法
import heapq
import nltk
import logging
from pymongo import MongoClient
from mysql.connector import Error
from collections import Counter
from collections import defaultdict
from datetime import datetime, timedelta
from nltk.sentiment import SentimentIntensityAnalyzer
#------------------------airflow-----------------------
from airflow import DAG
from airflow.operators.python import PythonOperator
def keywords():
    """
    > 連線到 MongoDB

    """

    # MongoDB 連接設定
    mongo_uri = "mongodb+srv://TIR103:password6341@tir103.higsi.mongodb.net/?retryWrites=true&w=majority"
    client = MongoClient(mongo_uri)
    db = client['kafka']
    collection1 = db['kafka_collection_json_test2']
    collection2 = db['kafka_collection_json_dcard']

    """### Stopwords


    """

    stopwords = {
        "17", "!","#","$","%","&","'","(",")","*","+",",","-","--",".","【", "】","\n"
        "..","...","/","0","1","2","3","4","5","6","7","8","9", "11", "17", "18", "19",
        ":",";","<","=",">",">>","?","@","A","[","]","^","_","`","|",
        "~","·","—","——","‘","’","“","”","…","、","。","〈","〉","《","》",

        "一","一些","一何","一來","一切","一则","一則","一方面","一旦","一来",
        "一样","一樣","一般","一转眼","七","万一","三","三天兩頭","三番五次",
        "三番兩次","上","上下","上來","上去","下","不","不下","不了","不亦樂乎",
        "不仅","不但","不但...而且","不僅","不僅...而且","不僅僅","不僅僅是",
        "不光","不免","不再","不力","不勝","不单","不只","不可抗拒","不可開交",
        "不同","不問","不單","不外","不外乎","不大","不如","不妨","不定","不對",
        "不少","不尽","不尽然","不巧","不已","不常","不得","不得不","不得了","不得已",
        "不必","不怎麼","不怕","不惟","不成","不拘","不擇手段","不料","不日","不是",
        "不時","不曾","不會","不止","不止一次","不比","不消","不滿","不然","不然的話",
        "不特","不独","不獨","不由得","不知不覺","不管","不管怎樣","不經意","不能","不能不",
        "不至于","不至於","不若","不要","不論","不论","不起","不过","不迭","不過","不问",
        "不限","与","与其","与其说","与否","与此同时","且","且不说","且说","两者","並",
        "並且","並沒","並沒有","並無","並肩","並非","个","个别","串列","临","为","为了",
        "为什么","为何","为止","为此","为着","乃","乃至","乃至于","么","之","之一","之所以",
        "之类","之類","乌乎","乎","乒","乘","乘勝","乘勢","乘機","乘虛","乘隙","九","也",
        "也好","也罢","也罷","了","二","二来","二話不說","二話沒說","于","于是","于是乎",
        "云云","云尔","互","互相","五","些","交口","亦","人","人人","人们","人家","人民",
        "什么","什么样","什麼","什麼樣","今","介于","仍","仍旧","仍然","仍舊","从","从此",
        "从而","他","他人","他们","他們","以","以上","以为","以便","以免","以及","以故",
        "以期","以来","以至","以至于","以至於","以致","们","任","任何","任凭","任憑",
        "似的","但","但凡","但是","但願","何","何以","何况","何嘗","何处","何妨","何必",
        "何时","何時","何樂而不為","何止","何況","何苦","何處","何須","余外","作为", "表示"
        "作為","你","你们","你們","併排","使","使得","來","來不及","來得及","來看","來著",
        "來講","例如","依","依据","依照","便","便于","保管","保險","俺","俺们","個","個人",
        "倍加","倍感","們","倒不如","倒不如說","倒是","倘","倘使","倘或","倘然","倘若","借",
        "假使","假如","假若","偏偏","偶爾","偶而","傥然","傳","傳聞","傳說","僅","僅僅","像",
        "儘可能","儘快","儘早","儘管","儘管如此","儘量","儿","充其極","充其量","充分","先不先",
        "光","光是","內","全体","全力","全年","全然","全身心","全部","全都","兩者","八","八成",
        "公然","六","兮","共","共總","关于","其","其一","其中","其二","其他","其余","其它","其實",
        "其後","其次","其餘","具体地说","具体说来","具體來說","具體地說","具體說來","兼之","内",
        "再","再其次","再则","再有","再者","再者说","再說","再说","冒","冲","况且","凝神","几",
        "几时","凡","凡是","凭","凭借","出","出于","出來","出去","出来","分别","分期","分期分批",
        "分頭","切","切不可","切切","切勿","切莫","则","则甚","初","別","別人","別的","別說","别",
        "别人","别处","别是","别的","别管","别说","到","到了兒","到底","到目前為止","到處","到頭",
        "到頭來","則","前后","前後","前此","前者","剛","剛好","剛巧","剛才","加上","加之","加以",
        "勃然","動不動","動輒","匆匆","千","千萬","千萬千萬","半","即","即令","即使","即便","即刻",
        "即如","即將","即或","即是說","即若","却","去","又","又及","及","及其","及至","反之",
        "反之亦然","反之則","反倒","反倒是","反手","反而","反过来","反过来说","反過來","反過來說",
        "取道","受到","古來","另","另一個","另一方面","另外","另悉","另方面","另行","只","只当",
        "只怕","只是","只有","只消","只要","只限","叫","叮咚","叮噹","可","可以","可好","可是",
        "可能","可見","可见","各","各个","各位","各個","各式","各种","各種","各自","同","同时",
        "同時","后","后者","向","向使","向着","向著","吓","吗","否则","否則","吧","吧哒","吧噠",
        "吱","吶","呀","呃","呆呆地","呕","呗","呜","呜呼","呢","呵","呵呵","呸","呼哧","呼啦",
        "咋","和","咚","咦","咧","咱","咱们","咱們","咳","哇","哈","哈哈","哉","哎","哎呀",
        "哎哟","哎喲","哗","哟","哦","哩","哪","哪个","哪些","哪個","哪儿","哪兒","哪天","哪年",
        "哪怕","哪样","哪樣","哪裏","哪边","哪邊","哪里","哼","哼唷","唄","唉","唯有","啊","啊呀",
        "啊哈","啊喲","啐","啥","啦","啪达","啪達","啷当","喀","喂","喏","喔唷","單", "jpeg"
        "單單","單純","喲","喽","嗎","嗚","嗚呼","嗡","嗡嗡","嗬","嗯","嗳","嘎","嘎嘎","嘎登",
        "嘔","嘘","嘛","嘩","嘩啦","嘻","嘿","嘿嘿","噓","噯","嚇","四","因","因为","因了", "表示"
        "因此","因為","因着","因而","固","固然","在","在下","在于","地","均","基于","基於",
        "基本","基本上","处在","多","多么","多多","多多少少","多多益善","多少","多年來","多年前",
        "多次","多虧","夠瞧的","夥同","大","大不了","大事","大凡","大多","大大","大家","大張旗鼓",
        "大抵","大概","大略","大約","大致","大舉","大都","大面兒上","大體","大體上","奇","奈",
        "奮勇","她","她们","她們","好","好在","如","如上","如上所述","如下","如今","如何", "jpeg"
        "如其","如前所述","如同","如常","如是","如期","如果","如次","如此","如此等等","如若",
        "始而","姑且","存心","孰料","孰知","宁","宁可","宁愿","宁肯","它","它们","它們", "jpg"
        "定","寧","寧可","寧肯","寧願","对","对于","对待","对方","对比","将","將","將才", "17"
        "將要","將近","對","對於","小","尔","尔后","尔尔","尚且","就","就地","就是","就是了",
        "就是說","就是说","就此","就算","就要","尽","尽管","尽管如此","局外","居然","屆時",
        "屢","屢屢","屢次","屢次三番","岂但","川流不息","差一點","差不多","己","已", "jpg"
        "已矣","巴","巴巴","帶","常","常常","常言說","常言說得好","常言道","平素","年覆一年",
        "并","并且","并非","幾","幾乎","幾度","幾時","幾番","幾經","庶乎","庶几","开外",
        "开始","弗","彈指之間","归","归齐","当","当地","当然","当着","彼","彼时","彼此",
        "往","待","待到","很","很多","很少","後來","得","得了","得天獨厚","得起","從", "17"
        "從不","從中","從今以後","從來","從優","從古到今","從古至今","從嚴","從寬","從小",
        "從新","從早到晚","從未","從此","從此以後","從無到有","從而","從輕","從速","從重",
        "從頭","徹夜","必","必定","必將","必須","快","快要","忽地","忽然","怎","怎么",
        "怎么办","怎么样","怎奈","怎样","怎樣","怎麼","怎麼樣","怎麼辦","怕","急匆匆",
        "怪","怪不得","总之","总的来看","总的来说","总的说来","总而言之","恍然","恐怕",
        "恰似","恰好","恰如","恰巧","恰恰","恰恰相反","恰逢","您","惟其","慢說","慢说",
        "慣常","憑","憑藉","憤然","成年","成年累月","成心","我","我们","我們","或", "知道"
        "或则","或多或少","或是","或曰","或者","或許","截然","截至","所","所以","所在",
        "所幸","所有","才","才能","打","打从","打從","打開天窗說亮話","把","抑或","抽冷子",
        "拿","按","按時","按期","按照","按理","按說","挨個","挨家挨戶","挨次","挨著",
        "挨門挨戶","挨門逐戶","换句话说","换言之","据","据此","接下來","接着","接著",
        "接連不斷","換句話說","換言之","撲通","據","據實","據悉","據我所知","據此","據稱",
        "據說","攔腰","放量","故","故意","故此","故而","敞開兒","敢","敢情","敢於", "知道"
        "斷然","方","方才","方能","於","於是","於是乎","旁人","无","无宁","无论","既",
        "既...又","既往","既是","既然","日漸","日益","日臻","日覆一日","日見","时候",
        "昂然","是","是以","是的","時候","暗中","暗地裏","暗自","更","更加","更為",
        "更進一步","曾","替","替代","最","會","有","有些","有关","有及","有时","有的",
        "有關","望","朝","朝着","朝著","末##末","本","本人","本地","本着","本著", "覺得"
        "本身","来","来着","来自","来说","极了","果然","果真","某","某个","某些",
        "某個","某某","根据","根據","格外","梆","極","極了","極其","極力","極大",
        "極度","極為","極端","概","權時","次第","欤","正值","正如","正巧","正是",
        "此","此中","此地","此处","此外","此後","此时","此次","此間","此间","歷",
        "歸","歸根到底","歸根結底","殆","毋宁","毋寧","每","每当","每時每刻","每每",
        "每當","每逢","比","比及","比如","比如說","比方","比照","比起","毫不","毫無",
        "毫無例外","毫無保留地","汝","決不","決非","沒","沒有","沖","沙沙","没奈何",
        "沿","沿着","沿著","況且","活","湊巧","滿","漫說","漫说","為","為了","為什麼",
        "為何","為著","烏乎","焉","無寧","無論","然","然则","然則","然后","然後","然而",
        "照","照着","照著","爾後","爾等","牢牢","犹且","犹自","猛然","猛然間","獨",
        "獨自","率然","率爾","理應","理當","理該","瑟瑟","甚且","甚么","甚或","甚而",
        "甚至","甚至于","甚麼","用","用来","甫","甭","由","由于","由於","由是","由此",
        "由此可見","由此可见","畢竟","略","略加","略微","略為","當","當下","當中", "覺得"
        "當兒","當即","當口兒","當場","當庭","當然","當真","當著","當頭","白","白白",
        "的","的确","的確","的話","的话","皆可","盡","盡如人意","盡心盡力","盡心竭力","盡然",
        "直到","相对而言","相對而言","省得","看","看上去","看來","看樣子","看起來","眨眼",
        "着","着呢","矣","矣乎","矣哉","砰","碰巧","社會主義","离","究竟","窮年累月",
        "竊","立","立刻","立地","立時","立馬","竟","竟然","竟而","第","等","等到",
        "等等","策略地","简言之","管","簡直","簡而言之","簡言之","类如","粗","精光","純",
        "純粹","紧接着","累年","累次","結果","絕","絕不","絕對","絕非","絕頂","給","經",
        "經常","經過","綜上所述","緊接著","縱","縱令","縱使","縱然","縷縷","總之","總的來看",
        "總的來說","總的說來","總而言之","繼之","繼而","纵","纵令","纵使","纵然","经","经过","结果",
        "给","继之","继后","继而","综上所述","罢了","罷了","老","老大","老是","老老實實",
        "者","而","而且","而况","而又","而后","而外","而已","而後","而是","而況","而言","而論",
        "聯袂","背地裏","背靠背","能","能否","腾","臨","臨到","自","自个儿","自从","自個兒",
        "自各儿","自各兒","自后","自家","自己","自從","自打","自身","臭","至","至于",
        "至今","至於","至若","致","與","與其","與否","與此同時","舉凡","般的","若",
        "若夫","若是","若果","若非","莫","莫不","莫不然","莫如","莫若","莫非","萬一",
        "著","著呢","藉以","藉此","處處","虽","虽则","虽然","虽说","蠻","被","要","要不",
        "要不是","要不然","要么","要是","要麼","見","親口","親手","親眼","親自","親身",
        "設使","設若","話說","該","該當","誠然","誰","誰知","請勿","論","論說","諸位","謹",
        "譬喻","譬如","讓","让","许多","论","设使","设或","设若","诚如","诚然","该",
        "说来","诸","诸位","诸如","谁","谁人","谁料","谁知","豁然","豈","豈但","豈止",
        "豈非","贼死","赖以","赶","起","起來","起先","起初","起見","起见","起頭","起首",
        "趁","趁便","趁勢","趁早","趁機","趁熱","趁着","趁著","越是","趕","趕快",
        "趕早不趕晚","距","跟","路經","較","較之","較比","較為","轟然","较","较之","边",
        "迄","过","近","近來","近年來","近幾年來","还","还是","还有","还要","这","这一来",
        "这个","这么","这么些","这么样","这么点儿","这些","这会儿","这儿","这就是说",
        "这时","这样","这次","这般","这边","这里","进而","连","连同","迫於","逐步",
        "這","這些","這個","這兒","這就是說","這時","這會兒","這樣","這裏","這邊","這麼",
        "這麼些","這麼樣","這麼點兒","通过","通過","逢","連","連同","連日","連日來",
        "連聲","連袂","連連","進來","進去","進而","過","過於","達旦","遲早","遵循","遵照",
        "還","還是","還有","邊","那","那个","那么","那么些","那么样","那些","那会儿","那個","那儿",
        "那兒","那时","那時","那會兒","那末","那样","那樣","那般","那裏","那边","那邊","那里",
        "那麼","那麼些","那麼樣","都","鄙人","鉴于","鑒於","针对","長期以來","長此下去","長線",
        "長話短說","開外","開始","間或","關於","阿","陡然","除","除了","除卻","除去","除外","除开",
        "除此","除此之外","除此以外","除此而外","除開","除非","陳年","随","随后","随时",
        "随着","隔夜","隔日","隨","隨著","难道说","雖","雖則","雖然","雖說","離","難得",
        "難怪","難說","難道","雲雲","零","非但","非常","非徒","非得","非特","非独","完整", "10"
        "靠","頂多","頃","頃刻","頃刻之間","頃刻間","順","順著","頓時","頗","顺", "表示"
        "顺着","風雨無阻","飽","餵","首先","馬上","騰","高低","麼","默然","默默地",
        "齊","︿","！","＃","＄","％","＆","（","）","＊","＋", "直接"
        "，","０","１","２","３","４","５","６","７","８","９","：", "知道"
        "；","＜","＞","？","＠","［","］","｛","｜","｝","～", "直接", "10", "表示"
        "￥","剛剛","之前","安安","某個","最近","這就","事情","原因","昨天","今天","明天",
        "這個","那個","如果","其實","即使","如題","大家","同時","以下","各位","真的","以前",
        "以後","未來","是否","目前","要講","這兩個","前天","這樣","那樣","看起","一堆",
        "一個","有人","https","如題","媒體""來源", "台灣", "imgur", "www", "媒體",
        "違者", "看到", "com", "新聞", "來源", "文章", "以前", "刪除", "現在", "15", "一嘔",
        "表示", "知道", "jpg", "jpeg", "覺得", "from", "這次", "一直", "17",

    }

    """### 資料正規化"""

    def format_date(date_string):
        """
        統一處理兩種不同格式的日期:
        1. MM/DD 格式 (來自PTT)
        2. ISO格式 (來自Dcard) 2024-10-19T08:25:47.246Z
        """
        try:
            if not date_string:
                return None

            if "/" in date_string:  # PTT格式
                date_obj = datetime.strptime(date_string, "%m/%d")
                return f"2024-{date_obj.month:02d}-{date_obj.day:02d}"
            elif "T" in date_string:  # Dcard ISO格式
                date_obj = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
                return f"2024-{date_obj.month:02d}-{date_obj.day:02d}"
            else:
                return None
        except Exception as e:
            print(f"日期解析錯誤: {e}, 日期字串: {date_string}")
            return None

    def analyze_posts(contents, stopwords):
        """
        分析文章內容，返回關鍵字和出現次數的列表
        """
        keywords = []
        for content in contents:
            if not isinstance(content, str):
                continue

            # 使用結巴分詞
            seg_list = list(jieba.cut(content))

            # 過濾停用詞並統計詞頻
            word_freq = Counter(word for word in seg_list if word not in stopwords and len(word) > 1)

            # 將所有關鍵字和頻率加入結果列表
            keywords.extend(word_freq.items())

        return keywords

    def get_top_keywords(keyword_dict, n=3):
        """
        從關鍵字字典中獲取前N個關鍵字及其出現次數
        """
        top_n = heapq.nlargest(n, keyword_dict.items(), key=lambda x: x[1])
        keywords = []
        counts = []

        for keyword, count in top_n:
            keywords.append(keyword)
            counts.append(count)

        # 補足到指定長度
        while len(keywords) < n:
            keywords.append(None)
            counts.append(None)

        return keywords, counts

    def get_date_from_document(document):
        """
        從文件中提取日期，處理多種可能的日期欄位名稱
        """
        if not isinstance(document, dict) or 'value' not in document:
            return None

        value = document['value']
        if not isinstance(value, dict):
            return None

        # 檢查所有可能的日期欄位名稱
        date_field_names = ['發布時間', '發佈時間', '釋出日期', '發佈日期']
        for field_name in date_field_names:
            if field_name in value and value[field_name]:
                return format_date(value[field_name])

        return None

    def process_single_collection(collection, keyword_counts, stopwords):
        """
        處理單個collection的文件
        """
        batch_size = 5000
        counter = 0
        total_count = collection.count_documents({})
        date_format_stats = defaultdict(int)
        processed_posts = set()  # 用於追蹤已處理的文章

        print(f"開始處理 collection {collection.name}, 總文件數: {total_count}")

        while counter < total_count:
            cursor = collection.find().skip(counter).limit(batch_size)
            documents = list(cursor)

            if not documents:
                break

            for document in documents:
                try:
                    # 獲取文章ID
                    post_id = str(document.get('_id'))
                    if post_id in processed_posts:
                        continue

                    # 檢查value字段
                    if 'value' not in document:
                        print(f"文件缺少value欄位: {post_id}")
                        continue

                    value = document['value']
                    if not isinstance(value, dict):
                        print(f"value欄位不是字典格式: {post_id}")
                        continue

                    # 提取日期
                    publish_date = get_date_from_document(document)
                    if not publish_date:
                        print(f"無法解析日期: {post_id}")
                        continue

                    # 提取內容
                    content = value.get('內容')
                    if not content:
                        print(f"文件缺少內容: {post_id}")
                        continue

                    # 更新日期格式統計
                    source = 'PTT' if "ptt.cc" in str(value.get('連結', '')) else 'Dcard'
                    date_format_stats[source] += 1

                    # 處理內容和關鍵字
                    keywords = analyze_posts([content], stopwords)
                    if keywords:
                        for keyword, count in keywords:
                            keyword_counts[publish_date][keyword] += count

                    processed_posts.add(post_id)

                except Exception as e:
                    print(f"處理文件時發生錯誤 {post_id}: {str(e)}")
                    continue

            counter += batch_size
            print(f"已處理 {counter}/{total_count} 筆文件")

        # 輸出統計資訊
        print("\n日期格式統計:")
        for format_type, count in date_format_stats.items():
            print(f"{format_type}: {count} 筆")

        return keyword_counts

    def process_all_collections(collections, stopwords):
        """
        處理所有collections並整合結果
        """
        combined_keyword_counts = defaultdict(lambda: defaultdict(int))

        for collection in collections:
            print(f"\n開始處理 collection: {collection.name}")
            combined_keyword_counts = process_single_collection(
                collection,
                combined_keyword_counts,
                stopwords
            )

        # 將結果轉換為DataFrame
        daily_top_keywords = []

        for date in sorted(combined_keyword_counts.keys()):
            keywords, counts = get_top_keywords(combined_keyword_counts[date])
            daily_top_keywords.append({
                "發佈日期": date,
                "關鍵字1": keywords[0],
                "次數1": counts[0],
                "關鍵字2": keywords[1],
                "次數2": counts[1],
                "關鍵字3": keywords[2],
                "次數3": counts[2]
            })

        result_df = pd.DataFrame(daily_top_keywords)

        # 顯示處理結果統計
        print(f"\n總共處理了 {len(result_df)} 個不同日期")
        if not result_df.empty:
            print(f"每個日期的關鍵字數量: {(len(result_df.columns) - 1) // 2}")
        else:
            print("警告: 未產生任何結果")

        return result_df

    """### 主程式"""

    if __name__ == "__main__":
        try:
            # 設定logging
            logging.basicConfig(level=logging.INFO)

            # 連接 MySQL
            connection, cursor = connect_to_mysql()

            if not connection or not cursor:
                raise Exception("無法建立資料庫連線")

            try:
                # 載入停用詞（確保已經定義）
                if 'stopwords' not in locals():
                    stopwords = set()  # 或從檔案載入
                    print("使用空的停用詞集合")

                # 處理collections
                collections = [collection1, collection2]  # 確保這些變數已經定義
                result_df = process_all_collections(collections, stopwords)

                if not result_df.empty:
                    print("\n每日關鍵字統計結果：")
                    print(result_df)
                    update_keywords_table(connection, cursor, result_df)
                else:
                    print("沒有產生任何結果，跳過資料庫更新")

            finally:
                cursor.close()
                connection.close()
                print("資料庫連線已關閉")

        except Exception as e:
            logging.error(f"程式執行過程發生錯誤: {str(e)}")
            raise

    # 設置默認參數
    default_args = {
        'owner': 'airflow',
        'depends_on_past': False,
        'start_date': datetime(2024, 10, 24),
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    }

    # 定義 DAG
    with DAG(
        'test3',
        default_args=default_args,
        description='A simple Selenium DAG',
        schedule_interval=timedelta(days=1),  # 每天運行一次
        catchup=False,
    ) as dag:

        run_selenium_task = PythonOperator(
            task_id='run_selenium_task',
            python_callable=selenium_scraper
        )
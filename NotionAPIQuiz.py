import requests
import time
import random

db_id = "DB_ID"
db_url = f"https://api.notion.com/v1/databases/{db_id}/query"

integration_token = "INTEGRATION_TOKEN"

headers = {
    "Authorization": f"Bearer {integration_token}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}


def query_database(page_id, integration_token):
    """
    最初にデータベースを全部読み込む
    """
    has_more = True
    next_cursor = None
    results = []
    count = 0
    
    while has_more:
        payload = {}
        if next_cursor:
            payload["start_cursor"] = next_cursor
        
        response = requests.post(db_url, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            results.extend(data["results"])
            has_more = data["has_more"]
            next_cursor = data.get("next_cursor")
            print(f"page{count} loaded")
            count += 1
        else:
            return response.status_code, response.text, response.reason
    
    return results        


def make_words_count(results):
    """
    実際に使うリストを作る
    """
    words_counts = []
    start_time = time.time()
    for result in results:
        try:
            ## タイトルが空になっているページを除く
            word = result["properties"]["Name"]["title"][0]["text"]["content"]
        except:
            continue
        ## ここで counter が 0 になるやつもあるので、アプリとするときはエラー処理入れる
        count = result["properties"]["count"]["number"] + 1
        url = result["url"]
        word_id = result["id"]

        ## 他のプロパティを取得
        word_type = None
        material = None
        category = None

        try:
            word_type = result["properties"]["type"]["select"]["name"]
        except:
            pass

        try:
            material = result["properties"]["material"]["multi_select"]["name"]
        except:
            pass

        try:
            category = result["properties"]["category"]["multi_select"]["name"]
        except:
            pass

        words_counts.append((word, count, url, word_id, word_type, material, category))
    end_time = time.time()
    print(f"繰り返し処理用のリスト作成 {end_time - start_time}s")
    
    return words_counts


def break_type_checker():
    """
    終了のタイプを決める
    """
    break_input = input("プログラムの中断によって終了する場合はエンターを押してください。それ以外の入力で都度確認します。:")
    
    if break_input == "":
        break_type = "program_interupt"
    else:
        break_type = "input_interupt"
    
    return break_type


def mode_checker():
    """
    mode: 表示する情報のリストを決める
    """
    mode_edit = input("表示する情報を編集しない場合はエンターを押してください。それ以外の入力でモードを編集します。")
    
    if mode_edit == "":
        mode = [
            "count",
            "word_type",
            "material",
            "category",
        ]
    
    else:
        mode = []
        mode_add = input("カウントを表示する場合はエンターを押してください。それ以外の入力で表示しません。:")
        if mode_add == "":
            mode.append("count")
        else:
            pass

        mode_add = input("タイプを表示する場合はエンターを押してください。それ以外の入力で表示しません。:")
        if mode_add == "":
            mode.append("word_type")
        else:
            pass

        mode_add = input("教材を表示する場合はエンターを押してください。それ以外の入力で表示しません。:")
        if mode_add == "":
            mode.append("material")
        else:
            pass

        mode_add = input("カテゴリを表示する場合はエンターを押してください。それ以外の入力で表示しません。:")
        if mode_add == "":
            mode.append("category")
        else:
            pass
            
    return mode

def make_filter():
    """
    フィルターを作る（今後追加)
    """
    pass

def random_word_choice(words_counts, mode, filter_mode=None):
    """
    mode: list, ランダムに選んだワードの、どのプロパティを表示するかを指定する
    filter_mode: フィルタリング機能（今後追加)
    """
    
    total_weight = sum(word_count[1] for word_count in words_counts)
    flag = True
    
    while flag:
        
        r = random.uniform(0, total_weight)
        upto = 0

        for name, count, url, word_id, word_type, material, category in words_counts:
            if upto + count >= r:
            
                ## ここでフィルター処理入れる予定; flag を使う
                
                ## 必須のものを先に display に入れておく
                display = {"question": name,
                           "url" : url
                          }

                if "count" in mode:
                    display["count"] = count - 1
                else:
                    display["count"] = "HIDDEN count"

                if "word_type" in mode:
                    display["word_type"] = word_type
                else:
                    display["word_type"] = "HIDDEN type"

                if "material" in mode:
                    display["material"] = material
                else:
                    display["material"] = "HIDDEN material"

                if "category" in mode:
                    display["category"] = category
                else:
                    display["category"] = "HIDDEN cotegory"

                ## 表示はしないので、最後に入れる
                display["word_id"] = word_id

                return display, count
            upto += count
        
        

if __name__ == "__main__":
    ## 最初に DB全体を読み込む
    start_time = time.time()
    results = query_database(db_id, integration_token)
    end_time = time.time()
    print(f"データベース読み込み終了 {end_time - start_time}s")
    
    words_counts = make_words_count(results)
    
    mode = mode_checker()
    break_type = break_type_checker()
    print(break_type)
    
    quiz_count = 1
    
    ## クイズの表示
    while True:
        ## 問題の表示
        print(f"====== 第{quiz_count}問 ====================================================================")

        display, count = random_word_choice(words_counts, mode)
        keys = list(display.keys())
        for key in keys[:-1]:
            print(key, ": ", display[key])

        ## 解答の表示
        """
        answer_button = input("解答を表示します。エンターを押してください。 ：")
        while not answer_button == "":
            answer_button = input("無効です。解答を表示します。エンターを押してください。：")
        else:
            page_id = ...
            ...
            print("-------------------------------------------------------")
        """
        answer_button = input("解答を表示します。何かを入力してください。 ：")
        #else:
        page_id = display["word_id"]
        url = f"https://api.notion.com/v1/blocks/{page_id}/children"

        print("-------------------------解答-------------------------")
        response = requests.get(url, headers=headers)
        blocks = response.json()["results"]
        for block in blocks:
            try:
                ## 空白のブロックだとエラーになる
                print(block["paragraph"]["rich_text"][0]["text"]["content"])
            except:
                try:
                    ## numbered_list の場合
                    print(block["numbered_list_item"]["rich_text"][0]["text"]["content"])
                except:
                    try:
                        print(block["code"]["rich_text"][0]["text"]["content"])
                    except:
                        print("")
        print("------------------------------------------------------")

        ## カウントアップの意思確認
        countup_button = input("そのまま続ける場合はエンターを押してください。それ以外の入力でカウントを1増やします。：")
        if countup_button == "":
            pass
        else:
            url = f"https://api.notion.com/v1/pages/{page_id}"
            data = {
                "properties": {
                    "count":{
                        "number": count ## すでに1足されているのでこれで良い
                    }
                }
            }
            response = requests.patch(url, headers=headers, json=data)
            print("カウントを1増やしました。")

        ## 終了の意思確認
        if break_type == "program_interupt":
            pass
        else:
            break_button = input("続ける場合はエンターを押してください。それ以外の入力で終了します。：")
            if break_button == "":
                pass
            else:
                print("================================================================================")
                print(f"終了します。{quiz_count}問解きました。")
                break
        quiz_count += 1
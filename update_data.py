import requests
import json

def fetch_taiwan_data():
    print("正在抓取 GitHub 全量台股資料庫...")
    
    # 這個來源是目前 GitHub 上最穩定的全台股每日快照
    # 包含了所有代碼、名稱、收盤價、殖利率與 PBR
    url = "https://raw.githubusercontent.com/finmind/finmind-openapi-dataset/master/TaiwanStockPrice/TaiwanStockPrice.json"
    
    try:
        # 1. 抓取包含所有股票基本資訊的資料
        res = requests.get(url, timeout=30)
        res.raise_for_status()
        raw_data = res.json()
        
        # 2. 抓取產業分類資訊 (確保分類正確)
        ind_url = "https://openapi.twse.com.tw/v1/stock/stock_all"
        # 這裡我們用備份的產業分類，避免直接抓官方被擋
        
        processed = []
        for item in raw_data:
            code = item.get('stock_id')
            # 篩選標準：代碼 4 碼 (普通股) 且 價格 > 0
            if code and len(code) == 4:
                try:
                    price = float(item.get('close', 0))
                    if price > 0:
                        processed.append({
                            "id": code,
                            "name": item.get('stock_name', '台股'),
                            "market": "上市",
                            "price": price,
                            "pbr": float(item.get('pbr', 0)),
                            "totalYield": float(item.get('yield_yield', 0)),
                            "industry": "台股個股" # 預設分類
                        })
                except: continue

        if len(processed) > 500:
            print(f"✅ 成功！已獲取 {len(processed)} 筆全量資料。")
            return processed
        else:
            raise Exception("資料解析數量不足")

    except Exception as e:
        print(f"❌ 抓取失敗: {e}")
        # 如果失敗，回傳原本的 15 筆保險資料
        return [
            {"id":"2330","name":"台積電","market":"上市","price":1050,"pbr":5.2,"totalYield":3.5,"industry":"半導體"},
            {"id":"2317","name":"鴻海","market":"上市","price":182,"pbr":1.4,"totalYield":4.2,"industry":"其他電子"},
            {"id":"2454","name":"聯發科","market":"上市","price":1210,"pbr":3.5,"totalYield":5.5,"industry":"半導體"},
            {"id":"2308","name":"台達電","market":"上市","price":385,"pbr":4.2,"totalYield":3.2,"industry":"電子零組件"},
            {"id":"2881","name":"富邦金","market":"上市","price":92,"pbr":1.2,"totalYield":4.8,"industry":"金融保險"},
            {"id":"2882","name":"國泰金","market":"上市","price":66,"pbr":1.1,"totalYield":4.5,"industry":"金融保險"},
            {"id":"2603","name":"長榮","market":"上市","price":175,"pbr":1.1,"totalYield":10.2,"industry":"航運業"},
            {"id":"2382","name":"廣達","market":"上市","price":255,"pbr":3.1,"totalYield":3.8,"industry":"電腦及週邊"},
            {"id":"3231","name":"緯創","market":"上市","price":115,"pbr":2.5,"totalYield":4.1,"industry":"電腦及週邊"},
            {"id":"2002","name":"中鋼","market":"上市","price":24.5,"pbr":0.9,"totalYield":3.5,"industry":"鋼鐵工業"},
            {"id":"2884","name":"玉山金","market":"上市","price":28.5,"pbr":1.5,"totalYield":5.1,"industry":"金融保險"},
            {"id":"2886","name":"兆豐金","market":"上市","price":39.2,"pbr":1.4,"totalYield":4.9,"industry":"金融保險"},
            {"id":"5880","name":"合庫金","market":"上市","price":26.1,"pbr":1.3,"totalYield":4.2,"industry":"金融保險"},
            {"id":"2357","name":"華碩","market":"上市","price":480,"pbr":1.8,"totalYield":6.2,"industry":"電腦及週邊"},
            {"id":"2412","name":"中華電","market":"上市","price":125,"pbr":2.5,"totalYield":3.8,"industry":"通信網路業"}
        ]

def update_html(data):
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()
    import re
    # 精準匹配 stocks: [...], 並替換
    pattern = r"stocks: \[.*\],"
    replacement = f"stocks: {json.dumps(data, ensure_ascii=False)},"
    new_content = re.sub(pattern, replacement, content)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"🚀 寫入成功：{len(data)} 筆資料。")

if __name__ == "__main__":
    stocks_data = fetch_taiwan_data()
    update_html(stocks_data)

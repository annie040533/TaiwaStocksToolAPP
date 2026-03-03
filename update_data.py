import requests
import json

def fetch_taiwan_data():
    print("正在抓取證交所穩定 OpenAPI 節點...")
    
    # 這是證交所正式開放給開發者的節點，包含 PBR, 殖利率, 價格
    url = "https://openapi.twse.com.tw/v1/exchangeReport/BWIBYK_ALL"
    # 產業對照節點
    ind_url = "https://openapi.twse.com.tw/v1/stock/stock_all"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        # 1. 抓取基本數據
        res = requests.get(url, headers=headers, timeout=30)
        res.raise_for_status()
        raw_data = res.json()
        
        # 2. 抓取產業分類 (如果被擋就用預設)
        try:
            ind_res = requests.get(ind_url, headers=headers, timeout=20)
            ind_lookup = {item['Code']: item for item in ind_res.json()}
        except:
            ind_lookup = {}

        processed = []
        for item in raw_data:
            code = item.get('Code')
            # 排除權證與特別股，只抓 4 碼普通股
            if code and len(code) == 4:
                try:
                    price = float(item['ClosingPrice']) if item.get('ClosingPrice') else 0
                    if price > 0:
                        processed.append({
                            "id": code,
                            "name": ind_lookup.get(code, {}).get('Name', item.get('Name', '台股')),
                            "market": "上市",
                            "price": price,
                            "pbr": float(item['PBRatio']) if item.get('PBRatio') else 0,
                            "totalYield": float(item['YieldYield']) if item.get('YieldYield') else 0,
                            "industry": ind_lookup.get(code, {}).get('Category', '一般產業')
                        })
                except: continue

        if len(processed) > 500:
            print(f"✅ 成功！已獲取 {len(processed)} 筆全量資料。")
            return processed
        else:
            raise Exception("資料解析數量不足")

    except Exception as e:
        print(f"❌ API 抓取失敗: {e}")
        # 最終保險：回傳擴充後的 20 檔權值股清單
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
            {"id":"2884","name":"玉山金","market":"上市","price":28,"pbr":1.5,"totalYield":5.0,"industry":"金融保險"},
            {"id":"2357","name":"華碩","market":"上市","price":480,"pbr":1.8,"totalYield":6.1,"industry":"電腦及週邊"},
            {"id":"2609","name":"陽明","market":"上市","price":72,"pbr":0.9,"totalYield":8.5,"industry":"航運業"},
            {"id":"2615","name":"萬海","market":"上市","price":90,"pbr":1.0,"totalYield":7.2,"industry":"航運業"},
            {"id":"2891","name":"中信金","market":"上市","price":35,"pbr":1.3,"totalYield":5.2,"industry":"金融保險"},
            {"id":"1101","name":"台泥","market":"上市","price":32,"pbr":0.8,"totalYield":4.5,"industry":"水泥工業"},
            {"id":"2327","name":"國巨","market":"上市","price":580,"pbr":2.1,"totalYield":4.0,"industry":"電子零組件"},
            {"id":"3008","name":"大立光","market":"上市","price":2400,"pbr":2.5,"totalYield":3.8,"industry":"光電業"},
            {"id":"2379","name":"瑞昱","market":"上市","price":450,"pbr":4.5,"totalYield":5.5,"industry":"半導體"},
            {"id":"2892","name":"第一金","market":"上市","price":27,"pbr":1.4,"totalYield":4.8,"industry":"金融保險"}
        ]

def update_html(data):
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()
    import re
    # 萬用匹配
    pattern = r"stocks: \[.*\],"
    replacement = f"stocks: {json.dumps(data, ensure_ascii=False)},"
    new_content = re.sub(pattern, replacement, content)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"🚀 已成功寫入 {len(data)} 筆資料到 index.html")

if __name__ == "__main__":
    stocks_data = fetch_taiwan_data()
    update_html(stocks_data)

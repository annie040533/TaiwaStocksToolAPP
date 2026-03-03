import requests
import json

def fetch_taiwan_data():
    print("正在嘗試從穩定來源抓取資料...")
    # 改用更開放的 GitHub Data Source 或是備用穩定網址
    # 這裡我們換一個證交所另一組較寬鬆的 API
    url_pbr = "https://openapi.twse.com.tw/v1/exchangeReport/BWIBYK_ALL"
    url_name = "https://openapi.twse.com.tw/v1/stock/stock_all"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        # 1. 先抓取基本資料
        res = requests.get(url_pbr, headers=headers, timeout=30)
        res.raise_for_status()
        raw_stocks = res.json()
        
        # 2. 抓取名稱與產業資料
        res_ind = requests.get(url_name, headers=headers, timeout=30)
        ind_lookup = {item['Code']: item for item in res_ind.json()}
        
        processed = []
        for item in raw_stocks:
            code = item.get('Code')
            # 排除權證與非普通股 (代碼長度為 4 碼)
            if code and len(code) == 4 and code in ind_lookup:
                try:
                    price = float(item['ClosingPrice']) if item.get('ClosingPrice') else 0
                    if price > 0:
                        processed.append({
                            "id": code,
                            "name": ind_lookup[code]['Name'],
                            "market": "上市",
                            "price": price,
                            "pbr": float(item['PBRatio']) if item.get('PBRatio') else 0,
                            "totalYield": float(item['YieldYield']) if item.get('YieldYield') else 0,
                            "industry": ind_lookup[code]['Category']
                        })
                except: continue
        
        if processed:
            print(f"成功抓取 {len(processed)} 筆真實資料！")
            return processed
            
    except Exception as e:
        print(f"抓取失敗: {e}")
    
    # 萬一還是被封鎖，最後一招：回傳一組預設的熱門股，不讓網頁全空
    return [
        {"id": "2330", "name": "台積電", "market": "上市", "price": 1050, "pbr": 5.2, "totalYield": 3.5, "industry": "半導體"},
        {"id": "2317", "name": "鴻海", "market": "上市", "price": 180, "pbr": 1.5, "totalYield": 4.2, "industry": "其他電子"},
        {"id": "2454", "name": "聯發科", "market": "上市", "price": 1200, "pbr": 3.8, "totalYield": 5.1, "industry": "半導體"}
    ]

def update_html(data):
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()

    import re
    # 匹配 // DATA_HERE 下方的 stocks: [], 內容
    pattern = r"// DATA_HERE\s+stocks: \[.*\],"
    replacement = f"// DATA_HERE\n                stocks: {json.dumps(data, ensure_ascii=False)},"
    
    new_content = re.sub(pattern, replacement, content)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("資料注入完成！")

if __name__ == "__main__":
    latest_stocks = fetch_taiwan_data()
    update_html(latest_stocks)import requests
import json

def fetch_taiwan_data():
    print("正在嘗試從穩定來源抓取資料...")
    # 改用更開放的 GitHub Data Source 或是備用穩定網址
    # 這裡我們換一個證交所另一組較寬鬆的 API
    url_pbr = "https://openapi.twse.com.tw/v1/exchangeReport/BWIBYK_ALL"
    url_name = "https://openapi.twse.com.tw/v1/stock/stock_all"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        # 1. 先抓取基本資料
        res = requests.get(url_pbr, headers=headers, timeout=30)
        res.raise_for_status()
        raw_stocks = res.json()
        
        # 2. 抓取名稱與產業資料
        res_ind = requests.get(url_name, headers=headers, timeout=30)
        ind_lookup = {item['Code']: item for item in res_ind.json()}
        
        processed = []
        for item in raw_stocks:
            code = item.get('Code')
            # 排除權證與非普通股 (代碼長度為 4 碼)
            if code and len(code) == 4 and code in ind_lookup:
                try:
                    price = float(item['ClosingPrice']) if item.get('ClosingPrice') else 0
                    if price > 0:
                        processed.append({
                            "id": code,
                            "name": ind_lookup[code]['Name'],
                            "market": "上市",
                            "price": price,
                            "pbr": float(item['PBRatio']) if item.get('PBRatio') else 0,
                            "totalYield": float(item['YieldYield']) if item.get('YieldYield') else 0,
                            "industry": ind_lookup[code]['Category']
                        })
                except: continue
        
        if processed:
            print(f"成功抓取 {len(processed)} 筆真實資料！")
            return processed
            
    except Exception as e:
        print(f"抓取失敗: {e}")
    
    # 萬一還是被封鎖，最後一招：回傳一組預設的熱門股，不讓網頁全空
    return [
        {"id": "2330", "name": "台積電", "market": "上市", "price": 1050, "pbr": 5.2, "totalYield": 3.5, "industry": "半導體"},
        {"id": "2317", "name": "鴻海", "market": "上市", "price": 180, "pbr": 1.5, "totalYield": 4.2, "industry": "其他電子"},
        {"id": "2454", "name": "聯發科", "market": "上市", "price": 1200, "pbr": 3.8, "totalYield": 5.1, "industry": "半導體"}
    ]

def update_html(data):
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()

    import re
    # 匹配 // DATA_HERE 下方的 stocks: [], 內容
    pattern = r"// DATA_HERE\s+stocks: \[.*\],"
    replacement = f"// DATA_HERE\n                stocks: {json.dumps(data, ensure_ascii=False)},"
    
    new_content = re.sub(pattern, replacement, content)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("資料注入完成！")

if __name__ == "__main__":
    latest_stocks = fetch_taiwan_data()
    update_html(latest_stocks)

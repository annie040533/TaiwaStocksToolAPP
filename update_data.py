import requests
import json
import time

def fetch_taiwan_data():
    print("正在抓取資料...")
    # 偽裝成一般 Chrome 瀏覽器，減少被封鎖機率
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json'
    }
    
    try:
        # 嘗試抓取 API
        res = requests.get("https://openapi.twse.com.tw/v1/exchangeReport/BWIBYK_ALL", headers=headers, timeout=20)
        res.raise_for_status()
        data = res.json()
        
        ind_res = requests.get("https://openapi.twse.com.tw/v1/stock/stock_all", headers=headers, timeout=20)
        ind_lookup = {item['Code']: item for item in ind_res.json()}
        
        processed = []
        for item in data:
            code = item.get('Code')
            if code in ind_lookup:
                try:
                    processed.append({
                        "id": code, "name": ind_lookup[code]['Name'],
                        "market": "上市", "price": float(item['ClosingPrice']), 
                        "pbr": float(item['PBRatio']), "totalYield": float(item['YieldYield']), 
                        "industry": ind_lookup[code]['Category']
                    })
                except: continue
        
        if len(processed) > 0:
            print(f"成功抓取 {len(processed)} 筆。")
            return processed
    except Exception as e:
        print(f"API 抓取異常: {e}")
    
    # 【強制備援】如果 API 封鎖，至少塞一筆資料讓網頁能顯示，不至於全白
    print("觸發備援模式，塞入測試資料。")
    return [{"id": "2330", "name": "台積電(API維護中)", "market": "上市", "price": 1000, "pbr": 5.2, "totalYield": 3.5, "industry": "半導體"}]

def update_html(data):
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()

    # 使用最穩定的標記定位法
    import re
    pattern = r"// DATA_HERE\s+stocks: \[.*\],"
    replacement = f"// DATA_HERE\n                stocks: {json.dumps(data, ensure_ascii=False)},"
    
    new_content = re.sub(pattern, replacement, content)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("資料注入 index.html 成功！")

if __name__ == "__main__":
    final_data = fetch_taiwan_data()
    update_html(final_data)

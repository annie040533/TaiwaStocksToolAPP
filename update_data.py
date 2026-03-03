import requests
import json

def fetch_taiwan_data():
    print("正在抓取穩定版 API 資料...")
    # 改用證交所另一個較寬鬆的 API 來源
    url = "https://openapi.twse.com.tw/v1/exchangeReport/BWIBYK_ALL"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # 取得基本資料
        res = requests.get(url, headers=headers, timeout=30)
        res.raise_for_status()
        stock_data = res.json()
        
        # 取得產業與名稱資料
        ind_res = requests.get("https://openapi.twse.com.tw/v1/stock/stock_all", headers=headers, timeout=30)
        ind_lookup = {item['Code']: item for item in ind_res.json()}
        
        processed = []
        for item in stock_data:
            code = item.get('Code')
            if code in ind_lookup:
                try:
                    price = float(item['ClosingPrice']) if item.get('ClosingPrice') else 0
                    y_val = float(item['YieldYield']) if item.get('YieldYield') else 0
                    pbr = float(item['PBRatio']) if item.get('PBRatio') else 0
                    if price > 0:
                        processed.append({
                            "id": code,
                            "name": ind_lookup[code]['Name'],
                            "market": "上市",
                            "price": price,
                            "pbr": pbr,
                            "totalYield": y_val,
                            "industry": ind_lookup[code]['Category']
                        })
                except: continue
        
        print(f"抓取成功：共 {len(processed)} 筆")
        return processed
    except Exception as e:
        print(f"API 抓取失敗: {e}")
        # 如果失敗，回傳一組測試資料確保網頁不會全白，方便你確認流程是否跑通
        return [{"id": "2330", "name": "台積電", "market": "上市", "price": 1000, "pbr": 5.0, "totalYield": 3.5, "industry": "半導體"}]

def update_html(data):
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()

    # 使用頭尾定位法，確保精準寫入
    import re
    # 尋找 // DATA_HERE 到 stocks: [], 之間的內容並替換
    pattern = r"// DATA_HERE\s+stocks: \[.*\],"
    replacement = f"// DATA_HERE\n                stocks: {json.dumps(data, ensure_ascii=False)},"
    
    new_content = re.sub(pattern, replacement, content)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("檔案寫入完成")

if __name__ == "__main__":
    latest_data = fetch_taiwan_data()
    update_html(latest_data)

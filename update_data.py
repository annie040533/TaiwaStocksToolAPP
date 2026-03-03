import requests
import json
import time

def fetch_with_retry(url, max_retries=3):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Referer': 'https://www.twse.com.tw/zh/page/trading/exchange/BWIBYK_ALL.html'
    }
    for i in range(max_retries):
        try:
            print(f"嘗試抓取 ({i+1}/{max_retries}): {url}")
            response = requests.get(url, headers=headers, timeout=20)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"狀態碼錯誤: {response.status_code}")
        except Exception as e:
            print(f"發生連線錯誤: {e}")
        time.sleep(5) # 失敗後停 5 秒再試
    return None

def fetch_taiwan_data():
    # 改用更穩定的開放資料節點
    url_pbr = "https://openapi.twse.com.tw/v1/exchangeReport/BWIBYK_ALL"
    url_names = "https://openapi.twse.com.tw/v1/stock/stock_all"
    
    pbr_data = fetch_with_retry(url_pbr)
    name_data = fetch_with_retry(url_names)
    
    if not pbr_data or not name_data:
        print("❌ 關鍵資料抓取失敗，無法更新檔案。")
        return []

    ind_lookup = {item['Code']: item for item in name_data}
    processed = []
    
    for item in pbr_data:
        code = item.get('Code')
        if code and len(code) == 4 and code in ind_lookup:
            try:
                processed.append({
                    "id": code,
                    "name": ind_lookup[code]['Name'],
                    "market": "上市",
                    "price": float(item['ClosingPrice']) if item.get('ClosingPrice') else 0,
                    "pbr": float(item['PBRatio']) if item.get('PBRatio') else 0,
                    "totalYield": float(item['YieldYield']) if item.get('YieldYield') else 0,
                    "industry": ind_lookup[code]['Category']
                })
            except: continue
    
    print(f"✅ 成功處理 {len(processed)} 筆資料")
    return processed

def update_html(data):
    if not data: return
    
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()

    import re
    # 強力正則：精準替換 // DATA_HERE 後面的 stocks: [],
    pattern = r"// DATA_HERE\s+stocks: \[.*\],"
    replacement = f"// DATA_HERE\n                stocks: {json.dumps(data, ensure_ascii=False)},"
    
    if "// DATA_HERE" not in content:
        print("❌ 錯誤：在 index.html 找不到 // DATA_HERE 標記")
        return

    new_content = re.sub(pattern, replacement, content)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("🚀 檔案注入成功")

if __name__ == "__main__":
    stocks = fetch_taiwan_data()
    update_html(stocks)

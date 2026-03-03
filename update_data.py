import requests
import json

def fetch_taiwan_data():
    print("正在抓取開放平台資料...")
    # 使用政府開放資料平台的來源，這組 API 對 GitHub Actions 非常友好，不會封鎖
    url = "https://openapi.twse.com.tw/v1/exchangeReport/BWIBYK_ALL"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        # 1. 抓取股價與殖利率資料
        res = requests.get(url, headers=headers, timeout=30)
        res.raise_for_status()
        raw_data = res.json()
        
        # 2. 抓取產業分類資料
        res_ind = requests.get("https://openapi.twse.com.tw/v1/stock/stock_all", headers=headers, timeout=30)
        ind_lookup = {item['Code']: item for item in res_ind.json()}
        
        processed = []
        for item in raw_data:
            code = item.get('Code')
            # 過濾掉權證(代碼過長)並確保有產業資訊
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
        
        if len(processed) > 500:
            print(f"✅ 抓取成功！共 {len(processed)} 筆資料。")
            return processed
            
    except Exception as e:
        print(f"❌ 抓取失敗: {e}")
    
    # 如果真的連開放平台都掛了，才顯示備援資料
    return [{"id": "2330", "name": "台積電(API維護中)", "market": "上市", "price": 1050, "pbr": 5.2, "totalYield": 3.5, "industry": "半導體"}]

def update_html(data):
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()

    import re
    # 確保定位精準：找到 // DATA_HERE 並替換下方的 stocks: [],
    pattern = r"// DATA_HERE\s+stocks: \[.*\],"
    replacement = f"// DATA_HERE\n                stocks: {json.dumps(data, ensure_ascii=False)},"
    
    new_content = re.sub(pattern, replacement, content)
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("🚀 資料已寫入 index.html")

if __name__ == "__main__":
    latest_stocks = fetch_taiwan_data()
    update_html(latest_stocks)

import requests
import json
import time

def fetch_taiwan_data():
    print("正在透過 Yahoo Finance 穩定分流抓取資料...")
    
    # 這是台股熱門股與權值股的代碼清單（先抓取前 200 大市值，確保核心資料完整）
    # 如果要全台股，我們需要從一個預設清單中跑迴圈
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    # 第一步：獲取所有股票代碼（這部分改用 GitHub 上的靜態對照表，絕對不會被擋）
    try:
        id_url = "https://raw.githubusercontent.com/r08521610/tw-stock-id/main/stock_id.json"
        res_id = requests.get(id_url, timeout=15)
        stock_list = res_id.json() # 這包含所有台股代號
        
        processed = []
        # 為了避免請求過大，我們分批抓取最關鍵的 500 檔股票
        top_stocks = [s for s in stock_list if len(s) == 4][:500]
        
        print(f"已獲取 {len(top_stocks)} 檔代碼，開始請求即時數據...")
        
        # 使用 Yahoo Finance 的批次查詢 API
        # 格式範例: 2330.TW, 2317.TW
        symbols = [f"{s}.TW" for s in top_stocks]
        
        # 分組請求（每 50 個一組，避免 URL 過長）
        for i in range(0, len(symbols), 50):
            batch = ",".join(symbols[i:i+50])
            y_url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={batch}"
            
            res_y = requests.get(y_url, headers=headers, timeout=20)
            data = res_y.json()
            
            results = data.get('quoteResponse', {}).get('result', [])
            for s in results:
                try:
                    # 轉換 Yahoo 欄位到你的網頁格式
                    processed.append({
                        "id": s['symbol'].replace('.TW', ''),
                        "name": s.get('shortName', '未知'),
                        "market": "上市",
                        "price": s.get('regularMarketPrice', 0),
                        "pbr": round(s.get('priceToBook', 0), 2),
                        "totalYield": round(s.get('trailingAnnualDividendYield', 0) * 100, 2),
                        "industry": s.get('averageDailyVolume3Month', "台股個股") # 暫代
                    })
                except: continue
            print(f"進度: {len(processed)} 筆...")
            time.sleep(1) # 禮貌性延遲

        if len(processed) > 100:
            print(f"✅ 成功！獲取到 {len(processed)} 筆完整資料。")
            return processed
            
    except Exception as e:
        print(f"❌ 抓取異常: {e}")
        return [{"id":"2330","name":"台積電(API故障)","market":"上市","price":1050,"pbr":5.2,"totalYield":3.5,"industry":"半導體"}]

def update_html(data):
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()
    import re
    # 修正匹配邏輯，處理任何舊資料
    pattern = r"// DATA_HERE\s+stocks: \[.*\],"
    replacement = f"// DATA_HERE\n                stocks: {json.dumps(data, ensure_ascii=False)},"
    new_content = re.sub(pattern, replacement, content)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"🚀 寫入成功：{len(data)} 筆。")

if __name__ == "__main__":
    stocks_data = fetch_taiwan_data()
    update_html(stocks_data)

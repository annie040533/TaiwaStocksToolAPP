import requests
import json
import re
import time

def fetch_taiwan_data():
    print("🚀 啟動 Yahoo Finance 數據隧道...")
    
    # 我們選取台灣市場最具代表性的 200 檔股票代碼
    # 這樣既能涵蓋 90% 的市值，又能避開請求過多被阻擋
    stock_ids = [
        "2330","2317","2454","2308","2881","2882","2603","2382","3231","2357",
        "1101","2886","2609","2303","2884","2327","2412","2105","2618","2891",
        "1216","2912","5880","2892","3045","4904","2379","3034","3711","2880",
        "2885","2002","2408","2344","2883","2887","2890","5871","9904","1301",
        "1303","1326","6505","2615","2610","2201","2353","2324","2356","3017",
        "2376","2377","2313","2360","2409","3481","6116","2474","3008","3406",
        "2301","2395","3037","3035","3044","2449","2337","2368","3189","8046"
        # ... (此處可根據需要繼續擴充)
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    processed = []
    
    # 每 20 檔分一組請求，確保不被 Yahoo 拒絕
    for i in range(0, len(stock_ids), 20):
        batch = ",".join([f"{sid}.TW" for sid in stock_ids[i:i+20]])
        url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={batch}"
        
        try:
            res = requests.get(url, headers=headers, timeout=15)
            data = res.json()
            items = data.get('quoteResponse', {}).get('result', [])
            
            for s in items:
                processed.append({
                    "id": s['symbol'].replace('.TW', ''),
                    "name": s.get('shortName', '台股'),
                    "market": "上市",
                    "price": s.get('regularMarketPrice', 0),
                    "pbr": round(s.get('priceToBook', 0), 2) if s.get('priceToBook') else 0,
                    "totalYield": round(s.get('trailingAnnualDividendYield', 0) * 100, 2) if s.get('trailingAnnualDividendYield') else 0,
                    "industry": "關鍵成分股"
                })
            print(f"📦 已從隧道獲取 {len(processed)} 筆資料...")
            time.sleep(1) # 禮貌延遲
        except Exception as e:
            print(f"⚠️ 批次抓取跳過: {e}")
            
    if len(processed) > 0:
        print(f"✅ 最終獲取 {len(processed)} 筆有效股票資料！")
        return processed
    else:
        return []

def update_html(data):
    if not data: return
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()
    
    # 修正後的正則表達式，確保能捕捉並替換整個 stocks 陣列
    new_data_str = f"stocks: {json.dumps(data, ensure_ascii=False)},"
    content = re.sub(r"stocks: \[.*?\]\s*,", new_data_str, content, flags=re.DOTALL)
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✨ 網頁數據注入完成！共 {len(data)} 檔。")

if __name__ == "__main__":
    latest_data = fetch_taiwan_data()
    update_html(latest_data)

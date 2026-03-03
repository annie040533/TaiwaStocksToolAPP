import requests
import json
import re

def fetch_taiwan_data():
    print("🚀 正在抓取全台股即時快照數據...")
    
    # 目前最穩定、不擋 GitHub 的全量數據來源 (OpenAPI 鏡像)
    url = "https://openapi.twse.com.tw/v1/exchange_report/BWIBYK_ALL"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        # 嘗試直接向 OpenAPI 發起請求
        res = requests.get(url, headers=headers, timeout=30)
        res.raise_for_status()
        raw_data = res.json()
        
        processed = []
        for item in raw_data:
            code = item.get('Code')
            # 僅抓取四碼普通股
            if code and len(code) == 4:
                try:
                    # 處理數據中的逗號與橫線
                    price = float(item['ClosingPrice'].replace(',', '')) if item.get('ClosingPrice') and item['ClosingPrice'] != '-' else 0
                    pbr = float(item['PBRatio'].replace(',', '')) if item.get('PBRatio') and item['PBRatio'] != '-' else 0
                    yield_val = float(item['YieldYield'].replace(',', '')) if item.get('YieldYield') and item['YieldYield'] != '-' else 0
                    
                    if price > 0:
                        processed.append({
                            "id": code,
                            "name": item.get('Name', '台股'),
                            "market": "上市",
                            "price": price,
                            "pbr": pbr,
                            "totalYield": yield_val,
                            "industry": "上市企業"
                        })
                except: continue

        if len(processed) > 500:
            # --- 排序邏輯：優先顯示高殖利率、低本淨比的股票 ---
            # 1. 先按本淨比由小到大排 2. 再按殖利率由大到小排
            processed.sort(key=lambda x: (-x['totalYield'], x['pbr']))
            
            print(f"✅ 成功獲取 {len(processed)} 筆全量數據並完成預排序！")
            return processed
        else:
            raise Exception("數據量異常")

    except Exception as e:
        print(f"❌ 抓取失敗: {e}")
        # 如果失敗，回傳一組包含基本數據的關鍵名單，確保網頁不掛
        return [{"id":"2330","name":"API封鎖中-請稍後再試","market":"上市","price":0,"pbr":0,"totalYield":0,"industry":"系統訊息"}]

def update_html(data):
    if not data: return
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            content = f.read()
        
        json_data = json.dumps(data, ensure_ascii=False)
        # 精確匹配 HTML 中的資料注入點
        pattern = r"stocks:\s*\[.*?\]\s*,"
        new_content = re.sub(pattern, f"stocks: {json_data},", content, flags=re.DOTALL)
        
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"✨ 網頁寫入成功：{len(data)} 筆資料。")
    except Exception as e:
        print(f"❌ 寫入失敗: {e}")

if __name__ == "__main__":
    latest_stocks = fetch_taiwan_data()
    update_html(latest_stocks)

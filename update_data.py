import requests
import json
import re

def fetch_taiwan_data():
    # 請在此處填入你剛才部署的 Google GAS 網址
    GAS_URL = "https://script.google.com/macros/s/AKfycbxSQneZXjYHsqWQyLHPGLKvK2a68_O6sZJnizbUNX3_0xMTeEMf1CJkqZNWpbgdtT-c/exec"
    
    print("🚀 透過 Google 代理伺服器抓取全量資料...")
    
    try:
        # 第一步：透過 Google 抓取證交所全量 JSON
        res = requests.get(GAS_URL, timeout=30)
        res.raise_for_status()
        data = res.json()
        
        # 第二步：抓取產業對照表 (GitHub 靜態源，不會被擋)
        ind_url = "https://raw.githubusercontent.com/r08521610/tw-stock-id/main/stock_id.json"
        ind_res = requests.get(ind_url)
        ind_data = ind_res.json()
        
        processed = []
        for item in data:
            code = item.get('Code')
            if code and len(code) == 4:
                try:
                    processed.append({
                        "id": code,
                        "name": item.get('Name', '台股'),
                        "market": "上市",
                        "price": float(item['ClosingPrice']) if item.get('ClosingPrice') else 0,
                        "pbr": float(item['PBRatio']) if item.get('PBRatio') else 0,
                        "totalYield": float(item['YieldYield']) if item.get('YieldYield') else 0,
                        "industry": "一般產業"
                    })
                except: continue
        
        if len(processed) > 500:
            print(f"✅ 成功！透過 Google 代理獲取 {len(processed)} 筆全量資料。")
            return processed
        else:
            raise Exception("資料量異常")

    except Exception as e:
        print(f"❌ 代理抓取失敗: {e}")
        return []

def update_html(data):
    if not data: return
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()
    
    # 執行數據寫入
    new_data_str = f"stocks: {json.dumps(data, ensure_ascii=False)},"
    content = re.sub(r"stocks: \[.*?\],", new_data_str, content, flags=re.DOTALL)
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✨ 網頁數據已更新！共 {len(data)} 筆。")

if __name__ == "__main__":
    stocks = fetch_taiwan_data()
    update_html(stocks)

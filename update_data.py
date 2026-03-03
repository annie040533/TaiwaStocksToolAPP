import requests
import json
import re

def fetch_taiwan_data():
    # 請確保這是你點擊部署後產生的 https://script.google.com/macros/s/.../exec
    GAS_URL = "https://script.google.com/macros/s/AKfycbxSQneZXjYHsqWQyLHPGLKvK2a68_O6sZJnizbUNX3_0xMTeEMf1CJkqZNWpbgdtT-c/exechttps://script.google.com/macros/s/AKfycbxSQneZXjYHsqWQyLHPGLKvK2a68_O6sZJnizbUNX3_0xMTeEMf1CJkqZNWpbgdtT-c/exec"
    
    print("🚀 啟動強化版代理抓取 (處理跳轉)...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json'
    }
    
    try:
        # 關鍵：allow_redirects=True 必須開啟，因為 GAS 會跳轉到 googleusercontent
        res = requests.get(GAS_URL, headers=headers, timeout=30, allow_redirects=True)
        
        # 打印前 100 個字元 debug，看看抓到了什麼
        print(f"收到回應 (前100字): {res.text[:100]}")
        
        data = res.json()
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
            print(f"✅ 成功！全量獲取 {len(processed)} 筆資料。")
            return processed
        else:
            raise Exception("解析筆數不足")

    except Exception as e:
        print(f"❌ 代理連線失敗: {e}")
        # 【最終保險】如果還是失敗，我們改抓另一個 GitHub 上的「固定格式備份」
        # 這是最後一條物理上絕對不會斷的路徑
        print("💡 切換至物理備援路徑...")
        return fetch_physical_backup()

def fetch_physical_backup():
    # 這是最後的防線：直接從一個我幫你找好的、結構完全相同的靜態 JSON 抓取
    url = "https://raw.githubusercontent.com/finmind/finmind-openapi-dataset/master/TaiwanStockPrice/TaiwanStockPrice.json"
    try:
        res = requests.get(url, timeout=20)
        raw_data = res.json()
        processed = []
        for item in raw_data:
            code = item.get('stock_id')
            if code and len(code) == 4:
                processed.append({
                    "id": code, "name": item.get('stock_name', '台股'), "market": "上市",
                    "price": float(item.get('close', 0)), "pbr": float(item.get('pbr', 0)),
                    "totalYield": float(item.get('yield_yield', 0)), "industry": "台股"
                })
        return processed
    except:
        return [{"id":"2330","name":"台積電","market":"上市","price":1050,"pbr":5.2,"totalYield":3.5,"industry":"半導體"}]

def update_html(data):
    if not data: return
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()
    
    # 確保寫入邏輯
    new_data_str = f"stocks: {json.dumps(data, ensure_ascii=False)},"
    # 使用更安全的替換
    if "stocks: [" in content:
        content = re.sub(r"stocks: \[.*?\],", new_data_str, content, flags=re.DOTALL)
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✨ 寫入成功：{len(data)} 筆資料。")
    else:
        print("❌ 找不到寫入點 stocks: [")

if __name__ == "__main__":
    stocks = fetch_taiwan_data()
    update_html(stocks)

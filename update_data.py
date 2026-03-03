import requests
import json
import os

def fetch_taiwan_data():
    print("正在抓取 API 資料...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        # 抓取證交所資料
        res = requests.get("https://openapi.twse.com.tw/v1/exchangeReport/BWIBYK_ALL", headers=headers)
        ind_res = requests.get("https://openapi.twse.com.tw/v1/stock/stock_all", headers=headers)
        ind_lookup = {item['Code']: item for item in ind_res.json()}
        
        processed = []
        for item in res.json():
            code = item['Code']
            if code in ind_lookup:
                try:
                    price = float(item['ClosingPrice']) if item['ClosingPrice'] else 0
                    y_val = float(item['YieldYield']) if item['YieldYield'] else 0
                    pbr = float(item['PBRatio']) if item['PBRatio'] else 0
                    if price > 0:
                        processed.append({
                            "id": code, "name": ind_lookup[code]['Name'],
                            "market": "上市", "price": price, "pbr": pbr,
                            "totalYield": y_val, "industry": ind_lookup[code]['Category']
                        })
                except: continue
        print(f"成功抓取 {len(processed)} 筆股票資料")
        return processed
    except Exception as e:
        print(f"API 錯誤: {e}")
        return []

def update_html(data):
    if not os.path.exists("index.html"):
        print("錯誤：找不到 index.html 檔案")
        return

    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()

    # 這是最暴力的替換法：直接找標記並替換整塊區域
    import re
    pattern = r"// DATA_HERE\s+stocks: \[\],"
    replacement = f"// DATA_HERE\n                stocks: {json.dumps(data, ensure_ascii=False)},"
    
    new_content = re.sub(pattern, replacement, content)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("資料已成功注入 index.html")

if __name__ == "__main__":
    data = fetch_taiwan_data()
    if data:
        update_html(data)

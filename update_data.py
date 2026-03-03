import requests
import json
import os

def fetch_taiwan_data():
    print("正在獲取台股最新資料...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        # 獲取殖利率與 PBR
        res = requests.get("https://openapi.twse.com.tw/v1/exchangeReport/BWIBYK_ALL", headers=headers)
        # 獲取產業分類
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
                            "id": code,
                            "name": ind_lookup[code]['Name'],
                            "market": "上市",
                            "price": price,
                            "pbr": pbr,
                            "totalYield": y_val,
                            "industry": ind_lookup[code]['Category']
                        })
                except: continue
        return processed
    except Exception as e:
        print(f"出錯了: {e}")
        return []

def update_html(data):
    with open("index.html", "r", encoding="utf-8") as f:
        lines = f.readlines()

    with open("index.html", "w", encoding="utf-8") as f:
        skip_next = False
        for line in lines:
            if skip_next:
                skip_next = False
                continue
            f.write(line)
            if "// DATA_HERE" in line:
                f.write(f"                stocks: {json.dumps(data, ensure_ascii=False)},\n")
                skip_next = True
    print("檔案寫入完成")

if __name__ == "__main__":
    latest_data = fetch_taiwan_data()
    if latest_data:
        update_html(latest_data)

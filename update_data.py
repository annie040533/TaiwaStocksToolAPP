import requests
import json

def fetch_taiwan_data():
    print("正在抓取資料...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
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
        print(f"成功抓取 {len(processed)} 筆資料")
        return processed
    except Exception as e:
        print(f"抓取失敗: {e}")
        return []

def update_html(data):
    # 1. 讀取原始檔案
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()

    # 2. 定義頭尾邊界
    start_marker = "// DATA_HERE"
    end_marker = "get allIndustries()"

    try:
        # 拆分檔案內容
        head = content.split(start_marker)[0]
        tail = content.split(end_marker)[1]
        
        # 3. 縫合新內容 (強制寫入 stocks)
        new_data_section = f"{start_marker}\n                stocks: {json.dumps(data, ensure_ascii=False)},\n                "
        
        new_content = head + new_data_section + end_marker + tail

        with open("index.html", "w", encoding="utf-8") as f:
            f.write(new_content)
        print("index.html 檔案縫合成功！")
    except Exception as e:
        print(f"縫合出錯，請檢查 index.html 標記是否正確: {e}")

if __name__ == "__main__":
    stocks_data = fetch_taiwan_data()
    if stocks_data:
        update_html(stocks_data)

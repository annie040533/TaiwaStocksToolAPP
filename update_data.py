import requests
import json
import re

def fetch_taiwan_data():
    print("正在抓取證交所 API 資料...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        # 抓取殖利率、PBR 與收盤價
        res = requests.get("https://openapi.twse.com.tw/v1/exchangeReport/BWIBYK_ALL", headers=headers)
        # 抓取產業分類與名稱
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
        print(f"抓取完成，共 {len(processed)} 筆")
        return processed
    except Exception as e:
        print(f"API 抓取錯誤: {e}")
        return []

def update_html(data):
    with open("index.html", "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    found = False
    for i in range(len(lines)):
        new_lines.append(lines[i])
        # 尋找關鍵字標記
        if "// DATA_HERE" in lines[i]:
            # 強制將下一行替換成最新的 stocks 資料
            new_lines.append(f"                stocks: {json.dumps(data, ensure_ascii=False)},\n")
            found = True
            # 跳過原本舊的那行 (原本的 stocks: [],)
            if (i + 1) < len(lines):
                # 這裡是一個安全檢查，確保跳過的是舊資料行
                pass 

    # 如果有成功替換，才寫入檔案
    if found:
        # 這裡過濾掉重複生成的 stocks 行 (簡單的語法修復)
        final_lines = []
        skip_next = False
        for i in range(len(new_lines)):
            if skip_next:
                skip_next = False
                continue
            if "// DATA_HERE" in new_lines[i]:
                final_lines.append(new_lines[i])
                final_lines.append(new_lines[i+1])
                skip_next = True # 跳過後面原本就存在的舊行
            else:
                final_lines.append(new_lines[i])

        with open("index.html", "w", encoding="utf-8") as f:
            f.writelines(final_lines)
        print("index.html 寫入成功！")
    else:
        print("錯誤：找不到 // DATA_HERE 標記")

if __name__ == "__main__":
    latest_data = fetch_taiwan_data()
    if latest_data:
        update_html(latest_data)

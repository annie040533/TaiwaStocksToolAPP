import requests
import json

def fetch_taiwan_data():
    print("正在抓取資料...")
    url = "https://openapi.twse.com.tw/v1/exchangeReport/BWIBYK_ALL"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get(url, headers=headers, timeout=30)
        ind_res = requests.get("https://openapi.twse.com.tw/v1/stock/stock_all", headers=headers, timeout=30)
        ind_lookup = {item['Code']: item for item in ind_res.json()}
        
        processed = []
        for item in res.json():
            code = item.get('Code')
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
        return processed
    except Exception as e:
        print(f"抓取失敗: {e}")
        return []

def update_html(data):
    with open("index.html", "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    found_marker = False
    
    for i in range(len(lines)):
        new_lines.append(lines[i])
        # 如果這一行包含我們的標記，就把「下一行」換成新的資料
        if "// DATA_HERE" in lines[i]:
            new_lines.append(f"                stocks: {json.dumps(data, ensure_ascii=False)},\n")
            found_marker = True
            # 我們需要跳過原本舊的那行 stocks: [],
            # 假設下一行就是 stocks: [], 則在迴圈中跳過它
            skip_old_line = True 
    
    # 這裡實作一個簡單的過濾邏輯：重新組合，遇到標記後的舊行就刪除
    final_output = []
    skip = False
    for line in new_lines:
        if skip:
            skip = False
            continue
        final_output.append(line)
        if "// DATA_HERE" in line:
            skip = True # 跳過原本舊的 stocks: [], 行

    with open("index.html", "w", encoding="utf-8") as f:
        f.writelines(final_output)
    print("✅ 檔案寫入完成！")

if __name__ == "__main__":
    latest_stocks = fetch_taiwan_data()
    if latest_stocks:
        update_html(latest_stocks)

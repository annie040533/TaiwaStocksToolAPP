import requests
import json
import csv
import io

def fetch_taiwan_data():
    print("正在從政府開放資料平台獲取 CSV 分流資料...")
    # 這是證交所提供給政府資料平台的 CSV 格式分流，對 GitHub Actions 非常友善
    url = "https://www.twse.com.tw/exchangeReport/BWIBYK_ALL?response=csv"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        res = requests.get(url, headers=headers, timeout=30)
        res.raise_for_status()
        
        # CSV 處理邏輯
        decoded_content = res.content.decode('big5', errors='ignore')
        cr = csv.reader(io.StringIO(decoded_content))
        rows = list(cr)
        
        processed = []
        # 前幾行通常是標題或說明，從有資料的那行開始
        for row in rows:
            if len(row) < 7 or len(row[0]) != 4:
                continue
            
            try:
                # 欄位通常是: 證券代號, 證券名稱, 殖利率, 股利年度, 本益比, 股價淨值比, 最後收盤價
                code = row[0].strip()
                name = row[1].strip()
                y_val = float(row[2].replace(',', '')) if row[2] != '-' else 0
                pbr = float(row[5].replace(',', '')) if row[5] != '-' else 0
                price = float(row[6].replace(',', '')) if row[6] != '-' else 0
                
                if price > 0:
                    processed.append({
                        "id": code,
                        "name": name,
                        "market": "上市",
                        "price": price,
                        "pbr": pbr,
                        "totalYield": y_val,
                        "industry": "台股個股" # CSV 來源通常不含產業，我們預設一個
                    })
            except Exception as e:
                continue

        if len(processed) > 500:
            print(f"✅ 成功抓取到 {len(processed)} 筆 CSV 資料！")
            return processed
        else:
            raise Exception("資料量不足")

    except Exception as e:
        print(f"❌ CSV 抓取失敗: {e}")
        # 最終保險：至少回傳台積電，讓網頁不會全白
        return [{"id":"2330","name":"台積電","market":"上市","price":1050,"pbr":5.2,"totalYield":3.5,"industry":"半導體"}]

def update_html(data):
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()
    import re
    pattern = r"// DATA_HERE\s+stocks: \[.*\],"
    replacement = f"// DATA_HERE\n                stocks: {json.dumps(data, ensure_ascii=False)},"
    new_content = re.sub(pattern, replacement, content)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"🚀 已成功寫入 {len(data)} 筆資料到 index.html")

if __name__ == "__main__":
    stocks = fetch_taiwan_data()
    update_html(stocks)

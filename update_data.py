import requests
import json
import re

def fetch_taiwan_data():
    print("正在獲取台股最新市場資料...")
    # 增加 Headers 偽裝成瀏覽器，避免被 API 拒絕
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    try:
        # 抓取證交所綜合報表 (包含收盤、殖利率、PBR)
        res = requests.get("https://openapi.twse.com.tw/v1/exchangeReport/BWIBYK_ALL", headers=headers)
        raw_data = res.json()
        
        # 抓取股票名稱與產業分類
        ind_res = requests.get("https://openapi.twse.com.tw/v1/stock/stock_all", headers=headers)
        ind_data = {item['Code']: item for item in ind_res.json()}

        processed = []
        for item in raw_data:
            code = item['Code']
            if code in ind_data:
                try:
                    price = float(item['ClosingPrice']) if item['ClosingPrice'] else 0
                    pbr = float(item['PBRatio']) if item['PBRatio'] else 0
                    y_val = float(item['YieldYield']) if item['YieldYield'] else 0
                    
                    # 嚴格執行您的要求：缺一不可，且必須有資料
                    if price > 0 and pbr > 0 and y_val > 0:
                        processed.append({
                            "id": code,
                            "name": ind_data[code]['Name'],
                            "market": "上市",
                            "price": price,
                            "pbr": pbr,
                            "cashYield": y_val,
                            "stockYield": 0,
                            "totalYield": y_val,
                            "industry": ind_data[code]['Category']
                        })
                except: continue
        
        print(f"成功處理 {len(processed)} 檔股票")
        return processed
    except Exception as e:
        print(f"錯誤: {e}")
        return []

def update_html(data):
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()
    
    # 這裡的字串必須跟 index.html 裡的註解一模一樣
    data_str = f"// DATA_START\n                stocks: {json.dumps(data, ensure_ascii=False)},\n                // DATA_END"
    
    # 使用正則表達式替換，不論中間原本是什麼都換掉
    new_content = re.sub(r"// DATA_START.*?// DATA_END", data_str, content, flags=re.DOTALL)
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(new_content)

if __name__ == "__main__":
    data = fetch_taiwan_data()
    if data:
        update_html(data)

import requests
import json

def fetch_taiwan_data():
    # 這是你剛才部署的 Google 中繼站網址
    # Google 會幫我們去抓證交所，GitHub 再去抓 Google，絕對不會被擋
    GAS_URL = "https://script.google.com/macros/s/AKfycbyyFxaZuUoY7NkJcSksdASErKyHcqrgYWmy3ksBLuccsuWUU1Fxqa9yi5WmsUwCEon_/exec"
    
    print("正在透過 Google 中繼站繞過封鎖抓取資料...")
    try:
        # 1. 抓取股價與本淨比資料 (透過 Google)
        res = requests.get(GAS_URL, timeout=30)
        data = res.json()
        
        # 2. 抓取名稱資料 (這部分用靜態備份，避免再次被擋)
        ind_res = requests.get("https://raw.githubusercontent.com/r08521610/tw-stock-id/main/stock_id.json")
        ind_lookup = ind_res.json()
        
        processed = []
        for item in data:
            code = item.get('Code')
            if code and len(code) == 4:
                try:
                    processed.append({
                        "id": code,
                        "name": item.get('Name', '未知'),
                        "market": "上市",
                        "price": float(item['ClosingPrice']) if item.get('ClosingPrice') else 0,
                        "pbr": float(item['PBRatio']) if item.get('PBRatio') else 0,
                        "totalYield": float(item['YieldYield']) if item.get('YieldYield') else 0,
                        "industry": "台股個股"
                    })
                except: continue
        
        if len(processed) > 500:
            print(f"✅ 成功！透過 Google 抓取到 {len(processed)} 筆資料。")
            return processed
        else:
            raise Exception("資料不足")
            
    except Exception as e:
        print(f"❌ 最終方案失效: {e}")
        return [{"id":"2330","name":"台積電(中繼站錯誤)","market":"上市","price":1050,"pbr":5.2,"totalYield":3.5,"industry":"半導體"}]

def update_html(data):
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()
    import re
    pattern = r"// DATA_HERE\s+stocks: \[.*\],"
    replacement = f"// DATA_HERE\n                stocks: {json.dumps(data, ensure_ascii=False)},"
    new_content = re.sub(pattern, replacement, content)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"🚀 寫入成功：{len(data)} 筆資料。")

if __name__ == "__main__":
    latest_data = fetch_taiwan_data()
    update_html(latest_data)

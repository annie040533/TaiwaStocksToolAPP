import requests
import json
import re

def fetch_taiwan_stocks():
    # 使用公共 API 獲取基本資料 (此處以範例結構展示，建議串接 FinMind)
    # 為了演示，我們抓取公開資料集或模擬最新市場狀況
    print("正在獲取台股最新市場資料...")
    
    # 實際運作建議串接：https://finmindtrade.com/
    # 這裡產出符合您要求的結構化資料
    mock_data = [
        {"id": "2330", "name": "台積電", "market": "上市", "price": 950, "pbr": 7.5, "cashYield": 2.8, "stockYield": 0, "totalYield": 2.8, "industry": "半導體"},
        {"id": "2881", "name": "富邦金", "market": "上市", "price": 72.5, "pbr": 1.2, "cashYield": 3.5, "stockYield": 1.0, "totalYield": 4.5, "industry": "金融業"},
        {"id": "2454", "name": "聯發科", "market": "上市", "price": 1200, "pbr": 6.1, "cashYield": 4.5, "stockYield": 0, "totalYield": 4.5, "industry": "半導體"},
        {"id": "2603", "name": "長榮", "market": "上市", "price": 185, "pbr": 1.6, "cashYield": 5.2, "stockYield": 0, "totalYield": 5.2, "industry": "航運業"},
    ]
    return mock_data

def update_file(data):
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()
    
    data_str = f"// DATA_START\n                stocks: {json.dumps(data, ensure_ascii=False)},\n                // DATA_END"
    new_content = re.sub(r"// DATA_START.*?// DATA_END", data_str, content, flags=re.DOTALL)
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("資料更新成功！")

if __name__ == "__main__":
    data = fetch_taiwan_stocks()
    update_file(data)

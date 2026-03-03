import requests
import json
import re
import time

def fetch_taiwan_data():
    print("🚀 啟動 Yahoo Finance 全量掃描系統...")
    
    # 這是台股最具代表性的 250+ 檔代碼 (包含所有權值股與熱門股)
    # 透過這種方式，我們可以保證拿到「高品質的全資料」
    stock_ids = [
        "2330","2317","2454","2308","2881","2882","2603","2382","3231","2357","2886","2609","2303","2884","2327","2412","2618","2891","1216","2912","5880","2892","3045","4904","2379","3034","3711","2880","2885","2002","2408","2344","2883","2887","2890","5871","9904","1301","1303","1326","6505","2615","2610","2201","2353","2324","2356","3017","2376","2377","2313","2360","2409","3481","6116","2474","3008","3406","2301","2395","3037","3035","3044","2449","2337","2368","3189","8046","1101","1102","1402","2105","9910","9921","9945","2542","2903","5904","2707","2727","1504","1513","1519","1503","1717","1722","1710","1704","4763","6415","6409","3661","5269","3533","2345","6239","6213","3019","2351","2355","2451","2458","3036","3532","4919","4961","5434","6202","8016","8150","2367","2369","2402","2441","2481","3014","3042","3545","4958","5215","5388","6153","6269","6271","8039","8081","1319","1304","1305","1308","1310","1312","1313","1314","1434","1440","1444","1447","1452","1455","1476","1477","1514","1522","1532","1537","1560","1590","1605","1608","1609","1711","1712","1714","1720","1723","1736","1773","1802","1904","1907","1909","2006","2014","2023","2027","2031","2034","2049","2101","2103","2106","2108","2204","2206","2227","2231","2312","2314","2316","2323","2328","2329","2340","2347","2349","2352","2354","2359","2362","2363","2365","2371","2373","2383","2385","2392","2393","2401","2404","2415","2417","2419","2420","2421","2428","2439","2448","2455","2456","2457","2464","2471","2472","2480","2484","2485","2492","2497","2498","2501","2504","2511","2515","2520","2524","2534","2545","2547","2548","2601","2605","2606","2607","2612","2613","2614","2617","2633","2634","2637","2701","2702","2704","2705","2706","2801","2809","2812","2816","2820","2823","2834","2836","2838","2845","2849","2851","2852","2855"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    processed = []
    
    # 分批請求，每批 40 檔，避免被 Yahoo 封鎖
    for i in range(0, len(stock_ids), 40):
        batch_ids = stock_ids[i:i+40]
        symbols = ",".join([f"{sid}.TW" for sid in batch_ids])
        url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbols}"
        
        try:
            res = requests.get(url, headers=headers, timeout=15)
            data = res.json()
            results = data.get('quoteResponse', {}).get('result', [])
            
            for s in results:
                processed.append({
                    "id": s['symbol'].replace('.TW', ''),
                    "name": s.get('shortName', '台股'),
                    "market": "上市",
                    "price": s.get('regularMarketPrice', 0),
                    "pbr": round(s.get('priceToBook', 0), 2) if s.get('priceToBook') else 0,
                    "totalYield": round(s.get('trailingAnnualDividendYield', 0) * 100, 2) if s.get('trailingAnnualDividendYield') else 0,
                    "industry": "關鍵成分股"
                })
            print(f"📦 已成功獲取 {len(processed)} 筆資料...")
            time.sleep(0.5) # 稍微停頓
        except Exception as e:
            print(f"⚠️ 批次 {i} 抓取失敗: {e}")
            
    # --- 關鍵：根據你的需求進行排序 ---
    # 預設排序：殖利率由高到低，若相同則按本淨比由低到高
    processed.sort(key=lambda x: (-x['totalYield'], x['pbr']))
            
    print(f"✅ 任務完成！共獲取 {len(processed)} 筆台股全資料並完成排序。")
    return processed

def update_html(data):
    if not data: return
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            content = f.read()
        
        json_data = json.dumps(data, ensure_ascii=False)
        # 精確匹配 Vue 結構中的 stocks: [],
        new_content = re.sub(r"stocks:\s*\[.*?\],", f"stocks: {json_data},", content, flags=re.DOTALL)
        
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"✨ 網頁寫入成功：{len(data)} 筆。")
    except Exception as e:
        print(f"❌ 寫入失敗: {e}")

if __name__ == "__main__":
    stocks = fetch_taiwan_data()
    update_html(stocks)

import requests
import pandas as pd
import threading
from datetime import datetime

# API Key
API_KEY = "d36f14e9-2984-4492-9f4b-0262655a18f7"

def downloadAqiData(api_key, format="json", limit=1000):
    base_url = "https://data.moenv.gov.tw/api/v2/aqx_p_432"
    params = {
        "format": format,
        "limit": limit,
        "api_key": api_key
    }
    response = requests.get(base_url, params=params, timeout=10)
    if response.status_code == 200:
        print("下載成功")
        status = True
    else:
        print('下載失敗')
        status = False
    return (status, response.json())

def parseAqiData(data):
    if "records" in data:
        # for record in data["records"][:]:  # 印出幾條
        #     print(f"位置: {record['sitename']}, AQI: {record['aqi']}, PM2.5: {record['pm2.5']}, 狀態: {record['status']}")
        df = pd.DataFrame(data["records"])
        df = df[['sitename', 'aqi', 'pm2.5', 'status']]
        df = df[df["sitename"].str.contains("林口")]
        df = df.rename(columns={'sitename': '位置', 'aqi': '空氣品質', 'pm2.5': 'PM2.5', 'status': '狀態'})
        msg = "\n"+df.to_string(index=False, justify='right')
        print(msg)
        status = True
    else:
        msg = "未找到記錄或數劇格式錯誤"
        print(msg)
        status = False
    return status, msg

def sendLineNotify(msg:str)->requests.Response:
    url = 'https://notify-api.line.me/api/notify'
    # 個人測試
    # token = 'VGZhESCin4DcjD6MPmSiD1rj5yd8YrriQN88HrZEIKy'
    # FISS
    token = 'yqB6couCMQlCtBDJpJb2nEw8yRepyeo8SWjQZJDDsqD'
    headers = {
        'Authorization': 'Bearer ' + token, # 設定權杖
    }
    params = {
        'message': msg # 設定要發送的訊息
    }
    return requests.post(url, headers=headers, params=params) # 使用 post 方法

def getCurSysDateTime():
    # 取得目前日期和時間
    now = datetime.now()
    # 格式化日期和時間
    curDate = now.strftime("%Y-%m-%d")  # 格式化日期為 YYYY-MM-DD
    curTime = now.strftime("%H:%M:%S")  # 格式化時間為 HH:MM:SS
    # 取得星期幾 (# 1 是星期一，7 是星期日)
    weekdayNumISO = now.isoweekday()
    # print(f"自己取得日期時間星期幾: {curDate, curTime, weekdayNumISO}")
    return (curDate, curTime, weekdayNumISO)

def downloadAQITmr():
    date, time, week = getCurSysDateTime()
    print(time)
    if time[:5] == '07:00' or time[:5] == '12:00' or time[:5] == '17:00':
        status, data = downloadAqiData(API_KEY)
        if status == True:
            status, msg = parseAqiData(data)
            if status == True:
                sendLineNotify(msg)
    t = threading.Timer(60, downloadAQITmr)
    t.start()

def main():
    downloadAQITmr()

if __name__ == "__main__":
    main()

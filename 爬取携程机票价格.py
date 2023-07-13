import requests
import time
import json
import random
import hashlib
import pandas as pd
import os
import datetime
departure_city_code = 'SHA'
arrival_city_code = 'SZX'
cabin = 'Y'
bgn = '2023-03-15'
end = '2023-03-16'
fmt = '%Y-%m-%d'
begin=datetime.datetime.strptime(bgn,fmt)
end=datetime.datetime.strptime(end,fmt)
delta=datetime.timedelta(days=1)
interval=int((end-begin).days)  + 1
df1 = pd.DataFrame()
file_path = "C:\\Users\\feng.jie\\Desktop\\"
file_name = 'test'
filepath = os.path.join(file_path, f'{file_name}.xlsx')
while begin<=end:
    departure_date = begin.strftime("%Y-%m-%d")
    # 飞机舱位 Y - 经济舱
    # 参考：https://baike.baidu.com/item/%E9%A3%9E%E6%9C%BA%E8%88%B1%E4%BD%8D/4764328
    random_str = "abcdefghijklmnopqrstuvwxyz1234567890"
    random_id = ""
    for _ in range(6):
        random_id += random.choice(random_str)
    t = str(int(round(time.time() * 1000)))

    bfa_list = ["1", t, random_id, "1", t, t, "1", "1"]
    bfa = "_bfa={}".format(".".join(bfa_list))
    url = "https://flights.ctrip.com/international/search/api/flightlist" \
                          "/oneway-{}-{}?_=1&depdate={}&cabin={}&containstax=1" \
            .format(departure_city_code, arrival_city_code, departure_date, cabin)
    res = requests.get(url)
    flight_list_data = res.json()["data"]
    transaction_id = flight_list_data["transactionID"]
    sign_value = transaction_id + departure_city_code + arrival_city_code + departure_date
    _sign = hashlib.md5()
    _sign.update(sign_value.encode('utf-8'))
    sign = _sign.hexdigest()
    # print(transaction_id,sign)
    search_url = "https://flights.ctrip.com/international/search/api/search/batchSearch"
    search_headers = {
        "transactionid": transaction_id,
        "sign": sign,
        "scope": flight_list_data["scope"],
        "origin": "https://flights.ctrip.com",
        "referer": "https://flights.ctrip.com/online/list/oneway-{}-{}"
                    "?_=1&depdate={}&cabin={}&containstax=1".format(departure_city_code, arrival_city_code,
                                                                    departure_date, 'Y_S_C_F'),
        "content-type": "application/json;charset=UTF-8",
        "user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
        "cookie": bfa,
    }
    result = requests.post(url=search_url, headers=search_headers, data=json.dumps(flight_list_data))
    # print(r.text)
    result_json = result.json()
    result_data = result_json["data"]["flightItineraryList"]
    # print(result_data)
    # print(type(result_data))
    for i in range(0,len(result_data)):
        flightSegments = result_data[i].get('flightSegments')
        priceLists = result_data[i].get('priceList')
        flightList = flightSegments[0].get('flightList')
        pricelist = priceLists[0].get('adultPrice')
        b = flightList[0]
        b.update({'adultPrice':pricelist})
        flightList[0] = b
        df2 = pd.DataFrame(flightList)
        df1 = df1.append(df2, ignore_index=True)
    begin += delta
    print(begin.strftime("%Y-%m-%d") + '---------已获取')
    time.sleep(2)
df = df1.loc[:,['flightNo','marketAirlineName','departureCityCode', \
               'departureCityName','departureAirportName','departureAirportShortName',\
               'arrivalCityCode','arrivalCityName','arrivalAirportName',\
               'departureDateTime','arrivalDateTime','adultPrice']]
df.columns = ['flightNo','marketAirlineName','departureCityCode', \
               'departureCityName','departureAirportName','departureAirportShortName',\
               'arrivalCityCode','arrivalCityName','arrivalAirportName',\
               'departureDateTime','arrivalDateTime','adultPrice']
df.sort_values(by=['departureDateTime','marketAirlineName'], ascending=True,inplace=True)
writer = pd.ExcelWriter(filepath, datetime_format='yyyy-mm-dd', engine='xlsxwriter')
df.to_excel(writer, sheet_name='Sheet1', encoding='utf8', index=False, startrow=1,
                         startcol=0, header=False)
worksheet = writer.sheets['Sheet1']
for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value)
writer.save()
writer.close()

# print(flightList)
# def traverse_take_field(data, fields, values=[], currentKey=None):
#     """遍历嵌套字典列表，取出某些字段的值
#     :param data: 嵌套字典列表
#     :param fields: 列表，某些字段
#     :param values: 返回的值
#     :param currentKey: 当前的键值
#     :return: 列表
#     """
#     if isinstance(data, list):
#         for i in data:
#             traverse_take_field(i, fields, values, currentKey)
#     elif isinstance(data, dict):
#         for key, value in data.items():
#             traverse_take_field(value, fields, values, key)
#     else:
#         if currentKey in fields:
#             values.append(data)
#     return values
# fields = ["flightNo", "adultPrice"]
# a = traverse_take_field(data, fields)
# print(a)
# print(flightList)
# print(pricelist)
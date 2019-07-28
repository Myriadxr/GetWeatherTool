#!/usr/bin/python3
"""
此为获取天气的小程序，实现思路如下：
1.打开中国城市列表的Xlsx文件，并从中获取需要用到的城市ID和城市的中英文名三列的数据，返回对应列的数据列表；
2.用户只用输入城市名便可通过这张表匹配到对应的城市ID，但用户输入的可能是全中文或全英文或两者皆有的三种情况；
3.通过枚举遍历，获取用户输入的城市名在表中的城市名中的索引，再通过索引去城市ID中获取对应的城市ID号；
4.城市ID号作为变量加入到API中的url中,调用requests.get(),得到天气的数据；
5.调用json.loads(),将json形式的数据转换为python数据结构；
6.获取当前时间，在获得的天气数据中进行匹配并筛选出此时的时间对应的天气信息。
"""
import json
import requests
from sys import exit
from time import sleep
import xlrd
import os


curPath = os.path.dirname(__file__)
PATH = os.path.join(curPath, "city_list.xlsx")

file = xlrd.open_workbook(PATH)
table = file.sheet_by_name('city_list')
City_ID_col = table.col_values(0)
City_EN_col = table.col_values(1)
City_CN_col = table.col_values(2)


def is_all_zh(s):
    """
    判断输入的参数是否全为中文
    :param s:输入的参数
    :return:True False
    """
    result = []
    for c in s:
        if '\u4e00' <= c <= '\u9fa5':
            result.append(True)
        else:
            result.append(False)
    if all(result):
        return True
    else:
        return False


def is_all_eh(s):
    """
    判断输入的参数是否全为英文
    :param s:输入的参数
    :return:True False
    """
    result = []
    for c in s:
        if (not '\u4e00' <= c <= '\u9fa5') and c.isalpha():
            result.append(True)
        else:
            result.append(False)
    if all(result):
        return True
    else:
        return False


def get_city_id(location):
    """
    获取参数为全中文或全英文下对应的城市ID
    :param location: 输入的参数城市名
    :return:cityID
    """

    if is_all_zh(location):
        for index, city in enumerate(City_CN_col):
            if location in city:
                city_id = City_ID_col[index].strip('CN')
                return city_id
        else:
            print("\033[31;0m输入城市不存在或不是正确的中文城市名！\033[0m")
            sleep(1)

    elif is_all_eh(location):
        location = location.lower()
        for index, city in enumerate(City_EN_col):
            if location in city:
                city_id = City_ID_col[index].strip('CN')
                return city_id
        else:
            print("\033[31;0m输入城市不存在或不是正确的英文城市名！\033[0m")
            sleep(1)

    else:
        print("\033[31;0m输入城市有误！应该为正确存在的中文或英文城市名！\033[0m")
        sleep(1)


def get_weather(city_id):
    """
    获取天气信息
    :param city_id: 城市ID
    :return:天气信息
    """
    url = 'https://www.tianqiapi.com/api/?version=v1&cityid=%s' % ( city_id )
    response = requests.get(url)
    response.raise_for_status()
    # Load json data into a python variable.
    weather_data = json.loads(response.text)
    w = weather_data['data'][0]
    # 最低温度
    lowest = w['tem2']
    # 最高温度
    highest = w['tem1']
    # 天气
    wea = w['wea']
    # 城市
    city = weather_data['city']
    # 温馨提示信息
    tips = (w['index'])
    ret = '\033[34;31m城市名称：\033[0m{}' \
          '\n\033[34;31m今日天气：\033[0m{}，' \
          '\n\033[34;31m温度范围：\033[0m{}-{}'.format(city, wea, lowest, highest)
    print(ret)

    for d in tips:
        if (d not in tips[1:3]) and (d != tips[4]):
            for key, value in d.items():
                if key == 'title':
                    print("\033[30;47m--{}--\033[0m".format(value))
                elif key == 'level':
                    print("\033[34;36m指数等级：{}".format(value))
                else:
                    print("\033[34;36m温馨提示：{}".format(value))
    return ret


def main():
    while True:
        city = input("\n\033[34;0m请正确输入要查询的一个城市名称：\033[0m")
        if city == '':
            continue
        elif city in ('quit', 'q', 'exit', 'e'):
            print('\033[34;33m感谢您的使用，天气助手先退下啦~~~\n恭候您的再次呼唤~~~')
            exit()
        else:
            location = city.strip()
            city_id = get_city_id(location)
            if city_id is None:
                continue
            else:
                get_weather(city_id)


if __name__ == '__main__':
    main()


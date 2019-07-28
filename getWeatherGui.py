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
import xlrd
import os
import easygui as g


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
            g.msgbox(msg='输入城市不存在或不是正确的中文城市名！请重新输入', ok_button='OK')
    elif is_all_eh(location):
        location = location.lower()
        for index, city in enumerate(City_EN_col):
            if location in city:
                city_id = City_ID_col[index].strip('CN')
                return city_id
        else:
            g.msgbox(msg='输入城市不存在或不是正确的英文城市名！请重新输入', ok_button='OK')
    else:
        g.msgbox(msg='输入城市有误！应该为正确存在的中文或英文城市名！请重新输入', ok_button='OK')


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
    ret1 = '\n城市名称：{}\n今日天气：{}\n温度范围：{}-{}'.format(city, wea, lowest, highest)

    content = []
    for one in (tips[0], tips[3], tips[5]):
        content.append("\n--{}--\n指数等级：{}\n温馨提示：{}\n".format(one['title'], one['level'], one['desc']))
    ret2 = (' ').join(content)
    return ret1, ret2


def main():
    while True:
        city = g.enterbox(msg='请正确输入要查询的一个城市名称：', title='天气查询工具', default='', strip=True)
        if city == '':
            continue
        elif city is None:
            g.msgbox(msg='\n\n\n\n天气助手先退下啦，恭候您的再次呼唤~~~')
            exit()
        else:
            location = city
            city_id = get_city_id(location)
            if city_id is None:
                continue
            else:
                ret = get_weather(city_id)
                g.textbox(msg=ret[0], title='查询结果', text=ret[1])


if __name__ == '__main__':
    main()


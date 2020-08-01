# import libraries

from bs4 import BeautifulSoup as bs
import requests
import json
import pandas as pd
import urllib.parse
import re
import urllib
import os
# 初始化一个空的set集合用于存放产品的详细地址
urls = ([])
headers = {'Connection': 'keep-alive',
           'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'zh-CN,zh;q=0.8',
           'content-type': 'application/x-www-form-urlencoded',
           'Referer': 'https://home.mi.com/crowdfundinglist',
           'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36'}

def de_duplication(lst):   ##去重不改变原数据顺序
    de_du = list(set(lst))
    de_du.sort(key=lst.index)
    return de_du

def saveToLocal(url,i,count,gid):
    r = requests.get(url)
    with open(str(gid)+"_"+str(i)+".jpg", 'wb')as jpg:
        jpg.write(r.content)





def getDetails(gid,count):
    # 获取产品的详细信息
    detailparm = "{\"detail\":{\"model\":\"Shopv2\",\"action\":\"getDetail\",\"parameters\":{\"gid\":\"+%s+\"}},\"comment\":{\"model\":\"Comment\",\"action\":\"getList\",\"parameters\":{\"goods_id\":\"+%s+\",\"orderby\":\"1\",\"pageindex\":\"0\",\"pagesize\":\"2\"}},\"activity\":{\"model\":\"Activity\",\"action\":\"getAct\",\"parameters\":{\"gid\":\"+%s+\"}}}" % (gid,gid,gid)
    detailreq = urllib.parse.quote(detailparm)
    #print(detailreq)
    detailreq = "data=" + detailreq
    detailresponse = requests.post("https://home.mi.com/app/shop/pipe", headers=headers, data=detailreq)
    # 美化json格式
    detailResultJsondata = json.dumps(detailresponse.json(), sort_keys=True, indent=4,separators=(',', ': '))
    good = json.loads(detailResultJsondata)['result']['detail']['data']['good']
    detail_item = pd.DataFrame(columns=('SKU','商品简介', '商品介绍图片链接', '商品常见问题图片链接'))
    # detail_item.loc[0] = [good['gid'], good['summary'],good['intro_ext']['url']]
    #print(good)
    # 产品详情 常见问题
    #print(good['intro_ext'][0]['url'] + " ===== " + good['intro_ext'][1]['url'] + " ====== " + good['summary']+ " ====== " +good['album'][0])
    # i = 0
    # for item in good['album']:
    #     print(item)
    #     saveToLocal(item, i,count)
    #     i+=1
    url=good['intro_ext'][1]['url']
    response = requests.get(url, headers=headers)
    bs_info = bs(response.text,'html.parser')  # convert text to sth that bs can identified
    imgsArray = bs_info.find_all('img') # find specific position without using reg exp
    i = 0
    for image in imgsArray:
        try:
            print(image['src'])
            saveToLocal(image['src'], i, count,gid)
            i += 1
        except KeyError:
            print(f"{gid}'s age is unknown.")



def getPage():
    headers = {'Connection': 'keep-alive',
               'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'zh-CN,zh;q=0.8',
               'content-type': 'application/x-www-form-urlencoded',
               'Referer': 'https://home.mi.com/crowdfundinglist',
               'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36'}
    data = {'data':'{"result": {"model": "Homepage", "action": "GetGroup2ClassInfo", "parameters": {}}}'}
    r = requests.post("https://home.mi.com/app/shopv3/pipe",params=data,headers=headers).json()
    jsondata = json.dumps(r, sort_keys=True, indent=4, separators=(',', ': '))
    groups = r['result']['result']['data']['groups']
    df = pd.DataFrame(columns=('一级分类ID', '一级分类', '二级分类ID', '二级分类'))
    x = 0
    for i in groups:
        for j in i:
            class1_name=j['class']['name']      ##一级分类
            ucid1=j['class']['ucid']   ##一级分类ID
            for k in j['sub_class']:
                class2_name=k['name']   ##二级分类
                ucid2=k['ucid']   #二级分类ID
                df.loc[x] = [ucid1, class1_name, ucid2, class2_name]
                x=x+1
    df.to_csv('list.csv',index=False, encoding="GB18030")

    ##获取商品数据

    s = requests.session()
    cateList = df['一级分类ID'].values.tolist()
    catename = df['一级分类'].values.tolist()
    cateList=de_duplication(cateList)
    catename=de_duplication(catename)
    df_item = pd.DataFrame(columns=('一级分类ID','一级分类','二级分类','二级分类ID', '商品ID', '商品名称', '商品简介', '商品图片', '商品URL'))
    x = 0
    url = 'https://youpin.mi.com/app/shopv3/pipe'
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Content-Length': '145',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': 'youpindistinct_id=1677376dd950-07a9ccd760a322-514b2f1f; UM_distinctid=1677376de97317-013da9709fcd2b-514b2f1f-1fa400-1677376de98e12; Hm_lvt_f60d40663f1e63b337d026672aca065b=1543830429; mjclient=PC; youpin_sessionid=16777d642ba-0b57d1ad5863d-1ee2; CNZZDATA1267968936=1240670798-1543827326-%7C1543899301; Hm_lpvt_f60d40663f1e63b337d026672aca065b=1543903790',
        'Host': 'youpin.mi.com',
        'Origin': 'https://youpin.mi.com',
        'Referer': 'https://youpin.mi.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.15 Safari/537.36'
    }
    s.headers.update(headers)

    for i in range(len(cateList)):  ##一级分类目录商品
        data = {
            'data': '{"uClassList": {"model": "Homepage", "action": "BuildHome", "parameters": {"id": "' + str(
                cateList[i]) + '"}}}'
        }
        req = s.post(url=url, data=data).json()
        itemdata = req['result']['uClassList']['data']
        # print(itemdata)
        for j in itemdata:
            if 'content' in j:
                content_name = j['content']['name']  ##二级分类
                ucid = j['content']['ucid']  # 二级分类ID
                summary = k['summary']
                for k in j['data']:
                    try:
                        gid = k['gid']  ##商品ID
                        iid = k['iid'] #图片
                        pic2 = k['img_horizon'] # another pic
                        name = k['name']  ##商品名称
                        pic_url = k['pic_url']
                        itemurl = k['url']
                        df_item.loc[x] = [cateList[i], catename[i], ucid, content_name, gid, name, summary, pic_url, itemurl]
                        # 循环遍历将地址插入到地址集合:由于每个项目详细页面的地址都是http://home.mi.com/shop/detail?gid+上产品的编号，故这里只需要存入产品编号即可
                        # getDetails(gid)
                        x += 1
                    except:
                        print("ee")
    # df_item.to_csv('df_item.csv', index=False, encoding="GB18030")

IDlist = [104221,102521,106226,104868,107755,105273,107218,103314,104454,104404,108208,103802,103373,106781,101217,105295,104001,
          103505,104687,106774,105792,106266,107297,106770,106687,106021,102847,105522,631,749,102258,105984,104446,
          104558,108320,107732,106687,106778,102605,107314,106262,108100,106265,104946,106224,108104,105566,101123,104239,102848,
          105368,100945,103864,110077,109808,107450,110157,107614,107036,107638,103361,109303,107891,108215,103896,107425,109100,
          106279,104258,107596,104959,103261,112901,112415,110282,102891,104868,105118,106253,109536,110569,108617,107154,101975,
          107933,111763,113036,110289,108202,108584,107363,108240,109465,107692,109751,110565,111264,108748,107200,788,
          108883,105775,109422,109767,109299,102703,117200]
IDlist=[103802,103373,106781,101217,105295,104001,
          103505,104687,106774,105792,106266,107297,106770,106687,106021,102847,105522,631,749,102258,105984,104446,
          104558,108320,107732,106687,106778,102605,107314,106262,108100,106265,104946,106224,108104,105566,101123,104239,102848,
          105368,100945,103864,110077,109808,107450,110157,107614,107036,107638,103361,109303,107891,108215,103896,107425,109100,
          106279,104258,107596,104959,103261,112901,112415,110282,102891,104868,105118,106253,109536,110569,108617,107154,101975,
          107933,111763,113036,110289,108202,108584,107363,108240,109465,107692,109751,110565,111264,108748,107200,788,
          108883,105775,109422,109767,109299,102703,1172003]
#107314,108100,106265

#try:
#     print(f'{person} is {ages[person]} years old.')
# except KeyError:
#     print(f"{person}'s age is unknown.")

#102891 #107363(78) 108883(87)
count = 0
for i in IDlist:
    getDetails(i,count)
    count +=1






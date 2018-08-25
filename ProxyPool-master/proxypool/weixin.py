import requests
from pyquery import PyQuery as pq
from urllib.parse import urlencode
basic_url ='http://weixin.sogou.com/weixin?'
proxy_pool_url = 'http://127.0.0.1:5000/get'
import pymongo
proxy = None #全局代理
max_count = 5
headers = {
'Cookie':"ssuid=5064793980; SUV=006379BB6F2FB6F656869430F4630778; dt_ssuid=8874230314; pgv_pvi=3720247296; pex=C864C03270DED3DD8A06887A372DA219231FFAC25A9D64AE09E82AED12E416AC; CXID=C8E9F3A0A3EE3F375F07313ADD429944; teleplay_play_records=teleplay_587098:18; usid=OAcHFA0qrCyU08V_; weixinIndexVisited=1; SUID=F6B62F6F6573860A5667AA100005BA53; sct=79; GOTO=Af22417-3002; ad=86RvSkllll2bnjlglllllVHTcKklllllbhMLhlllll9lllll9Aoll5@@@@@@@@@@; IPLOC=CN4211; ABTEST=0|1535157599|v1; SNUID=CDA23B7B14116022AF7CA9AE151E0125; __guid=14337457.1862869906174477000.1535157603861.4497; renren_tag_0526=isTag; JSESSIONID=aaaECNhCcf8Ek9aWArBvw; ppinf=5|1535158452|1536368052|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZTozNjolRTUlOEQlOTclRTQlQjklOTQlRTUlOEMlOTclRTYlOUMlQTh8Y3J0OjEwOjE1MzUxNTg0NTJ8cmVmbmljazozNjolRTUlOEQlOTclRTQlQjklOTQlRTUlOEMlOTclRTYlOUMlQTh8dXNlcmlkOjQ0Om85dDJsdUVmNDJORUdIZGRybl9iQlMxanY3ZFlAd2VpeGluLnNvaHUuY29tfA; pprdig=NmoFjob5xX1c7yeaG-ZMvcjh6eZWli9LFpdEqcU3bhe7NnQxo7NxiXhevXZ36IaavEjaLFxV8YUC1QAkx80qzOYrn_uU91BQb7MzylkZvPIMmr9Jh0r8md-RMzEIrq38UsmFKCjbmTc24y75M6vS5zz-zDpGrTdY8SX3m6ItGwA; sgid=25-36773081-AVuAqLStmB7s6P72u6eqlHw; ppmdig=1535158453000000e799f69fb4f550342170e31dd8ee1033; monitor_count=7",
'Host':'weixin.sogou.com',
'Upgrade-Insecure-Requests':'1',
'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
}
#定义获取代理的ip地址
def get_proxy():
   try:
       res = requests.get(proxy_pool_url)
       if res.status_code == 200:
           print(res.text)
           return res.text
       return None
   except ConnectionError:
       return None

#定义获取页面是否存在封ip
def get_html(url,count = 1):
    global proxy
    #防止循环请求超过5次返回空
    if count>=max_count:
        print('请求失败')
        return None
    try:
        if proxy:
            proxies = {
                'http':'http://'+proxy
            }
            res = res = requests.get(url,allow_redirects = False,headers = headers,proxies = proxies)
        else:
             res = requests.get(url,allow_redirects = False,headers = headers)
        if res.status_code == 200:
            return res.text
        if res.status_code == 302:
            print('ip被封')
            proxy = get_proxy()
            if proxy:
               print('代理在使用',proxy)
               return get_html(url)
            else:
                print('获取代理失败')
                return None
    except ConnectionError:
        count+=1
        print('请求失败')
        proxy = get_proxy()
        return get_html(url,count)


#定义获取索引页的方法
def get_index(keyword,page):
    data = {
        'query':keyword,
        'type':2,
        'page':page
    }
    #组合url地址
    url = basic_url+urlencode(data)
    html = get_html(url)
    return html
#解析索引页
def parse_index(html):
    doc = pq(html)
    items = doc('.news-box .news-list li .txt-box h3 a').items()

    for item in items:
        yield item.attr('href')
#得到文章内容页
def get_article_detail(url):
    res = requests.get(url)
    if res.status_code == 200:
        return res.text
    return None

#解析文章内容
def parse_article(html):
     doc = pq(html)
     title = doc('.rich_media_title').text()
     content = doc('.rich_media_content ').text()
     date = doc('#publish_time').text()
     nickname = doc('#js_author_name').text()
     #返回字典
     return {
         'title':title,
         'content':content,
         'date':date,
         'nickname':nickname
     }

#保存到数据库
client = pymongo.MongoClient('127.0.0.1')
db = client['weixin']

def save_to_mongodb(result):
    global db
    db['weixin'].insert(result)
    print('存储成功')

def mao():
          html =  get_index('风景',1)
          if html:
              article_url = parse_index(html)
              for url in article_url:
                  articleurl = get_article_detail(url)
                  if articleurl:
                      article_data = parse_article(articleurl)
                      save_to_mongodb(article_data)


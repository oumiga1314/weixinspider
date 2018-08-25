import requests
import re

html = requests.get("http://www.89ip.cn/index_1.html")
ok=html.text
ok.replace(' ','')
ok.replace('\t','')
print(ok)
pattern2 = re.compile('(\d+\.\d+\.\d+\.\d+).*?(\d+)',re.S)
p1 = re.findall(pattern2,ok)
for i in p1:
    x = i[0]+':'+i[1]
    print(x)


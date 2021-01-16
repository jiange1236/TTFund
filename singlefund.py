import random
import time
import requests    # XPath解析
from lxml import etree
import re

tcode = '377240'
sdate = '2016-03-01'
edate = '2017-03-01'

rename = re.compile(r'(?<='+tcode+'",")\w*","([\u4e00-\u9fa5]{0,})')
respm = requests.get(url=f'http://fund.eastmoney.com/js/fundcode_search.js')
# print(respm.text)
name = rename.search(respm.text)[1]

respt = requests.get(
    url=f'http://fund.eastmoney.com/f10/F10DataApi.aspx?type=lsjz&code={tcode}&page=1&per=20&sdate={sdate}&edate={edate}')
htmlt = etree.HTML(respt.text)
spanst = htmlt.xpath('/html/body/text()')
pages = re.search(r'(?<=pages:)[1-9]+', spanst[0])[0]
for page in range(1, int(pages)):
    resp = requests.get(
        url=f'http://fund.eastmoney.com/f10/F10DataApi.aspx?type=lsjz&code={tcode}&page={page}&per=20&sdate={sdate}&edate={edate}')
    # 通过XPath语法从页面中提取需要的数据
    # 可通过Chrome浏览器中F12调试工具右键选择查看元素的XPath★★★
    html = etree.HTML(resp.text)
    spans = html.xpath(
        '/html/body/table/tbody/tr/td')
    spantext = []
    for span in spans:
        spantext.append(span.text)
    with open(f'{name}.txt', 'a', encoding="utf-8") as file:
        x = 0
        while x < len(spantext):
            for y in range(7):
                file.write(f'{spantext[x]} ')
                x += 1
            file.write(f'\n')
    time.sleep(random.randint(1, 2))
print('生成完毕')

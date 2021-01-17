import requests    # XPath解析
from lxml import etree
import re
import xlwt
import time

# 设置基金代码、时间
tcode = ['163402', '110011', '166002', '163406', '519736', '000619']
sdate = '2010-01-04'
edate = '2021-01-15'


class fund(object):
    def __init__(self, tc):
        self.tc = tc
        self.fdurl = 'http://fund.eastmoney.com/f10/F10DataApi.aspx?type=lsjz&code=' + \
            self.tc+'&page=1&per=20&sdate='+sdate+'&edate='+edate
        self.fddata = requests.get(url=self.fdurl)
        self.htmlt = etree.HTML(self.fddata.text)
        # 通过XPath语法从页面中提取需要的数据
        # 可通过Chrome浏览器中F12调试工具右键选择查看元素的XPath★★★

    def fdname(self):
        # 获取基金名称
        renaze = re.compile(r'(?<='+self.tc+'",")\w*","([\u4e00-\u9fa5]{0,})')
        rename = requests.get(
            url=f'http://fund.eastmoney.com/js/fundcode_search.js')
        name = renaze.search(rename.text)[1]
        return name

    def fdtitle(self):
        titles = self.htmlt.xpath('/html/body/table/thead/tr/th')
        return titles

    def fdpage(self):
        fdpages = self.htmlt.xpath('/html/body/text()')
        pages = re.search(r'(?<=pages:)[1-9]+', fdpages[0])[0]
        return pages

    def fdda(self):
        spantext = []
        page = self.fdpage()
        for page in range(1, int(page)):
            fdurls = 'http://fund.eastmoney.com/f10/F10DataApi.aspx?type=lsjz&code=' + \
                self.tc+'&page='+str(page)+'&per=20&sdate=' + \
                sdate+'&edate='+edate
            fddatas = requests.get(url=fdurls)
            htmlts = etree.HTML(fddatas.text)
            spans = htmlts.xpath('/html/body/table/tbody/tr/td')
            for span in spans:
                spantext.append(span.text)
        return spantext


print('----------START-----------')
print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
print('-')
# 获得基金数据
fdnum = len(tcode)
fd_name = [fund(tcode[i]).fdname() for i in range(fdnum)]
fd_title = [fund(tcode[i]).fdtitle() for i in range(fdnum)]
fd_data = [fund(tcode[i]).fdda() for i in range(fdnum)]


# 初始化excel函数
wb = xlwt.Workbook()
st = [wb.add_sheet(fd_name[i]) for i in range(fdnum)]

# 写入数据
for i in range(fdnum):
    tirow = 0
    sx = 0
    srow = 1
    for fdti in fd_title[i]:
        st[i].write(0, tirow, fdti.text)
        tirow += 1
    while sx < len(fd_data[i]):
        for scol in range(7):
            st[i].write(srow, scol, fd_data[i][sx])
            sx += 1
        srow += 1

wb.save('基金净值数据.xlsx')
print('-')
print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
print('-----------END------------')
print('生成完毕')

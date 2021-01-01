import requests
import csv,time
from lxml import etree

def GetCookie():
    url = 'https://www.lagou.com/jobs/list_%E8%BF%90%E8%90%A5/p-city_213?&cl=false&fromSearch=true&labelWords=&suginput='
    # 注意如果url中有中文，需要把中文字符编码后才可以正常运行
    headers = {
        'User-Agent': 'ozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3704.400 QQBrowser/10.4.3587.400'
    }
    response = requests.get(url=url, headers=headers, allow_redirects=False)
    # cookies = requests.utils.dict_from_cookiejar(response.cookies)
    return  response.cookies

# page 当前页数
# kd 岗位名称
# url 请求的url
def GetData(page, kd, url):
    headers = {
        'Host': 'www.lagou.com',
        'Origin': 'https://www.lagou.com',
        'Referer': 'https://www.lagou.com/jobs/list_%E8%BF%90%E8%90%A5?labelWords=&fromSearch=true&suginput=',
        'User-Agent': 'ozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3704.400 QQBrowser/10.4.3587.400'
    }
    data = {
        'first': 'true',
        'pn': str(page),
        'kd': str(kd),
    }
    s = requests.Session()
    response = s.post(url=url, data=data, headers=headers, cookies=GetCookie())
    response.encoding = response.apparent_encoding  # 根据网页内容分析出的编码方式
    html = response.json()['content']['positionResult']['result']
    showid = response.json()['content']['showId']
    saveData(html, kd, showid, s, page)

def saveData(html, kd, showid, s, page):
    f = open(kd + '.csv', mode="a+", newline='', encoding='utf-8-sig')
    csv_write = csv.writer(f)
    if page == 2:
        csv_write.writerow(['职位名称', '公司名称', '公司规模', '薪资待遇', '工作经验', '是否全职', '学历要求', '公司福利', '发布时间', '职位详情链接', '职位详情'])
    for i in range(len(html)):
        positionid = html[i]['positionId']  # 职位id，用于爬取下一页内容
        job_detail = detail_parse(positionid, showid, s)
        positionName = html[i]['positionName']  # 职位名称
        companyFullName = html[i]['companyFullName']  # 公司名称
        companySize = html[i]['companySize']  # 公司规模
        salary = html[i]['salary']  # 薪资待遇
        workYear = html[i]['workYear']  # 工作经验
        jobNature = html[i]['jobNature']  # 是否全职
        education = html[i]['education']  # 学历要求
        positionAdvantage = html[i]['positionAdvantage']  # 公司福利
        lastLogin = html[i]['lastLogin']  # 发布时间
        url = 'https://www.lagou.com/jobs/{}.html'.format(positionid)  # 职位详情链接
        csv_write.writerow([positionName, companyFullName, companySize, salary, workYear, jobNature, education, positionAdvantage, lastLogin, url, job_detail])
    f.close()

def detail_parse(positionid, showid, s):
    # 解析详情页数据
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36',
    }
    url = 'https://www.lagou.com/jobs/{}.html?show={}'.format(positionid, showid)
    response = s.get(url, headers=headers, cookies=GetCookie())
    print(response.text)
    tree = etree.HTML(response.content)
    job_detail = tree.xpath('//div[@class="job-detail"]/p/text()')
    job_detail = ''.join(job_detail)
    return job_detail

def main():
    print('【说明文档】')
    print('1.输入要查询的岗位和城市后，目前只能爬取30页数据')
    print('2.为了防止拉勾反爬虫机制，每页爬取时间间隔2秒，无需手动设置')
    print('3.爬取完毕后，会在原文件夹生成一个csv文件，跟excel一样打开即可查看数据')
    print('*' * 30)
    # 发送请求
    kd = input('请输入你要查询的岗位：')
    city = input('请输入你要查询的城市：')
    page = int(input('请输入你要爬取的页数：'))
    if page >= 30:
        page = 30
    url = 'https://www.lagou.com/jobs/positionAjax.json?city={}&needAddtionalResult=false'.format(city)
    for page in range(2, page + 2):
        print('第%i页正在爬取' % (page - 1))
        GetData(page, kd, url)
        time.sleep(2)

    print('*' * 30)
    print('所有数据爬取完毕，可以关闭当前界面，前往查看爬取下来的数据了~')

if __name__ == '__main__':
    main()
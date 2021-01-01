# 原理
#import requests
#proxy = {
#     'http': 'http://' + '222.90.42.232:36739',
#     'https': 'https://' + '222.90.42.232:36739',
# }
# print(proxy)
# headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'}
# p = requests.get('https://www.baidu.com/', headers=headers, proxies=headers,timeout = 3)
# print(p.text)
#

import requests
import pymysql
conn = pymysql.connect(host='数据库ip', user='用户名', passwd='密码', db='数据库名称', charset='utf8')
cursor = conn.cursor()

# 将爬取到的ip放到数据库内
def crawl_ips():
    r = requests.get('http://api.shenlongip.com/ip?key=xey54s36&pattern=json&count=100&need=1001&protocol=1')
    data = r.json()['data']
    for ip_info in data:
        cursor.execute(
            """insert ip(ip,port,prov,city) VALUES('{}','{}','{}','{}')""".format(
                ip_info['ip'], ip_info['port'], ip_info['prov'], ip_info['city']
            )
        )
        conn.commit()

# 从数据库中删除无用ip
def delete_ip(ip):
    delete_sql = """
        delete from ip where ip = {}
    """.format(ip)
    cursor.execute(delete_sql)
    conn.commit()
    return True

# 判断ip是否可用
def judge_ip(ip, port):
    http_url = 'https://www.baidu.com'
    proxy_url = 'https://{}:{}'.format(ip, port)
    print(proxy_url)
    try:
        proxy_dict = {
            'http': proxy_url
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
        }
        response = requests.get(http_url, headers=headers, proxies=proxy_dict, timeout=3)
        code = response.status_code
        if code>=200 and code<300:
            print('effective ip')
            return True
        else:
            print('invalid')
            delete_ip(ip)
            return False
        return True
    except Exception as e:
        print('ip出现异常')
        # 出现异常后就把这个ip给删除掉
        delete_ip(ip)
        return False

# 从数据库中随机获取到一个可用的ip
def get_random_ip():
    random_sql = """
                SELECT ip,port FROM ip
                ORDER BY RAND()
                LIMIT 1
            """
    result = cursor.execute(random_sql)
    for ip_info in cursor.fetchall():
        ip = ip_info[0]
        port = ip_info[1]
        judge_re = judge_ip(ip, port)
        print(judge_re)

# crawl_ips()
get_random_ip()
conn.close()
cursor.close()


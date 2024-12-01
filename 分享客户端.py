import json
import string
import zipfile

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

from selenium.webdriver.chrome.service import Service


def create_proxyauth_extension(proxy_host, proxy_port, proxy_username, proxy_password, scheme='http', plugin_path=None):
    """代理认证插件

    args:
        proxy_host (str): 你的代理地址或者域名（str类型）
        proxy_port (int): 代理端口号（int类型）
        # 用户名密码认证(私密代理/独享代理)
        proxy_username (str):用户名（字符串）
        proxy_password (str): 密码 （字符串）
    kwargs:
        scheme (str): 代理方式 默认http
        plugin_path (str): 扩展的绝对路径

    return str -> plugin_path
    """
    if plugin_path is None:
        plugin_path = 'vimm_chrome_proxyauth_plugin.zip'

    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """

    background_js = string.Template(
        """
        var config = {
                mode: "fixed_servers",
                rules: {
                singleProxy: {
                    scheme: "${scheme}",
                    host: "${host}",
                    port: parseInt(${port})
                },
                bypassList: ["foobar.com"]
                }
            };

        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "${username}",
                    password: "${password}"
                }
            };
        }

        chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {urls: ["<all_urls>"]},
                    ['blocking']
        );
        """
    ).substitute(
        host=proxy_host,
        port=proxy_port,
        username=proxy_username,
        password=proxy_password,
        scheme=scheme,
    )
    with zipfile.ZipFile(plugin_path, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)
    return plugin_path


def get_bvid3():
    ipjson = requests.post(url='http://124.221.28.167:8080/ip_json').json()
    print(ipjson)
    ip = ipjson['ip']
    port = ipjson['port']
    username = ipjson['username']
    password = ipjson['password']
    proxyauth_plugin_path = create_proxyauth_extension(
        proxy_host=ip,  # 代理IP
        proxy_port=port,  # 端口号
        # 用户名密码(私密代理/独享代理)
        proxy_username=username,
        proxy_password=password
    )
    chrome_options = Options()
    chrome_options.add_argument('--log-level=3')
    service = Service(log_path='NUL')
    chrome_options.add_extension(proxyauth_plugin_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get("https://www.bilibili.com/")
    # 等待10秒，确保页面加载和cookie设置完成
    time.sleep(3)

    # 获取所有cookies
    cookies = driver.get_cookies()

    # 查找.bilibili域下的buvid3的值
    buvid3_value = None
    for cookie in cookies:
        if cookie['name'] == 'buvid3' and '.bilibili' in cookie['domain']:
            buvid3_value = cookie['value']
            break
    driver.quit()
    print("buvid3的值是:", buvid3_value)
    return buvid3_value

def fetch_buvid3():
    # API URL
    header={
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    }
    url = "https://api.bilibili.com/x/frontend/finger/spi"

    # 发送请求
    response_buvid3 = requests.get(headers=header, url=url).json()
    buvid3 = response_buvid3['data']['b_3']
    return buvid3

def bili_share():
    new_bvid = requests.get(url='http://124.221.28.167:8080/Get_new_json/new_BVID.json').json()
    for i in new_bvid['BVID']:
        buvid3_value = fetch_buvid3()
        BVID=i['BVID']
        params={
            'bvid': BVID,
            'eab_x': '2',
            'ramval': '9',
            'source': 'android',
            'ga': '1',
            'csrf': '',
            'appkey':'123',
            'action':'like',
        }
        header={
            'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'referer':'https://www.bilibili.com/',
        }
        cookie={
            'buvid3':buvid3_value
        }
        try:
            sproxies = requests.get('http://124.221.28.167:8080/GET_IP').json()
            shar = requests.post(url='https://api.bilibili.com/x/web-interface/share/add', headers=header, params=params, cookies=cookie, proxies=sproxies).json()
            print(shar)
            if shar['code'] == 0:
                share = shar['data']
                print('分享成功', BVID,'视频分享次数：',share)
            elif shar['code'] == -403:
                print('账号&IP风控了：',shar['message'],BVID)
            elif shar['code'] == -404:
                print('视频没有了：',shar['message'],BVID)
                params={
                    'bvid':BVID
                }
                dell_bvido = requests.get(url='http://124.221.28.167:8080/delete_bvid',params=params).json()
                print(dell_bvido)
        except Exception as e:
            print(e)
    return {'success': '0','msg':'所有BVID已完成一次分享'}
success = 0
while True:
    sdasd = bili_share()
    print(sdasd)
    success += 1
    print('已完成分享次数：',success)
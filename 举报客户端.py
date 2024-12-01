import base64
import json
import string
import zipfile

import requests
from lxml.html.diff import token
from selenium import webdriver
from selenium.common import ElementNotInteractableException, NoSuchElementException, NoSuchFrameException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
import time

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from sqlalchemy.sql.functions import random
import random



def get_jubao_list(parmas):

    get_list = requests.get(url='http://124.221.28.167:8080/find_video', params=parmas).json()
    return get_list


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
def Get_Token(SESSDATA,bili_jct):
    img = 'a.png'
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
    driver.get("https://www.bilibili.com/video/BV1qb411U7Aa/")
    cookie = [
        {'name': 'SESSDATA', 'value': SESSDATA, 'domain': '.bilibili.com'},
        {'name': 'bili_jct', 'value': bili_jct, 'domain': '.bilibili.com'},
        {'name': 'x-bili-gaia-vtoken', 'value': '', 'domain': '.bilibili.com'}
    ]
    for cookie in cookie:
        driver.add_cookie(cookie)
    driver.refresh()
    time.sleep(60)
    try:
        actions = ActionChains(driver)
        driver.find_element(By.CSS_SELECTOR, '.video-tool-more-reference').click()
        time.sleep(2)
        driver.find_element(By.CSS_SELECTOR, '.video-complaint').click()
        time.sleep(2)
        driver.switch_to.frame('appeal')
        time.sleep(2)
        driver.find_elements(By.CSS_SELECTOR, '.item-check-btn')[0].click()
        time.sleep(2)
        driver.find_element(By.CSS_SELECTOR, 'textarea.cnt').send_keys('稿件存在传播盗版资源等问题。在平台大量发布视频，宣传，售卖（包括或不限于）简介，主页，头像，评论区，视频内二维码，QQ群号，引流到外链下载盗版地下城与勇士版本')
        time.sleep(2)
        driver.find_element(By.CSS_SELECTOR, '.btn-confirm').click()
        time.sleep(2)
        YZM = driver.find_element(By.CSS_SELECTOR, '.geetest_panel_next')
        time.sleep(2)
        YZM.screenshot('a.png')
        b = open(img, 'rb')
        base64_data = base64.b64encode(b.read())
        b64 = base64_data.decode()
        data = {"username": 'LaoGouih1', "password": 'Asd123', "typeid": '27', "image": b64}
        result = json.loads(requests.post("http://api.ttshitu.com/predict", json=data).text)
        if result['success']:
            X_Y_result = result["data"]["result"]
            X_Y_list = X_Y_result.split('|')
            for X_Y_lists in X_Y_list:
                x, y = map(int, X_Y_lists.split(','))
                actions.move_to_element_with_offset(YZM, x - 159, y - 204).click().perform()
            driver.find_element(By.CSS_SELECTOR, '.geetest_commit_tip').click()
            time.sleep(2)
            driver.refresh()
            all_cookies = driver.get_cookies()
            token = next((cookie['value'] for cookie in all_cookies if cookie['name'] == 'x-bili-gaia-vtoken'), None)
            return token
        else:
            return None
    except NoSuchFrameException:
        return None
    except ElementNotInteractableException:
        driver.quit()
        print('ElementNotInteractableException')
        return None
    except NoSuchElementException:
        print('NoSuchElementException')
        driver.quit()
        return None

def token_San_lian(SESSDATA,bili_jct,BVID,token):
    buvid3 = fetch_buvid3()
    params={
        "SESSDATA": SESSDATA,
        "bili_jct": bili_jct,
        'buvid3':buvid3,
        "BVID": BVID,
        "token": token,
        }
    token_sanl = requests.get(url='http://124.221.28.167:8080/Bili_Token_San_Lian',params=params).json()
    print(token_sanl)
    return token_sanl


def pt_jb(aid,cookie):
    csrf = cookie['bili_jct']
    harad ={
       'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
    }
    params={
        'aid': aid,
        'attach':'',
        'block_author': False,
        'csrf': csrf,
        'desc': '1',
        'tid': '10022',
    }
    pt_jb_rq = requests.post('https://api.bilibili.com/x/web-interface/appeal/v2/submit', params=params,headers=harad,cookies=cookie).json()
    return pt_jb_rq

def token_jb(aid,cookie,token):
    csrf = cookie['bili_jct']
    SESSDATA =cookie['SESSDATA']
    bili_jct = cookie['bili_jct']
    harad ={
       'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
    }
    params={
        'aid': aid,
        'attach':'',
        'block_author': False,
        'csrf': csrf,
        'desc': '1',
        'tid': '10022',
        'tk': token,
    }
    cookie={
        'SESSDATA': SESSDATA,
        'bili_jct': bili_jct,
        'x-bili-gaia-vtoken': token,
    }
    tk_jb_rq = requests.post('https://api.bilibili.com/x/web-interface/appeal/v2/submit', params=params,headers=harad,cookies=cookie).json()
    return tk_jb_rq


def main ():
    cookie_id = 0
    while True:
        key_world = ['DNF70','DNF86','DNF60','DNF90','act4','dnf新开','dnf复古','dnf公益',]
        get_cooke = requests.get('http://124.221.28.167:8080/Get_new_json/Cookies.json').json()
        get_wrid = requests.get(url='http://124.221.28.167:8080/generate_w_rid').json()
        get_new_bvid = requests.get(url='http://124.221.28.167:8080/Get_new_json/new_BVID.json').json()
        random_keyword = random.choice(key_world)
        w_rid = get_wrid['w_rid']
        wts = get_wrid['wts']
        San_lian_bvid = get_new_bvid['BVID'][0]['BVID']
        SESSDATA = get_cooke[cookie_id]['SESSDATA']
        bili_jct = get_cooke[cookie_id]['bili_jct']
        parmas={
            "SESSDATA": SESSDATA,
            "bili_jct": bili_jct,
            "BVID":random_keyword,
            "w_rid": w_rid,
            "wts":wts,
        }
        cookie = {
            'SESSDATA': SESSDATA,
            'bili_jct': bili_jct
        }
        token = Get_Token(SESSDATA, bili_jct)
        if token == None:
            print('获取token失败')
            cookie_id += 1
        else:
            San_lian_RQ = token_San_lian(SESSDATA=SESSDATA,bili_jct=bili_jct,token=token,BVID=San_lian_bvid)
            if San_lian_RQ['msg'] == 'Token三连成功':
                print('三连成功',San_lian_bvid)
            jubao_list = get_jubao_list(parmas=parmas)
            for tileitem in jubao_list['data']['result']:
                BVID = tileitem['bvid']
                title = tileitem['title']
                aid = tileitem['aid']
                tokenjb = token_jb(aid=aid,cookie=cookie,token=token)
                print(tokenjb)
                if tokenjb['code'] == 0:
                    print('Token举报成功','BVID:',BVID,title)
                else:
                    print('Token举报失败')
                    cookie_id += 1
                    break

aa = main()
print(aa)
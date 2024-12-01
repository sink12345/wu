import base64
import json
import string
import time
import zipfile

from selenium.common import ElementNotInteractableException, NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import requests
from selenium import webdriver

from Bili_API import dell_bvid_route


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
    time.sleep(15)
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
    except ElementNotInteractableException:
        driver.quit()
        print('ElementNotInteractableException')
        return None
    except NoSuchElementException:
        print('NoSuchElementException')
        driver.quit()
        return None

def San_lian_all_BVID(user_ID = 0 ,bid = 0):
    Get_new_Cookie_rq = requests.post(url='http://124.221.28.167:8080/Get_new_json/Cookies.json').json()
    print(Get_new_Cookie_rq)
    Get_new_BVID_rq = requests.post(url='http://124.221.28.167:8080/Get_new_json/new_BVID.json').json()
    print(Get_new_BVID_rq)
    while True:
        try:
            SESSDATA = Get_new_Cookie_rq[user_ID]['SESSDATA']
            bili_jct = Get_new_Cookie_rq[user_ID]['bili_jct']
            BVID = Get_new_BVID_rq['BVID'][bid]['BVID']
            data={
                'SESSDATA': SESSDATA,
                'bili_jct': bili_jct,
                'BVID': BVID
            }
            Bili_San_Lian_rq = requests.get(url=f'http://124.221.28.167:8080/Bili_San_Lian',params=data).json()
            if Bili_San_Lian_rq['msg'] == '三连异常':
                print(Bili_San_Lian_rq)
                user_ID += 1
            elif Bili_San_Lian_rq['response']['message']=='账号未登录':
                user_ID += 1
            elif Bili_San_Lian_rq['response']['code'] == -401 or Bili_San_Lian_rq['response']['code'] == -403:
                token = Get_Token(SESSDATA=SESSDATA, bili_jct=bili_jct)
                for b in Get_new_BVID_rq['BVID']:
                    BVID = b['BVID']
                    data={
                        'SESSDATA': SESSDATA,
                        'bili_jct': bili_jct,
                        'BVID': BVID,
                        'token': token
                    }
                    Bili_Token_San_Lian_rq = requests.post(url='http://124.221.28.167:8080/Bili_Token_San_Lian',data=data).json()
                    print(Bili_Token_San_Lian_rq)
                    if Bili_Token_San_Lian_rq['msg'] == 'Token三连失败':
                        print(Bili_Token_San_Lian_rq)
                        break
                    else:
                        print(Bili_Token_San_Lian_rq)
                print('当前账号三连完成', user_ID)
                user_ID += 1
            else:
                print(Bili_San_Lian_rq)
                bid += 1
        except IndexError:
            return {'success':'0','msg':'所有账号已完成三连','user_ID':user_ID}


token1 = San_lian_all_BVID()
print(token1)
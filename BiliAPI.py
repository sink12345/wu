import datetime
import hashlib
import json
import os
import random
import re
import time
import urllib

import openpyxl
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from flask import render_template_string
import pandas as pd
from flask import Flask, request, jsonify
from requests.exceptions import JSONDecodeError, ProxyError, RequestException

app = Flask(__name__)
# 用于存储代理信息的变量
proxies_info = None




# HTML模板，用于显示数据表
TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Bilibili Video Data</title>
</head>
<body>
    <h1>Bilibili Video Data</h1>
    <table border="1">
        {% for row in data %}
            <tr>
                {% for cell in row %}
                    <td>{{ cell }}</td>
                {% endfor %}
            </tr>
        {% endfor %}
    </table>
</body>
</html>
'''




@app.route('/fetch_buvid3',methods=['GET', 'POST'])
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




@app.route('/bilibili-video-data')
def bilibili_video_data():
    # 读取Excel文件
    df = pd.read_excel('哔哩哔哩视频数据.xlsx')

    # 将DataFrame转换为HTML表格可以接受的格式
    data = df.values.tolist()

    # 使用render_template_string渲染HTML模板
    return render_template_string(TEMPLATE, data=data)
def decode_key(input_str):
    return "".join(chr(ord(c) - 1) for c in input_str)
# 定义获取代理的函数
def fetch_proxies():
    # API接口地址
    api_url = "https://dps.kdlapi.com/api/getdps/?secret_id=odb8cskdnp4w6j1nzfcc&signature=t2h6uykokdzsu0pntiqf22dhkkfi202k&num=1&pt=1&format=json&sep=1"
    # 发送请求获取代理信息
    response = requests.get(api_url)
    # 提取代理IP列表
    proxy_ip = response.json()['data']['proxy_list']
    # 用户名和密码
    username = "d2299983745"
    password = "e8g8y8o2"
    # 随机选择一个代理
    proxy = random.choice(proxy_ip)
    # 构造代理字典
    proxies = {
        "http": f"http://{username}:{password}@{proxy}/",
        "https": f"http://{username}:{password}@{proxy}/"
    }
    return proxies

@app.route('/delete_bvid', methods=['GET', 'POST'])
def delete_bvid():
    bvid = None
    if request.method == 'GET':
        bvid = request.args.get('bvid')
    elif request.method == 'POST':
        # 假设客户端发送的是JSON数据
        if request.is_json:
            bvid = request.json.get('bvid')
        else:
            # 如果不是JSON，可能需要其他处理方式，例如表单数据
            return jsonify({'code': 1, 'message': '请求内容类型不是JSON'}), 400

    if not bvid:
        return jsonify({'code': 1, 'message': 'BVID参数未提供'}), 400

    JSON_FILE_PATH = 'new_BVID.json'
    try:
        # 读取JSON文件内容
        with open(JSON_FILE_PATH, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # 确保BVID键存在且是列表
        if 'BVID' in data and isinstance(data['BVID'], list):
            # 删除指定BVID的条目
            data['BVID'] = [entry for entry in data['BVID'] if entry.get('BVID') != bvid]

            # 写入JSON文件内容
            with open(JSON_FILE_PATH, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)

            return jsonify({'code': 0, 'message': 'BVID已删除'})
        else:
            return jsonify({'code': 1, 'message': 'BVID列表不存在或格式不正确'}), 400
    except Exception as e:
        return jsonify({'code': 1, 'message': str(e)}), 500











# 定义Flask路由，用于获取代理信息
@app.route('/GET_IP', methods=['GET', 'POST'])
def GET_IP():
    global proxies_info
    # 如果proxies_info为None，则调用fetch_proxies获取新的代理信息
    if proxies_info is None:
        proxies_info = fetch_proxies()
    # 返回存储的代理信息
    return proxies_info

# 定义Flask路由，用于停止获取代理信息的定时任务
@app.route('/stop_fetch_proxies', methods=['GET', 'POST'])
def stop_fetch_proxies():
    global proxies_info
    # 如果proxies_info存在，则移除任务并重置proxies_info
    if proxies_info:
        proxies_info = None
        return '获取代理的定时任务已停止。', 200
    else:
        return '没有正在运行的获取代理的定时任务。', 404

















# 定义Flask路由，用于启动获取代理信息的定时任务
@app.route('/start_fetch_proxies', methods=['GET', 'POST'])
def start_fetch_proxies():
    global proxies_info
    # 如果proxies_info为None，则添加任务并返回状态信息
    if proxies_info is None:
        proxies_info = fetch_proxies()
        return '获取代理的定时任务已启动。', 200
    else:
        return '获取代理的定时任务已经在运行。', 200









@app.route('/Get_Bili_name', methods=['POST', 'GET'])
def Get_Bili_name():
    """
    获取用户名，验证是否掉线的方法。
    """
    # 初始化参数
    bili_jct = None
    SESSDATA = None

    # 对于GET请求，从查询字符串中获取参数
    if request.method == 'GET':
        bili_jct = request.args.get('bili_jct')
        SESSDATA = request.args.get('SESSDATA')

    # 对于POST请求，从表单或JSON数据中获取参数
    elif request.method == 'POST':
        bili_jct = request.form.get('bili_jct') or request.json.get('bili_jct')
        SESSDATA = request.form.get('SESSDATA') or request.json.get('SESSDATA')

    # 检查是否提供了必要的参数
    if not bili_jct or not SESSDATA:
        return jsonify({'success': '0', 'msg': '缺少必要的参数'}), 400

    url = 'https://api.bilibili.com/x/web-interface/nav'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'referer': 'https://www.bilibili.com/?',
    }
    cookies = {
        'bili_jct': bili_jct,
        'SESSDATA': SESSDATA,
    }

    try:
        response = requests.get(url=url, headers=headers, cookies=cookies)
        response.raise_for_status()  # 如果HTTP请求返回了不成功的状态码，则抛出HTTPError异常
        data = response.json()

        if data['code'] == -101:
            return jsonify({'success': '0', 'msg': 'Cookie失效'}), 401
        elif data['code'] == 0:
            return jsonify({'success': '1', 'name': data['data']['uname'], 'msg': 'Cookie有效'}), 200
        else:
            return jsonify({'success': '0', 'msg': 'Cookie异常'}), 400

    except requests.exceptions.RequestException as e:
        return jsonify({'success': '-1', 'msg': '请求异常'}), 500













@app.route('/Bili_San_Lian', methods=['POST','GET'])
def Bili_San_Lian():
    """
    发送普通三连的方法。
    :param bili_jct: bili_jct
    :param SESSDATA: SESSDATA
    :param BVID: BVID
    """
    bili_jct = None
    SESSDATA = None
    BVID = None
    buvid3 = None
    # 对于 GET 请求，从查询字符串中获取参数
    if request.method == 'GET':
        bili_jct = request.args.get('bili_jct')
        SESSDATA = request.args.get('SESSDATA')
        BVID = request.args.get('BVID')
        buvid3 = request.args.get('buvid3')
    # 对于 POST 请求，从表单或 JSON 数据中获取参数
    elif request.method == 'POST':
        bili_jct = request.form.get('bili_jct') or request.json.get('bili_jct')
        SESSDATA = request.form.get('SESSDATA') or request.json.get('SESSDATA')
        BVID = request.form.get('BVID') or request.json.get('BVID')
        buvid3 = request.form.get('buvid3') or request.json.get('buvid3')

    url = 'https://api.bilibili.com/x/web-interface/archive/like/triple'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'referer': 'https://www.bilibili.com/',
    }
    parmas= {
        'bvid': BVID,
        'eab_x': '2',
        'ramval': '4',
        'source': 'web_normal',
        'ga': '1',
        'csrf': bili_jct,
    }
    cookie = {
        'bili_jct':bili_jct,
        'SESSDATA':SESSDATA,
        'buvid3': buvid3,
    }
    try:
        sproxies = GET_IP()
        response = requests.post(url=url, headers=headers, params=parmas, cookies=cookie, proxies=sproxies).json()
        if response['code'] == 0:
            return {'success': '0', 'BVID': f'{BVID}', 'msg': '无Token三连成功', 'response': response,
                    'proxies': sproxies}
        else:
            return {'success': '0', 'BVID': f'{BVID}', 'msg': '无Token三连失败', 'response': response,
                    'proxies': sproxies}
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        return {'success': '-1', 'BVID': f'{BVID}', 'msg': '三连异常'}














@app.route('/Bili_Token_San_Lian', methods=['POST', 'GET'])
def Bili_Token_San_Lian():
    # 从请求中获取参数
    buvid3 = request.args.get('buvid3') if request.method == 'GET' else request.form.get('buvid3') or request.json.get('buvid3')
    bili_jct = request.args.get('bili_jct') if request.method == 'GET' else request.form.get('bili_jct') or request.json.get('bili_jct')
    SESSDATA = request.args.get('SESSDATA') if request.method == 'GET' else request.form.get('SESSDATA') or request.json.get('SESSDATA')
    BVID = request.args.get('BVID') if request.method == 'GET' else request.form.get('BVID') or request.json.get('BVID')
    token = request.args.get('token') if request.method == 'GET' else request.form.get('token') or request.json.get('token')
    url = 'https://api.bilibili.com/x/web-interface/archive/like/triple'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'referer': 'https://www.bilibili.com/',
    }
    data = {
        'bvid': BVID,
        'eab_x': '2',
        'ramval': '4',
        'source': 'web_normal',
        'ga': '1',
        'csrf': bili_jct,
        'tk': token,
    }
    cookies = {
        'bili_jct': bili_jct,
        'SESSDATA': SESSDATA,
        'x-bili-gaia-vtoken': token,
    }
    try:
        sproxies = GET_IP()
        response = requests.post(url=url, headers=headers, data=data, cookies=cookies,proxies=sproxies).json()
        if response['code'] == 0:
            return {'success':'0','BVID':f'{BVID}','msg':'Token三连成功','response':response,'proxies':sproxies}
        else:
            return {'success':'0','BVID':f'{BVID}','msg':'Token三连失败','response':response,'proxies':sproxies}
    except requests.exceptions.RequestException as e:
        return {'success':'-1','BVID':f'{BVID}','msg':'Token三连异常'}










@app.route('/Get_new_json/<flienm>', methods=['POST', 'GET'])
def Get_new_json(flienm):
    """
    获取BVID列表配合Get_token使用
    :param flienm: 可传入参数获取的json文件名称
    """
    try:
        with open(flienm, 'r', encoding='utf-8') as f:
            data = json.load(f)  # 解析 JSON 文件内容
        # 使用 with 语句创建应用程序上下文
        with app.app_context():
            return jsonify(data)  # jsonify 可以直接处理字典或列表
    except FileNotFoundError:
        with app.app_context():
            return jsonify({'error': '文件未找到'}), 404
    except json.JSONDecodeError:
        with app.app_context():
            return jsonify({'error': '无效的 JSON 文件'}), 500
    except Exception as e:
        with app.app_context():
            return jsonify({'error': str(e)}), 500

















@app.route('/generate_w_rid', methods=['POST','GET'])
def generate_w_rid():
    """
    获取w_rid的方法。
    """
    M = "d569546b86c252:db:9bc7e99c5d71e5"
    N = "557251g796:g54:f:ee94g8fg969e2de"
    params = {"mid": 1, "web_location": 1430654}
    mixin_key = decode_key(M) + decode_key(N)
    timestamp = int(time.time())
    timestamp_str = str(timestamp)
    sorted_params = json.dumps(params, sort_keys=True)
    encoded_params = urllib.parse.quote(sorted_params)
    hash_input = encoded_params + mixin_key + timestamp_str
    w_rid = hashlib.md5(hash_input.encode("utf-8")).hexdigest()
    return {"w_rid": w_rid, "wts": str(timestamp)}










@app.route('/find_video', methods=['POST', 'GET'])
def find_video():
    # 初始化参数
    bili_jct = None
    SESSDATA = None
    BVID = None
    w_rid = None
    wts = None

    # 对于 GET 请求，从查询字符串中获取参数
    if request.method == 'GET':
        bili_jct = request.args.get('bili_jct')
        SESSDATA = request.args.get('SESSDATA')
        BVID = request.args.get('BVID')
        w_rid = request.args.get('w_rid')
        wts = request.args.get('wts')
    # 对于 POST 请求，从表单或 JSON 数据中获取参数
    elif request.method == 'POST':
        BVID = request.form.get('BVID') or request.json.get('BVID')
        w_rid = request.form.get('w_rid') or request.json.get('w_rid')
        wts = request.form.get('wts') or request.json.get('wts')
        SESSDATA = request.form.get('SESSDATA') or request.json.get('SESSDATA')
        bili_jct = request.form.get('bili_jct') or request.json.get('bili_jct')
    url='https://api.bilibili.com/x/web-interface/wbi/search/type'
    parmas={
        'category_id':'',
        'search_type': 'video',
        'ad_resource': '5654',
        '__refresh__': True,
        '_extra':'',
        'context':'',
        'page': '1',
        'page_size': '42',
        'pubtime_begin_s': '0',
        'pubtime_end_s': '0',
        'from_source':'',
        'from_spmid': '333.337',
        'platform': 'pc',
        'highlight': '1',
        'single_column': '0',
        'keyword': BVID,
        'qv_id': '64lLB8WIf07ncYmUs3EQLIc6uUgbRdFt',
        'source_tag': '3',
        'gaia_vtoken':'',
        'dynamic_offset': '0',
        'web_location': '1430654',
        'w_rid': w_rid,
        'wts': wts,
    }
    cookie={
        'SESSDATA': SESSDATA,
        'bili_jct': bili_jct,
    }
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'referer': 'https://www.bilibili.com/',
    }
    sproxies = GET_IP()
    try:
        response = requests.get(url=url, params=parmas, cookies=cookie, headers=headers, proxies=sproxies)
        response.raise_for_status()  # 检查HTTP请求的状态
        if response.content:  # 确保响应内容不为空
            grequest = response.json()
            print(grequest)
            return grequest
        else:
            return {'code': '-1', 'message': 'Empty response'}, 204
    except ProxyError as e:
        # 处理代理错误
        print('Proxy error:', str(e))
        return {'code': '-1', 'message': 'Proxy error'}, 503
    except JSONDecodeError:
        # 记录实际的响应内容，以便调试
        print('Invalid JSON response:', response.text)
        return {'code': '-1', 'message': 'Invalid JSON response'}, 400
    except RequestException as e:
        # 处理其他可能的请求异常
        print('Request failed:', str(e))
        return {'code': '-1', 'message': 'Request failed'}, 500














@app.route('/update_cookies', methods=['POST','GET'])
def update_cookies(cookies_folder='Cookies', cookies_json='Cookies.json'):
    """
    更新Cookies信息到指定JSON文件的方法。
    :param cookies_folder: 存储cookie文件的文件夹路径
    :param cookies_json: 输出JSON文件的名称
    """
    # 初始化一个列表来存储所有cookie信息
    cookies_list = []
    # 遍历Cookies文件夹
    for filename in os.listdir(cookies_folder):
        # 移除文件名后缀
        file_id = os.path.splitext(filename)[0]
        file_path = os.path.join(cookies_folder, filename)
        if os.path.isfile(file_path):
            with open(file_path, 'r') as file:
                try:
                    cookies = json.load(file)
                    bili_jct = None
                    SESSDATA = None
                    for cookie in cookies:
                        if cookie['name'] == 'bili_jct':
                            bili_jct = cookie['value']
                        elif cookie['name'] == 'SESSDATA':
                            SESSDATA = cookie['value']
                    # 确保两个值都已找到
                    if bili_jct and SESSDATA:
                        cookie_info = {
                            "id": file_id,
                            "BT": "0",
                            "bili_jct": bili_jct,
                            "SESSDATA": SESSDATA,
                            "token": "0"
                        }
                        cookies_list.append(cookie_info)
                except json.JSONDecodeError:
                    return {'success': '0', 'msg': f"文件：{filename} 不是有效的JSON格式"}
    # 将列表写入到Cookies.json文件中
    with open(cookies_json, 'w') as outfile:
        json.dump(cookies_list, outfile, indent=4)
        return {'success': '0', 'msg': 'cookies_json已更新'}















@app.route('/Get_video_shuju', methods=['POST','GET'])
def Get_video_shuju():
    Cookie_ID = 0
    no_favorites = {"BVID": []}
    wb = openpyxl.Workbook()
    ws = wb.active
    Text_headers = ['视频标题', '视频作者', '视频标签', '视频链接', '视频BVID', '收到的赞', '视频播放量', '上传时间']
    ws.append(Text_headers)
    DL_video = 0
    error_videos = []
    with open('new_BVID.json', 'r', encoding='utf-8') as file:
        BVID_json = json.load(file)
    with open('Cookies.json', 'r', encoding='utf-8') as file:
        cookie_json = json.load(file)
    # 在列表里面循环获取BVID和cookie
    for teime in BVID_json['BVID']:
        cookie = cookie_json[Cookie_ID]
        bili_jct = cookie['bili_jct']
        SESSDATA = cookie['SESSDATA']
        Cookie_ID += 1
        BVID = teime['BVID']
        js_w_rid = generate_w_rid()
        w_rid = js_w_rid['w_rid']
        wts = js_w_rid['wts']
        parmas = {
            'wrid': w_rid,
            'bili_jct': bili_jct,
            'SESSDATA': SESSDATA,
            'wts': wts,
            'BVID': BVID,
        }
        try:
            requests1 = requests.get(url='http://124.221.28.167:8080/find_video', params=parmas).json()
            if requests1['code'] == 0:
                Video_list = requests1['data']['result']
                favorites = Video_list[0]['favorites']
                pubdate = Video_list[0]['pubdate']
                tag = Video_list[0]['tag']
                title = Video_list[0]['title']
                arcurl = Video_list[0]['arcurl']
                author = Video_list[0]['author']
                play = Video_list[0]['play']
                print('视屏标题：', title)
                print('视屏作者：', author)
                print('视屏标签：', tag)
                print('视屏链接：', arcurl)
                print('视屏BVID：', BVID)
                print('收到的赞:', favorites)
                print('视屏播放量：', play)
                converted_time = datetime.datetime.fromtimestamp(pubdate)
                video_time = converted_time.strftime('%Y-%m-%d %H:%M:%S')
                print('上传时间:', video_time)
                ws.append([
                    title,
                    author,
                    tag,
                    arcurl,
                    BVID,
                    favorites,
                    play,
                    video_time
                ])
                Cookie_ID += 1
                if favorites < 100:
                    bvid_dict = {"BVID": BVID}
                    no_favorites["BVID"].append(bvid_dict)
            else:
                print('请求错误')
        except KeyError or JSONDecodeError:
            print('视频失效',BVID)
            DL_video += 1
    file_path = './哔哩哔哩视频数据.xlsx'
    wb.save(file_path)
    wb.close()  # 关闭工作簿以防止文件损坏

    # 构建返回信息
    response = {
        'success': '0',
        'msg': file_path,
        'error_videos': error_videos ,
        'DL_video':DL_video,# 返回处理失败的BVID列表
    }
    return jsonify(response)
@app.route('/write_bvid', methods=['POST','GET'])
def write_bvid (BVID,file_path='new_BVID.json'):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)  # 读取 JSON 文件内容
        # 将新的 BVID 添加到 'BVID' 列表中
        data['BVID'].append({"BVID": BVID})  # 添加新的 BVID
        # 将更新的 JSON 数据保存回文件
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)  # 保存为 JSON 格式，并设置缩进为 2 个空格
            return {'success': '0', 'msg': f"{BVID}写入{file_path}成功",'data': data}

















@app.route('/ip_json', methods=['POST', 'GET'])
def ip_json():
    GET_IP_rq = GET_IP()
    print(GET_IP_rq)
    http = GET_IP_rq['http']
    print(http)
    pattern = r'http://(\w+):(\w+)@([\w.-]+):(\d+)/'
    match = re.search(pattern, http)
    if match:
        username = match.group(1)
        password = match.group(2)
        ip = match.group(3)
        port = match.group(4)
        list_name = {
            'username': username,
            'password': password,
            'ip': ip,
            'port': port
        }
        return list_name
    else:
        return None


@app.route('/')
def show_readme():
    with open('README.md', 'r', encoding='utf-8') as file:
        readme_content = file.read()
        from markdown import markdown
        readme_html = markdown(readme_content)
    return readme_html  # 或者返回 readme_html 如果您进行了转换


# 启动调度器
scheduler = BackgroundScheduler()
scheduler.add_job(func=stop_fetch_proxies, trigger='interval', seconds=60)
scheduler.start()
if __name__ == '__main__':
    # 运行Flask应用
    app.run(host='0.0.0.0', port=8080, debug=True)
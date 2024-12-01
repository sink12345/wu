# Bili_API
- @LaoGouih
- By 2017982754@qq.com
- 
## 【小白快速入门】

### 三连:
- 运行<获取token客户端.py>就会进行三连
- 大量账号掉线的话需要更新Cooke文件夹里的Cookie文件
- http://124.221.28.167:8080/update_cookies
- 进入这个网址就会更新Cookies.json
### 查询视频数据:
- http://124.221.28.167:8080/Get_video_shuju
- 进入这个网址网页加载完成就获取完毕了(需要等待很长时间)
- 不需要一直刷新点进去一次就行了
- http://124.221.28.167:8080/bilibili-video-data
- 然后进入这个网址查看视频数据
### 分享:
- 运行<分享客户端.py>就会进行分享
-


## 【开发者文档】
#### 【获取用户名，验证是否掉线的方法】
- http://124.221.28.167:8080
**请求路径**:
`GET /Get_Bili_name`

**请求参数**:
```json
{
  "SESSDATA": "SESSDATA",
  "bili_jct": "bili_jct"
}
```
### 成功响应示例

**Cookie失效**:
```json
{"success":"0","msg":"Cookie失效","response":"response"}
```

**Cookie未失效**:
```json
{"success":"0","name":"账号用户名","msg":"Cookie有效","response":"response"}
```

**请求异常**:
```json
{"success":"-1","msg":"请求异常"}
```


### 【无Token三连】
- http://124.221.28.167:8080
**请求路径**:
`GET /Bili_San_Lian`

**请求参数**:
```json
{
  "SESSDATA": "SESSDATA",
  "bili_jct": "bili_jct",
  "BVID": "BVID"
}
```

## 成功响应示列
**三连成功**:
```json
{"success":"0","BVID":"视频BV号","msg":"无Token三连成功","response":"responsett","proxies":"sproxies"}
```
**三连失败**:
```json
{"success":"0","BVID":"视频BV号","msg":"无Token三连失败","response":"responsett","proxies":"sproxies"}
```

**请求异常**:
```json
{"success":"-1","BVID":"视频BV号","msg":"三连异常"}
```


### 【Token三连】
- http://124.221.28.167:8080
**请求路径**:
`GET /Bili_Token_San_Lian`

**请求参数**:
```json
{
  "SESSDATA": "SESSDATA",
  "bili_jct": "bili_jct",
  "BVID": "BVID",
  "token": "token"
}
```
## 成功响应示列
**三连成功**:
```json
{"success":"0","BVID":"视频BV号","msg":"Token三连成功","response":"response","proxies":"sproxies"}
```
**三连失败**:
```json
{"success":"0","BVID":"视频BV号","msg":"Token三连失败","response":"response","proxies":"sproxies"}
```

**请求异常**:
```json
{"success":"-1","BVID":"视频BV号","msg":"Token三连异常"}
```


### 【获取服务器JSON文件内容】
- http://124.221.28.167:8080
**请求路径**:
`GET /Get_new_json/<flienm>`

**请求参数**:
```json
{
  "flienm": "flienm"
}
```


### 【获取w_rid】
- http://124.221.28.167:8080
**请求路径**:
`GET /generate_w_rid`


### 成功响应示列
**获取成功**:
```json
{"w_rid": "w_rid", "wts": "当前时间戳"}
```


### 【视频详细信息-配合获取w_rid使用】
- http://124.221.28.167:8080
**请求路径**:
`GET /find_video`

**请求参数**:
```json
{
  "SESSDATA": "SESSDATA",
  "bili_jct": "bili_jct",
  "BVID": "BVID",
  "w_rid": "w_rid",
  "wts":"wts"  
}
``` 

### 【更新Cookies。json文件】
- http://124.221.28.167:8080
**请求路径**:
`GET /update_cookies`


### 【生成new_BVID.json内视频的数据在当前目录下的‘哔哩哔哩视频数据.xlsx’文件】
- http://124.221.28.167:8080
**请求路径**:
`GET /Get_video_shuju`


### 【添加新的BVID到new_BVID.json文件内】
- http://124.221.28.167:8080
**请求路径**:
`GET /write_bvid`

**请求参数**:
```json
{
  "BVID": "BVID",
  "file_path":"file_path"
}
``` 
### 【获取代理IP接口】
- http://124.221.28.167:8080
**请求路径**:
`GET /GET_IP`


### 【关闭&关闭 服务器每30s自动获取代理IP】
- http://124.221.28.167:8080
**请求路径**:
`GET /stop_fetch_proxies` 
`GET /start_fetch_proxies`

### 【自动处理验证码并获取Cookie内的token】
- http://124.221.28.167:8080
**请求路径**:
`GET /Get_token` 

**请求参数**:
```json
{
  "SESSDATA": "SESSDATA",
  "bili_jct": "bili_jct"
}
``` 


### 【获取代理服务器的json格式】
- http://124.221.28.167:8080
**请求路径**:
`GET /ip_json`

**返回参数**:
```json
{
  "username": "username",
  "password": "password",
  "ip": "ip",
  "port": "port"
}
```

### 【将new_BVID.json内的BVID全部进行三连】
- http://124.221.28.167:8080
**请求路径**:
`GET /San_lian_all_BVID`
**判断逻辑**:
```text
user_ID = 0
bid = 0
进行获取Cookeis和BVID
首先进行普通三连
如果点赞成功则BVID+1
如果不成功则进行执行Get_token获取token进行token三连
```

- 
## 安装

安装说明。

```bash
# 需要依赖
pip install openpyxl -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install requests -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install apscheduler -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install Flask -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install pandas -i https://pypi.tuna.tsinghua.edu.cn/simple

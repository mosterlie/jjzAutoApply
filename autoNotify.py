import sys
import requests
from datetime import datetime,timedelta
from notifypy import Notify
import json

import lark_oapi as lark
from lark_oapi.api.im.v1 import *
import uuid


# 配置信息（需自行填写）
URL = "jjz.jtgl.beijing.gov.cn" # 初始地址，防止恶意访问，请求地址不提供，需要的自行抓包
AUTH = "81d0456d4b19404fa166f8c62f46c9c8" # 访问凭证，通过抓包在请求头信息 Authorization 字段
SEND_KEY = "SCT294395TySxJHOUfi140ooyyj1iV4SCs" # server酱微信推送密钥(可选)


#https://sctapi.ftqq.com/{SEND_KEY}.send?title={title}&desp={msg}")
#gx:e0deca171a794cb5843d2db1bd5eb7d7
#ccy:81d0456d4b19404fa166f8c62f46c9c8
### 地理信息（按需改动，不懂可以不改。如需改动建议通过http://jingweidu.757dy.com/自行查询自己的经纬度）
SQDZGDJD = "116.269423" # 社区地址高德经度
SQDZGDWD = "40.211128" # 社区地址高德纬度
SQDZBDJD = "116.275203" # 社区地址百度经度
SQDZBDWD = "40.216228" # 社区地址百度纬度
XXDZ = "白浮泉公园" # 进京地址

# 接口地址（无需改动）
STATE_LIST_URL = f"https://{URL}/pro/applyRecordController/stateList" # 查询状态接口
INSERT_APPLY_RECORD_URL = f"https://{URL}/pro/applyRecordController/insertApplyRecord" # 办理续签接口


def robotNotic(messageStr,uid,appId,appSecret,receiveId):
    # 创建client
    client = lark.Client.builder() \
        .app_id(appId) \
        .app_secret(appSecret) \
        .log_level(lark.LogLevel.DEBUG) \
        .build()

    # 构造请求对象
    request: CreateMessageRequest = CreateMessageRequest.builder() \
        .receive_id_type("open_id") \
        .request_body(CreateMessageRequestBody.builder()
            .receive_id(receiveId)
            .msg_type("text")
            .content(messageStr)
            #.content( "{\"text\":\"今日到期，但存在待生效记录，无需申请当前状态: 审核通过(生效中)\"}")
            .uuid(uid)
            .build()) \
        .build()

    # 发起请求
    response: CreateMessageResponse = client.im.v1.message.create(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.im.v1.message.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \\n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
        return

    # 处理业务结果
    lark.logger.info(lark.JSON.marshal(response.data, indent=4))


def request(url, payload={}) -> dict:
    headers = {"Authorization": AUTH, "Content-Type": "application/json"}
    res = requests.post(url, headers=headers, json=payload)
    data = res.json()
    # if data["code"] != 200:
        #print(f"请求失败，状态码: {data['code']}，错误信息: {data['msg']}")
    return data
    

def exec_renew(data, date, jjzzl="六环外") -> dict:
    # payload = {
    #     "sqdzgdjd": SQDZGDJD,
    #     "sqdzgdwd": SQDZGDWD,
    #     "sqdzbdjd": SQDZBDJD,
    #     "sqdzbdwd": SQDZBDWD,
    #     "xxdz" : XXDZ,
    #     "hpzl" : data["hpzl"], # 车牌类型
    #     "applyIdOld" : data["applyId"], # 续办申请id
    #     "vId" : data["vId"], # 车辆识别代号
    #     "jsrxm" : data["jsrxm"], # 车主姓名
    #     "jszh" : data["jszh"], # 车主身份证号
    #     "hphm" : data["hphm"], # 车牌号
    #     "taxrxx" : [],
    #     "jjdq" : "010", # 进京目的地地区
    #     "jjmd" : "06", # 进京目的地
    #     "jjzzl" : "01" if jjzzl == "六环内" else "02", # 进京证类型
    #     "jjlk" : "00606", # 进京路况
    #     "jjmdmc" : "其它", # 进京目的地名称
    #     "jjlkmc" : "其他道路", # 进京路况名称
    #     "jjrq" : date, # 进京日期(申请生效日期)
    # }
    payload = {
            "sqdzgdjd" : "116.4",
            "jjdzgdwd" : "40.170103",
            "jjlkgdjd" : "",
            "ylzmc" : "进京证(六环内)",
            "xxdz" : "白马路辅路与坤安路交叉口东100米中信银行数据中心",
            "jsrxm" : data["jsrxm"],
            "jjzzl" : "02",
            "ylzqyms" : "市界到二环 (不含二环路)+客车全年可办理12次，每次限通行7天",
            "elzmc" : "进京证(六环外)",
            "sfzj" : "1",
            "jjrq" : date,
            "ylzsfkb" : true,
            "hpzl" : data["hpzl"],
            "jszh" : data["jszh"],
            "area" : "顺义区",
            "jingState" : "",
            "jjmdmc" : "其它",
            "sqdzgdwd" : "39.9",
            "jjlkgdwd" : "",
            "jjdzgdjd" : "116.668192",
            "jjmd" : "06",
            "elzqyms" : "市界到六环 (含六环路、不含通州全域)+客车全年不限办理次数，每次限通行7天",
            "dabh" : "",
            "jszOcrPath" : "",
            "zjxxdzgdwd" : "40.170103",       
            "jjlk" : "",
            "cllx" : "01",
            "zjxxdz" : "中信银行数据中心",
            "elzsfkb" : true,
            "jjdq" : "010",
            "jjlkmc" : "",
            "zjxxdzgdjd" : "116.668192",
            "txrxx" : [],
            "vId" : data["vId"],
            "hphm" : data["hphm"]
    }
    return request(INSERT_APPLY_RECORD_URL, payload)

def days_between_dates(date1: str, date2: str) -> int:
    d1 = datetime.strptime(date1, '%Y-%m-%d')
    d2 = datetime.strptime(date2, '%Y-%m-%d')
    return (d2 - d1).days + 1

def dateCompare(date1: str, date2: str) -> int:
    d1 = datetime.strptime(date1, '%Y-%m-%d')
    d2 = datetime.strptime(date2, '%Y-%m-%d')
    return (d1 - d2).days

def get_future_date(date_str, days) -> str:
    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    future_date = date_obj + timedelta(days=days)
    return future_date.strftime("%Y-%m-%d")

def send_wechat(title, msg) -> None:
    if not SEND_KEY:
        print("未配置server酱推送密钥，不发送微信推送")
        return
    requests.post(f"https://sctapi.ftqq.com/{SEND_KEY}.send?title={title}&desp={msg}")



def handle_response(state_data):
    # print(state_data)
    waite_valid_data = state_data["data"]["bzclxx"][0]["ecbzxx"][0] if state_data["data"]["bzclxx"][0]["ecbzxx"] else None
    # print(waite_valid_data)
    valid_data = state_data["data"]["bzclxx"][0]["bzxx"][0] if state_data["data"]["bzclxx"][0]["bzxx"] else None
    # print(valid_data)

    valid_jinjing_state = valid_data["blztmc"] if valid_data is not None else None
    valid_jinjing_type = valid_data["jjzzlmc"] if valid_data is not None else None
    valid_jinjing_sqsj = valid_data["sqsj"] if valid_data is not None else None
    valid_jinjing_hphm = valid_data["hphm"] if valid_data is not None else None

    waite_valid_jinjing_state = waite_valid_data["blztmc"] if waite_valid_data is not None else None
    waite_valid_jinjing_type = waite_valid_data["jjzzlmc"] if waite_valid_data is not None else None
    waite_valid_jinjing_sqsj = waite_valid_data["sqsj"] if waite_valid_data is not None else None
    waite_valid_jinjing_hphm = waite_valid_data["hphm"] if waite_valid_data is not None else None
    formatted_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    today = datetime.now().strftime("%Y-%m-%d")
    
    msg = ""
    if valid_data is None:
        # 不存在生效的，需要申请
        renw_data = exec_renew(valid_data, apply_date, jjzzl="六环外")
        titile = "续签申请成功" if renw_data["code"] == 200 else f"续签申请失败:状态码: {renw_data['code']}，错误信息: {renw_data['msg']}"
        msg = f"当前无生效中进京证"
        flag = 1
        return titile,msg,flag
    # 判断状态
    if valid_jinjing_state not in ["审核通过(生效中)"]:
        # 不存在生效的，需要申请
        renw_data = exec_renew(valid_data, today, jjzzl="六环外")
        titile = "续签申请成功" if renw_data["code"] == 200 else f"续签申请失败:状态码: {renw_data['code']}，错误信息: {renw_data['msg']}"
        msg = f"当前无生效中进京证"
        flag = 1
        return titile,msg,flag

    # 判断有效时间

    valid_start_date, valid_end_date = valid_data["yxqs"], valid_data["yxqz"]
    if dateCompare(today, valid_end_date) >= 0:
        # 今日到期或已经到期，进一步判断是否已存在待生效记录
        if waite_valid_data is None:
            # 不存在待生效记录 ，需要申请
            apply_date=get_future_date(valid_end_date,1)
            renw_data = exec_renew(valid_data, apply_date, jjzzl="六环外")
            titile = "续签申请成功" if renw_data["code"] == 200 else f"续签申请失败:状态码: {renw_data['code']}，错误信息: {renw_data['msg']}"
            msg = f"当前状态: {valid_jinjing_state}\\n有效期: {valid_start_date}至{valid_end_date}\\n类型: {valid_jinjing_type}\\n申请时间: {valid_jinjing_sqsj}\\n执行时间: {formatted_time}\\n车牌号码: {valid_jinjing_hphm}"
            flag = 1
            return titile,msg,flag
        #print(waite_valid_data)
        waite_start_date, waite_end_date = waite_valid_data["yxqs"], waite_valid_data["yxqz"]
       # print(waite_end_date)
       # if dateCompare(today, waite_end_date) > 0:
        #    # 待生效记录，今日到期或已经到期，需要申请
        #    apply_date=get_future_date(waite_end_date,1)
        #    renw_data = exec_renew(valid_data, apply_date, jjzzl="六环外")
       #     titile = "续签申请成功" if renw_data["code"] == 200 else f"续签申请失败:状态码: {renw_data['code']}，错误信息: {renw_data['msg']}"
        #    msg = f"当前状态: {valid_jinjing_state}\\n有效期: {valid_start_date}至{valid_end_date}\\n类型: {valid_jinjing_type}\\n申请时间: {valid_jinjing_sqsj}\\n执行时间: {formatted_time}\\n车牌号码: {valid_jinjing_hphm}"
        #    return titile,msg

        # 存在待生效记录，并且未到期，无需操作
        if waite_valid_jinjing_state not in ["审核中", "审核通过(待生效)"]:
            # 待生效记录，今日到期或已经到期，需要申请
            apply_date=get_future_date(waite_end_date,1)
            renw_data = exec_renew(data, apply_date, jjzzl="六环外")
            titile = "续签申请成功" if renw_data["code"] == 200 else f"续签申请失败:状态码: {renw_data['code']}，错误信息: {renw_data['msg']}"
            msg = f"当前状态: {valid_jinjing_state}\\n有效期: {valid_start_date}至{valid_end_date}\\n类型: {valid_jinjing_type}\\n申请时间: {valid_jinjing_sqsj}\\n执行时间: {formatted_time}\\n车牌号码: {valid_jinjing_hphm}"
            flag = 1
            return titile,msg,flag

        
        titile = f"今日到期，已存在待生效记录，无需申请"
        flag = 0
        msg = f"当前状态: {valid_jinjing_state}\\n有效期: {valid_start_date}至{valid_end_date}\\n类型: {valid_jinjing_type}\\n申请时间: {valid_jinjing_sqsj}\\n执行时间: {formatted_time}\\n车牌号码: {valid_jinjing_hphm}"
        return titile, msg ,flag
    titile = "状态正常"
    flag = 0
    msg = f"当前状态: {valid_jinjing_state}\\n有效期: {valid_start_date}至{valid_end_date}\\n类型: {valid_jinjing_type}\\n申请时间: {valid_jinjing_sqsj}\\n执行时间: {formatted_time}\\n车牌号码: {valid_jinjing_hphm}"
    return titile,msg,flag

def main():


    gxAppId = "cli_a86520efaaf9500c"
    gxAppSecret = "9opaktlYsAP4wNrP9ylcxgGDUaT2z1EJ"
    gxReceiveId = "ou_675a2888e4154c365224b79a68984898"
    ccyAppId = "cli_a87b0edbd0b1501c"
    ccyAppSecret = "zP56TgJnDQm0WftUb7bjMdhbO2SLcYpP"
    gccyReceiveId = "ou_9d0a91ad4ebbbbe59fd274bff5b45c17"
    state_data = request(STATE_LIST_URL)
    title,msg,flag = handle_response(state_data)
    messageStr = title+"\\n"+msg
    message="{\"text\":"+"\""+messageStr+"\"}"
    uid_str = str(uuid.uuid4()) 
    

    #if flag == 1:
    robotNotic(message,uid_str,ccyAppId,ccyAppSecret,gccyReceiveId)
    
    robotNotic(message,uid_str,gxAppId,gxAppSecret,gxReceiveId)

    #print(state_data)
   # title,msg = handle_response(state_data)
   # print(title,"\\n",msg)
    #send_wechat(title,msg)
   # Notify.feishu_bot(title,msg)

if __name__ == "__main__":
    main()
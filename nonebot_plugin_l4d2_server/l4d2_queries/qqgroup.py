from ..l4d2_data.serverip import L4D2Server
from ..l4d2_image import server_ip_pic
from . import queries,player_queries,queries_dict,player_queries_anne_dict,msg_ip_to_list
from nonebot.log import logger
import random
import asyncio
import re
from ..message import PRISON,QUEREN,KAILAO
from .ohter import ALL_HOST
from typing import List,Dict
try:
    import ujson as json
except:
    import json
si = L4D2Server()
errors = (ConnectionRefusedError,ConnectionResetError,asyncio.exceptions.TimeoutError,OSError)
# errors = (TypeError,KeyError,ValueError,ConnectionResetError,TimeoutError)

async def get_qqgroup_ip_msg(qqgroup):
    """首先，获取qq群订阅数据，再依次queries返回ip原标"""
    ip_list = await si.query_server_ip(qqgroup)
    return ip_list
    
async def bind_group_ip(group:int,host:str,port:int):
    ip_list = await si.query_server_ip(group)
    if (host,port) in ip_list:
        return "本群已添加过该ip辣"
    await si.bind_server_ip(group,host,port)
    return "绑定成功喵，新增ip" + host

async def del_group_ip(group:int,number:int):
    number = int(number)
    logger.info(number)
    try:
        groups,host,port = await si.query_number(number)
    except TypeError:
        return '没有这个序号哦'
    if groups != group:
        return "本群可没有订阅过这个ip"
    await si.del_server_ip(number)
    return "取消成功喵，已删除序号" + str(number)
        
async def qq_ip_queries(msg:List[tuple]):
    """输入一个ip的二元元组组成的列表，返回一个输出消息的列表
    未来作图这里重置"""
    messsage = ""
    for i in msg:
        number,qqgroup,host,port = i
        msg2 = await player_queries(host,port)
        msg1 = await queries(host,port)
        messsage += '序号、'+ str(number) + '\n' + msg1 + msg2 + '--------------------\n'
    return messsage
            
async def qq_ip_queries_pic(msg:list):
    """输入一个ip的三元元组组成的列表，返回一个输出消息的图片"""
    msg_list = []
    if msg != []:
        for i in msg:
            number,host,port = i
            try:
                msg2 = await player_queries_anne_dict(host,port)
                msg1 = await queries_dict(host,port)
                msg1.update({'Players':msg2})
                msg1.update({'number':number})
                # msg1是一行数据完整的字典
                msg_list.append(msg1)
            except errors:
                pass
        pic = await server_ip_pic(msg_list)
    return pic
    
async def get_tan_jian(msg:List[tuple],mode:int):
    """获取anne列表抽一个"""
    msg_list = []
    rank = 0
    for i in msg:
        number,host,port = i 
        try:
            if mode == 1:
                # 探监
                msg2 = await player_queries_anne_dict(host,port)
                point = 0
                for i in msg2:
                    point += int(i['Score'])
                logger.info(point)
                msg1 = await queries_dict(host,port)
                sp:str = msg1['name']
                if '特' not in sp:
                    continue
                sp = int(sp.split('特')[0].split('[')[-1])
                points = point/4
                if points/sp <10:
                    continue
                if 'HT' in msg1['name']:
                    continue
                msg1.update({'Players':msg2})
                msg1.update({'ranks':point})
                ips = f'{host}:{str(port)}'
                msg1.update({'ips':ips})
                # msg1是一行数据完整的字典
                msg_list.append(msg1)
            if mode == 2:
                # 坐牢
                # try:
                msg1 = await queries_dict(host,port)
                if '普通药役' in msg1['name']:
                    if '缺人' in msg1['name']:
                        msg2 = await player_queries_anne_dict(host,port)
                        msg1.update({'Players':msg2})
                        ips = f'{host}:{str(port)}'
                        msg1.update({'ips':ips})
                        # msg1是一行数据完整的字典
                    else:
                        continue
                else:
                    continue
                msg_list.append(msg1)
            if mode == 3:
                # 开牢
                msg1 = await queries_dict(host,port)
                if '[' not in msg1['name']:
                    msg2 = await player_queries_anne_dict(host,port)
                    msg1.update({'Players':msg2})
                    ips = f'{host}:{str(port)}'
                    msg1.update({'ips':ips})
                    # msg1是一行数据完整的字典
                    msg_list.append(msg1)
        except errors:
            continue
    # 随机选一个牢房
    if len(msg_list) == 0:
        return '暂时没有这种牢房捏'
    logger.info(len(msg_list))
    mse = random.choice(msg_list)
    message:str = ''
    if mode == 1:
        ranks = mse['ranks']
        if ranks <= 300 :
            message = random.choice(PRISON[1])
        if 300 < ranks <= 450 :
            message = random.choice(PRISON[2])
        if ranks > 450 :
            message = random.choice(PRISON[3]) 
    if mode == 2:
        player_point = mse['players']
        if player_point == '1':
            message = random.choice(QUEREN[1])
        elif player_point == '2':
            message = random.choice(QUEREN[2])
        elif player_point == '3':
            message = random.choice(QUEREN[3])
        else:
            message = random.choice(QUEREN[4])
    if mode == 3:
        message = random.choice(KAILAO)
    message += '\n' + '名称：' + mse['name'] + '\n'
    message += '地图：' + mse['map_'] + '\n'
    message += f"玩家：{mse['players']} / {mse['max_players']}\n"
    print(mse['Players'])
    try:
        message += await msg_ip_to_list(mse['Players'])
    except (KeyError):
        message += '服务器里，是空空的呢\n'
    message += 'connect ' + mse['ip']
    return message

async def get_server_ip(number):
    group,host,port = await si.query_number(number)
    try:
        return str(host) + ':' + str(port)
    except TypeError:
        return None

def split_maohao(msg:str) -> list:
    """分割大小写冒号"""
    msg:list = re.split(":|：",msg.strip())
    mse = [msg[0],msg[-1]] if msg[0] != msg[-1] else [msg[0],20715]
    return mse

async def write_json(data_str:str):
    """添加数据或者删除数据
     - 【求生更新 添加 腐竹 ip 模式 序号】
     - 【求生更新 添加 腐竹 ip 模式】
     - 【求生更新 删除 腐竹 序号】
    """
    data_list = data_str.split(' ')
    logger.info(data_list)
    if data_list[0]=="添加":
        add_server = {}
        server_dict = ALL_HOST.get(data_list[1], {})
        if not server_dict:
            logger.info('新建分支')
            ALL_HOST[data_list[1]] = []
        for key,value in ALL_HOST.items():
            if data_list[1] == key:
                ids = []
                # 序号
                if len(data_list) == 4:
                    data_num:int = 1
                    for server in value:
                        ids.append(str(server['id']))
                    while data_num in ids:
                        data_num += 1
                    data_id = str(data_num)
                    add_server.update({'id':data_num})
                if len(data_list) == 5:
                    for server in value:
                        ids.append(str(server['id']))
                    if data_list[4].isdigit():
                        if data_list[4] not in ids:
                            data_id = data_list[4]
                            add_server.update({'id':int(data_id)})
                        else:
                            return '该序号已存在，请尝试删除原序号【求生更新 删除 腐竹 序号】'
                    else:
                        return '序号应该为大于0的正整数，请输入【求生更新 添加 腐竹 ip 模式 序号】'
                # 模式，ip
                add_server.update({'version':data_list[3]})
                try:
                    host,port = split_maohao(data_list[2])
                    add_server.update({'host':host,'port':port})
                except KeyError:
                    return 'ip格式不正确【114.11.4.514:9191】'
                value.append(add_server)
                ALL_HOST.update({key:value})
                with open('data/L4D2/l4d2.json', "r", encoding="utf8") as f_new:
                    json.dump(ALL_HOST, f_new, ensure_ascii=False, indent=4)
                return f'添加成功，指令为{key}{data_id}'
            
    elif data_list[0]=="删除":
        for key,value in ALL_HOST.items():
            value:List[dict]
            if data_list[1] == key:
                for server in value:
                    if int(data_list[2]) == server['id']:
                        value.remove(server)
                        if not value:
                            ALL_HOST.pop(key)
                        else:
                            ALL_HOST[key] = value
                        with open('data/L4D2/l4d2.json', "r", encoding="utf8") as f_new:
                            json.dump(ALL_HOST, f_new, ensure_ascii=False, indent=4)
                        return '删除成功喵'
                return '序号不正确，请输入【求生更新 删除 腐竹 序号】'
        return '腐竹名不存在，请输入【求生更新 删除 腐竹 序号】'    
    

ips = ALL_HOST['云']
ip_list = []
for one_ip in ips:
    host,port = split_maohao(one_ip['ip'])
    ip_list.append((one_ip['id'],host,port))
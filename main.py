import os
import sys
import time
import tkinter
from tkinter import filedialog
from urllib.parse import unquote

import requests
import win32api
import win32con
from win32clipboard import  OpenClipboard, SetClipboardData, CloseClipboard, EmptyClipboard


class Tool():  # 工具类函数

    @staticmethod
    # 写入剪贴板数据
    def set_clipboard(astr):
        OpenClipboard()
        EmptyClipboard()
        time.sleep(1)
        SetClipboardData(win32con.CF_UNICODETEXT, astr)
        CloseClipboard()
    @staticmethod
    def get( src_url, src_data, PROXY=None):  # get数据
        src_data['timestamp'] = int(time.time())  # 使用实时时间
        if PROXY:
            response = requests.get(src_url, src_data, proxies=PROXY, timeout=10)  # 超时10s，使用代理
        else:
            response = requests.get(src_url, src_data)
        if response.json()['message'] == 'OK' and response.json()['retcode'] == 0:
            return eval(response.text)['data']['list']
        elif 'visit too frequently' in response.text:
            time.sleep(0.5)  # 防止请求频繁
            raise ConnectionError( 'visit too frequently')
        else:
            raise ValueError("URL ERROR")

class _URL():
    HOST_CN = r'https://hk4e-api.mihoyo.com/event/gacha_info/api/getGachaLog'
    HOST_OS = r'https://hk4e-api-os.hoyoverse.com/event/gacha_info/api/getGachaLog'

    def __init__(self):
        if not os.path.exists('./cfg.ini'):
            open('./cfg.ini','w+').close()

        self.game_path=open('./cfg.ini','r',encoding='UTF-8').readline()

    def scanURL(self, game_path: str):
        if not os.path.exists(os.path.join(game_path, r'YuanShen_Data\webCaches\Cache\Cache_Data')):
            raise ValueError('游戏目录错误')
        else:
            open('./cfg.ini','w+',encoding='UTF-8').write(game_path)
        _P = os.path.join(game_path, r'YuanShen_Data\webCaches\Cache\Cache_Data')

        _f= os.path.join(_P,'data_2')
        _fdata = []
        _url = None
        _buf=[]
        try:
            _fdata = open( _f, 'rb').readlines()
        except PermissionError:
            win32api.CopyFile( _f,'cache')
            _fdata=open('cache','rb').readlines()
            os.remove('cache')

        for _l in _fdata:
            if self.HOST_CN.encode(encoding='UTF-8') in _l:
                _start = _l.rfind(self.HOST_CN.encode(encoding='UTF-8'))
                _end = _l.rfind('&game_biz=hk4e_cn'.encode(encoding='UTF-8')) + len('&game_biz=hk4e_cn')
                _url = _l[_start:_end].decode(encoding='UTF-8')
                if self.checkURL(_url):
                    _buf.append(_url)
                else:pass
        if _buf !=[]:
            _l=_buf[len(_buf)-1]
            user_id=open(os.path.join(os.getenv("APPDATA"),'../LocalLow/miHoYo/原神/UidInfo.txt'),'r',encoding='UTF-8').readlines()[0]

            return user_id,_url
                # break
        # win32api.DeleteFile( os.path.join(_P,'data_0'))
        # win32api.DeleteFile( os.path.join(_P,'data_1'))
        # win32api.DeleteFile( os.path.join(_P,'data_2'))
        # win32api.DeleteFile( os.path.join(_P,'data_3'))
        else:
            raise SystemError('没有可用的链接\n请登录 原神->祈愿->历史记录 刷新链接后重试')

    def transURL(self, url_forfirst, gacha_type, page, end_id):
        authkey_ver = int(url_forfirst[url_forfirst.rfind('authkey_ver=') + 12])
        sign_type = int(url_forfirst[url_forfirst.rfind('sign_type=') + 10])
        auth_appid = url_forfirst[url_forfirst.rfind('auth_appid=') + 11:url_forfirst.rfind('&init_type')]
        init_type = int(url_forfirst[url_forfirst.rfind('init_type=') + 10:url_forfirst.rfind('&gacha_id')])
        gacha_id = url_forfirst[url_forfirst.rfind('gacha_id=') + 9:url_forfirst.rfind('&timestamp')]
        timestamp = int(url_forfirst[url_forfirst.rfind('timestamp=') + 10:url_forfirst.rfind('&lang')])
        device_type = url_forfirst[url_forfirst.rfind('device_type=') + 12:url_forfirst.rfind('&game_version=')]
        game_version = url_forfirst[url_forfirst.rfind('game_version=') + 13:url_forfirst.rfind('&plat_type')]
        plat_type = url_forfirst[url_forfirst.rfind('plat_type=') + 10:url_forfirst.rfind('&region')]
        region = url_forfirst[url_forfirst.rfind('region=') + 7:url_forfirst.rfind('&authkey')]
        authkey = url_forfirst[url_forfirst.rfind('authkey=') + 8:url_forfirst.rfind('&game_biz')]
        game_biz = url_forfirst[url_forfirst.rfind('game_biz=') + 9:]
        data = {
            'authkey_ver': authkey_ver,
            'sign_type': sign_type,
            'auth_appid': auth_appid,
            'init_type': init_type,
            'gacha_id': gacha_id,
            'timestamp': timestamp,
            'lang': 'zh-cn',
            'device_type': device_type,
            'game_version': game_version,
            'plat_type': plat_type,
            'region': region,
            'authkey': unquote(authkey),  #
            'game_biz': game_biz,
            'gacha_type': gacha_type,
            'page': page,
            'size': 20,
            'end_id': end_id
        }
        if 'cn' not in region:
            return self.HOST_OS, data
        else:
            return self.HOST_CN, data

    def checkURL(self, url):
        try:
            _url, _data = self.transURL(url, 301, 1, 0)
            Tool.get(_url, _data)  # 获取一次以校验链接
            return 1
        except Exception as e:
            #raise e
            # print(e)
            return 0

def resource_path(relative_path):
    if getattr(sys, 'frozen', False):  # 是否Bundle Resource
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

if __name__ == '__main__':
    os.environ['REQUESTS_CA_BUNDLE'] = resource_path( "cacert.pem")  # 配置证书

    try:
        uid,url=_URL().scanURL(_URL().game_path)
    except SystemError as e:
        print(str(e))
        time.sleep(5)
        raise Exception
    except ValueError:
        root = tkinter.Tk()
        root.withdraw()
        # 获取选择文件夹的绝对路径
        GAME_PATH = filedialog.askdirectory(title='选择原神安装路径')
        if not os.path.exists(os.path.join(GAME_PATH, 'YuanShen.exe')):
            print('游戏路径错误,路径下应当包含YuanShen.exe')
            time.sleep(10)
            raise Exception
        else:
            try:
                uid, url = _URL().scanURL(GAME_PATH)
            except SystemError as e:
                print(str(e))
                time.sleep(5)
                raise Exception
            except ValueError:
                print('游戏目录错误！')
                time.sleep(10)
                raise Exception
    open(f'{uid.strip()}URL.txt','w+',encoding='UTF-8').write(url)
    print(f'已保存到文件 {uid.strip()}URL.txt')
    Tool.set_clipboard(url)
    print('已复制到剪贴板')
    time.sleep(5)
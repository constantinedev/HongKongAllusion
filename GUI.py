import io, os, sys, json, requests, youtube_dl, shutil, time
import PySimpleGUI as sg
from pytube.streams import Stream
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

software_names = [SoftwareName.CHROME.value]
operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]   
user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)
user_agent = user_agent_rotator.get_random_user_agent()

Apptitle = '香港長故'
sg.theme('SystemDefault')

headers = {
    'User-Agent': user_agent,
    'Content-Type': 'application/json'
}
payload = {}

session = requests.session()
session.proxies = {}
session.proxies['http'] = 'socks5h://localhost:9050'
session.proxies['https'] = 'socks5h://localhost:9050'

MENU_JSON = 'https://raw.githubusercontent.com/constantinedev/HongKongAllusion/main/dwn_menu.json'

class pre_options():
    menu_req = session.get(MENU_JSON, headers=headers, data=payload)
    if menu_req.status_code == 200:
        menu_res = menu_req.text
        menu_loads = json.loads(menu_res)
        offic_lst = menu_loads['office']
        opts_lst = menu_loads['options']
        menu_req.close()
    else:
        sg.popup('Server Error - 系統問題\n請通知@HKIGBot')
    
    DataDir = 'resultes'
    if not os.path.exists(DataDir):
        os.mkdir('resultes')
    else:
        pass

layout = [
        [sg.Text('媒體'), sg.Combo(list(pre_options.offic_lst), enable_events=True, key='office', size=(40, 5))],
        [sg.Text('類型'), sg.Combo(['圖片', '影片'], key='opts', size=(15, 5)), sg.Button('全自動備份', key='start_btn'), sg.Button('停止', key='stop_btn')],
        [sg.Output(size=(80, 20), key='res_dp')]
    ]

window = sg.Window(title=str(Apptitle), layout=layout)
    
def img_downloader(post_id, savdir, FileName, dw_url):
    if FileName + '.jpg' in os.listdir(savdir):
        print(str(post_id) + " => 已下載 - Downloaded")
        pass
    else:
        if dw_url is not None:
            req = requests.get(str(dw_url), stream=True, headers=headers, data=payload)
            if req.status_code == 200:
                try:
                    with open(savdir + FileName + '.jpg', 'wb') as dw_img:
                        shutil.copyfileobj(req.raw, dw_img)
                        dw_img.close()
                    print(str(post_id) + " => 完成 - Done" + str(req.status_code))
                    pass
                except:                
                    with open(savdir + FileName, 'wb') as dw_img:
                        shutil.copyfileobj(req.raw, dw_img)
                        dw_img.close()
                    print(str(post_id) + " => 完成 - Done " + str(req.status_code))
                    pass
            else:
                print(str(post_id) + " => Error Code: " + str(req.status_code))
                pass
            req.close()
        pass


def video_downloader(post_id, sav_dir, FileName, dw_url):
    dwn_url = str(dw_url).replace('https://www.youtube.com/embed/', 'https://www.youtube.com/watch?v=')
    with youtube_dl.YoutubeDL(payload) as ydl:
        meta_data = ydl.extract_info(dwn_url, download=False)
        video_title = meta_data.get('title', None)
    # json.dump(meta_data, sav_dir + post_id + '_' + FileName + '.json', ensure_ascii=False, indent=4)
    
    ydl_opts = {
        'format': 'bestvideo/best',
        'noplaylist': True,
        'outtmpl': sav_dir + FileName + '_' + video_title + '.%(ext)s',
    }
    
    # responser = requests.get(dwn_url, headers=headers, data=payload)
    # ts = responser.status_code()
    # responser.close()
        
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([dwn_url])

def main():
    while True:
        events, values = window.read()
        if events == sg.WIN_CLOSED:
            break
        if events == 'stop_btn':
            break
        
        if events == 'office':
            opts_upd = pre_options.opts_lst[str(values['office'])]
            off_lst = list(opts_upd)
            window['opts'].update(values=off_lst, size=(15, 5))
        
        if events == 'start_btn':
            offic = pre_options.offic_lst[str(values['office'])]
            opt = pre_options.opts_lst[str(values['office'])][str(values['opts'])]
            
            sav_dir = 'resultes/' + str(offic) + '/' + str(opt) + '/'            
            if not os.path.exists(sav_dir):
                os.makedirs(sav_dir)
                pass
            else:
                pass

            if opt == "photos":
                SELLST = "IMGLST"
            elif opt == 'videos':
                SELLST = "VIDEOLST"
            APIURI = "http://xpg5nj6en5j3hqbaw4vafhl2hveawii6w37sz6bof7zte47grdaucsad.onion/dwnreq.php?offic=" + offic + "&type_opt=" + SELLST
            
            responser = session.get(APIURI, headers=headers, data=payload)
            if responser.status_code == 200:
                res = str(responser.text).replace(', ]', ']')
            responser.close()
            
            JSONDATA = json.loads(res)
            for data in JSONDATA:
                poid = data['poid']
                FileName = data['Filename']
                dw_url = data['dw_url']
                
                if opt == "photos":
                    img_downloader(poid, sav_dir, FileName, dw_url)
                if opt == "videos":
                    video_downloader(poid, sav_dir, FileName, dw_url)
        
        # window['res_dp'].update("*任務完成(可重載抽樣500個項目)\n*Download Done(Reflash To Download New Items)!")
    # window.close()

if __name__ == '__main__':
    main()
    # window.close()

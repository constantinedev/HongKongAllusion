import io, os, sys, json, requests, youtube_dl, shutil, time
import PySimpleGUI as sg
# from random_user_agent.user_agent import UserAgent
# from random_user_agent.params import SoftwareName, OperatingSystem

# software_names = [SoftwareName.CHROME.value, SoftwareName.FIREFOX.value]
# operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
# user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)
# user_agent = user_agent_rotator.get_random_user_agent()

Apptitle = '香港長故'
sg.theme('SystemDefault')

payload = {}
headers = {
    # 'User-Agent': user_agent,
    'Content-Type': 'application/json'
}

session = requests.session()
session.proxies = {}
session.proxies['http'] = 'socks5h://localhost:9050'
session.proxies['https'] = 'socks5h://localhost:9050'

MENU_JSON = 'https://raw.githubusercontent.com/constantinedev/HongKongAllusion/main/dwn_menu.json'

class pre_options():
    DataDir = 'resultes'
    menu_req = session.get(MENU_JSON, headers=headers, data=payload)
    if menu_req.status_code == 200:
        menu_res = menu_req.text
        menu_loads = json.loads(menu_res)
        offic_lst = menu_loads['office']
        opts_lst = menu_loads['options']
        menu_req.close()
    else:
        sg.popup('Server Error - 系統問題\n請通知@HKIGBot')
        
layout = [
        [sg.Text('媒體'), sg.Combo(list(pre_options.offic_lst), enable_events=True, key='office', size=(40, 5))],
        [sg.Text('類型'), sg.Combo(['圖片', '影片'], key='opts', size=(15, 5)), sg.Button('全自動備份', key='start_btn'), sg.Button('停止', key='stop_btn')],
        [sg.Output(size=(120, 10), key='res_dp', background_color='black', text_color="#00FF00", echo_stdout_stderr=False)]
    ]

window = sg.Window(title=str(Apptitle), layout=layout)

def main():
    while True:
        events, values = window.read()
        if events == sg.WIN_CLOSED:
            break
        if events == 'stop_btn':
            window['res_dp'].update(values='')
            break
        
        if events == 'office':
            opts_upd = pre_options.opts_lst[str(values['office'])]
            off_lst = list(opts_upd)
            window['opts'].update(values=off_lst, size=(15, 5))
        
        if events == 'start_btn':
            offic = pre_options.offic_lst[str(values['office'])]
            opt = pre_options.opts_lst[str(values['office'])][str(values['opts'])]
            
            sav_dir = pre_options.DataDir + '/' + str(offic) + '/' + str(opt) + '/'
            if not os.path.exists(sav_dir):
                os.makedirs(sav_dir)
                pass
            else:
                pass

            if opt == "photos":
                SELLST = "IMGLST"
            elif opt == 'videos':
                SELLST = "VIDEOLST"
            elif opt == None:
                sg.popup('!!!未選取下載類別!!!')
                
            APIURI = "http://s3dlmo7jdfo2pe32t7mqtnbq4k3v7unk37nas3po544k2zvxgsj5juqd.onion/apis/dwnreq.php?offic=" + offic + "&type_opts=" + SELLST
            
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

def img_downloader(post_id, savdir, FileName, dw_url):
    if FileName + '.jpg' in os.listdir(savdir):
        print(str(post_id) + " => 已下載 - Downloaded")
        pass
    else:
        if dw_url is not None:
            req = requests.get(str(dw_url), stream=True,
                               headers=headers, data=payload)
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

def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, Do not close windows File Are Uploading...')
    if d['status'] == 'error':
        print(d['status'])
    if d['status'] == 'downloading':
        print(d['status'])

def video_downloader(post_id, sav_dir, FileName, dw_url):
    video_id = str(dw_url).replace('https://www.youtube.com/embed/', '')
    dwn_url = 'https://www.youtube.com/watch?v=' + str(video_id)
    
    ytdl_opts = {
        'format': '(bestvideo[ext=mp4][fps>30]/bestvideo[ext=mp4])+bestaudio[ext=m4a]',
        'nocheckcertificate': True,
        # 'User-Agent': user_agent,
        # 'download_archive': sav_dir + post_id + '_%(id)s_%(title)s.%(ext)s',
        # 'prefer_ffmpeg': True,
        'hls_prefer_native': True,
        'merge_output_format': 'mp4',
        'writeinfojson': True,
        'noplaylist': False,
        'cachedir': False,
        'newline': True,
        'external_downloader': 'wget',
        'outtmpl': sav_dir + post_id + '_%(id)s_%(title)s.%(ext)s',
        'progress_hooks': [my_hook],
    }

    try:
        with youtube_dl.YoutubeDL(ytdl_opts) as ydl:
            metaData = ydl.extract_info(dwn_url, download=False)
            video_title = metaData.get('title', None)
            print("DOWNLOADING: " + video_title)
            
            ydl.download([dwn_url])
            print("DOWNLOAD: " + video_title + ' Complet!')
    except:
        print(youtube_dl.utils.DownloadError)

if __name__ == '__main__':
    main()
    # window.close()

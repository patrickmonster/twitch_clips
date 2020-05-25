import os, sys
import json
import re # 정규식
import datetime
from PIL import Image, ImageDraw, ImageFont

version = "0.0.1"

# 주단위 필터 #2020-05-16T06:29:40Z
week_filter = re.compile(r'([0-9]+)-([0-9]+)-([0-9]+)T([0-9]+):([0-9]+):([0-9]+)Z')
day_filter = re.compile(r'(\d{4})(\d{2})(\d{2})')
client = "g1rhyzp1s7y2d755xqjn1otspdgvc3"

convert_file_option = {
    "start_video": False,#시작비디오
    "change_video":False,#변경비디오
    "end_video" : False,#끝비디오(아우트로)
    "img_font" : False ,# 안내 이미지 폰트
    "title":"yellow", #
    "scale":"1280x720",
    "channel":"",
    "option" : {
        "limit"   : "10", # max = 100
        "period"  : "week", #주간
        "trending": "false", # 조회순 / (true : 인기순)
        "game"    : "", # 콘텐츠 / 없으면 전부
    }
}


# logo = "ffmpeg -i input.mp4 -i logo.png -filter_complex 'overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2'"

video_root = os.getcwd() + "/video/"
clip_root = os.getcwd() + "/clip/"

if not os.path.isdir(os.getcwd()+"/data/"):
    os.mkdir(os.getcwd()+"/data/")

if not os.path.isdir(video_root):
    os.mkdir(video_root)

if not os.path.isdir(clip_root):
    os.mkdir(clip_root)

target = "https://api.twitch.tv/kraken/clips/top?"
clip_url = "https://clips.twitch.tv/embed?clip="

def get_list(week=-1,year=0,new=False):
    #파일 선점
    op = "&".join([i+"="+convert_file_option["option"][i] for i in convert_file_option["option"]]) + "&channel=" + convert_file_option["channel"]
    # json_file = "data/"+datetime.datetime.today().strftime("%Y%m%d%H%M") + ".tmp"
    if week == -1:
        json_file = "data/"+datetime.datetime.now().strftime("%Y_%W") + ".tmp"
    else :
        json_file = f"data/{year}_{week}.tmp"
    cmd = 'curl -H "Accept: application/vnd.twitchtv.v5+json" -H "Client-ID: '+client+'" "'+target+op +'" -o '+json_file
    if os.path.isfile(json_file) or new:
        print(os.system(cmd))
    with open(os.getcwd() + "/"+ json_file,'r',encoding="utf-8") as json_file:
        json_data = json.load(json_file)
    return json_data

def get_clips(l):#클립정보
    c = l["clips"]
    out = []
    for i in c:# 동영상 주요 정보 id / 제목/생성일/원본영상[offset/preview_image_url/url]/섬네일[medium/small/tiny]
        week = week_filter.findall(i["created_at"])[0]
        if len(week) > 2:
            out.append({"slug":i["slug"],"title":i["title"],"created_at":i["created_at"],"vod":i["vod"],"thumbnails":i["thumbnails"],"week":week})
    return out

def get_clip_file(target,file_date=""):
    if file_date == "":
        file_date = "%(upload_date)s"
    cmd = "youtube-dl -f 720 --output "+clip_root+"%(title)s_%(uploader)s_"+file_date+".%(ext)s https://clips.twitch.tv/embed?clip=" + target
    # print(cmd)
    print(os.system(cmd))

# 필터를 위한 함수
def get_video_week(filename):
    file_option = filename.split("_") # 0:title 1:uploader 2:upload_date
    if len(file_option) < 2:
        return 0
    print(file_option[2])
    date = day_filter.findall(file_option[2])[0]
    return int(datetime.date(int(date[0]),int(date[1]),int(date[2])).strftime("%W"))

#리스트 필터 (주간)
def get_list_week_file(week):
    videos = os.listdir(clip_root)
    if week == -1:
        return videos
    return list(filter(lambda index: get_video_week(index) == week,videos))

# 비디오 병합용 이름변경
def convert_video_name(list_to_video):
    out = {}
    count = 0
    size = len(str(len(list_to_video)))
    for i in list_to_video:
        out[i] = ('{0:0'+str(size)+'d}.mp4').format(count)
        count +=1
    return out


# 클립 타이틀
def make_title(title,color="yellow",font="neodgm.ttf"):
    target_img = Image.new("RGBA",(360,120),(0,0,0,0))
    selectFont = ImageFont.truetype(os.path.join(os.getcwd(),font),40)
    draw=ImageDraw.Draw(target_img)
    t=title
    if len(t) > 10:
        t = t[:10] + '\n' + t[10:]
    if len(t) > 21:
        t = t[:21] + '\n' + t[21:]
    draw.text((0,0),t,fill=color,font=selectFont)
    d = clip_root + "/"+title+".png"
    target_img.save(d)
    return d

# 비디오 합치기
def combine_video(list_video):
    if len(list_video) < 1:
        return # 리스트가 없음
    l = convert_video_name(list_video) # 비디오 변경
    txt = ""
    if convert_file_option["start_video"]:
        txt += "file '"+convert_file_option["start_video"]+"'\r\n"
    for i in l:
        txt += f"file '{l[i]}'\r\n"
        convert = f'ffmpeg -i "{clip_root + i}" -codec:v h264 -vf scale=1280x720 -codec:a copy {clip_root}'
        if convert_file_option["img_font"]: # 임시저장
            convert += "tmp.mp4"
        else :
            convert += l[i]
            print(convert)
        print(os.system(convert))

        if convert_file_option["img_font"]:#convert_file_option["img_font"]
            print("=======================================================")
            img_ti = make_title(i.split("_")[0])
            print(img_ti)
            convert = 'ffmpeg -y -i '+clip_root +'tmp.mp4 -i "'+img_ti+'" -filter_complex "overlay=W-w-5:H-h-5" ' + clip_root + l[i]
            print(os.system(convert)) # 이미지 변환
            os.remove(img_ti) # 타이틀 제거
            os.remove(clip_root +'tmp.mp4') # 파일제거

        if convert_file_option["change_video"] and i != list_video[-1]:
            txt += "file '"+convert_file_option["change_video"]+"'\r\n"

    if convert_file_option["end_video"]:
        txt += "file '"+convert_file_option["end_video"]+"'"
    with open(clip_root + "cmd.txt", "w") as f:
        f.writelines(txt)
    cmd = "ffmpeg -f concat -i " + clip_root + "cmd.txt -c copy " +video_root+ datetime.datetime.today().strftime("%Y%m%d%H%M")+ ".mp4"
    print(os.system(cmd)) # 명령실행

    os.remove(clip_root + "cmd.txt")
    for i in l:
        os.remove(clip_root + l[i]) # 파일제거

def indexOf(l,obj):
    try:
        return l.index(obj)
    except:
        return -1

helps="""
파일명 : clip.exe

-h
    설명서를 출력합니다

필수파일
    youtube-dl.exe  - 영상다운로드
    ffmpeg.exe      - 영상 변환 및 병합

기본옵션
-s : False
    인트로 비디오 - 경로를 적어주시면 됩니다.
-c : False
    화면전환 비디오 - 경로를 적어주시면 됩니다.
-e : False
    아웃트로 비디오 - 경로를 적어주시면 됩니다.
-img : False / true
    타이틀 이미지 여부
-title : yellow
    타이틀 이미지 색상 - 색상컬러를 영어로 적어주시면 됩니다
    [blue, black, yellow, red, 등]

다운로드 옵션
--limit : 10
    최대 다운로드 개수 [max - 100]
--period : week
    다운로드 범위 [day,week,month,all]
--trending
    인기순 / 조회순 [옵션을 추가할경우 인기순 :true]
    ex> --trending true
--game :
    검색영역 : [Just Chatting / League of Legends / VALORANT / Games + Demos]
    기본 : 전채
--channel :
    채널설정 기본적인 옵션입니다
    설정을 하지 않는경우, 프로그램이 동작하지 않습니다!

작업옵션
-load
    리스트를 갱신합니다
-down
    클립을 다운로드 합니다
    [클립을 다운로드 하지 않을경우 combine옵션에 오류가 생길 수 있습니다]
-combine
    영상을 병합합니다
"""

if __name__ == '__main__':
    # print(sys.argv)
    h = indexOf(sys.argv,"-h")
    if h != -1 or len(sys.argv) < 2:
        print(helps)
        sys.exit()
    ch_index = indexOf(sys.argv,"--channel")
    option = [indexOf(sys.argv,"--limit"),indexOf(sys.argv,"--period"),indexOf(sys.argv,"--trending"),indexOf(sys.argv,"--game")]
    if ch_index == -1 or sys.argv[ch_index+1].find("-") != -1:
        print("채널을 설정하지 않았습니다!\n\t--channel 채널ID")
        sys.exit()
    convert_file_option["channel"] = sys.argv[ch_index+1]
    keys = list(convert_file_option["option"].keys())
    for i in range(len(option)):
        if option[i] != -1:
            if sys.argv[option[i]+1].find("-") == -1:
                convert_file_option["option"][keys[i]] = sys.argv[option[i]+1]

    option = [indexOf(sys.argv,"-s"),indexOf(sys.argv,"-c"),indexOf(sys.argv,"-e"),indexOf(sys.argv,"-img"),indexOf(sys.argv,"-title")]

    keys = list(convert_file_option.keys())
    for i in range(len(option)):
        if option[i] != -1:
            if sys.argv[option[i]+1].find("-") == -1:
                convert_file_option[keys[i]] = sys.argv[option[i]+1]
    # 리스트 갱신 / 다운로드 / 병합
    option = [indexOf(sys.argv,"-load"),indexOf(sys.argv,"-down"),indexOf(sys.argv,"-combine"),indexOf(sys.argv,"-y")]

    if option[0] != -1: # 리스트 갱신여부
        # def get_list(week=-1,year=0,new=False):
        print("리스트를 불러옵니다....")
        l = get_clips(get_list(new=True)) # 리스트 불러오기
        for i in range(len(l)):
            print(f'{i+1}: {l[i]["title"]}\t{l[i]["slug"]}\t{l[i]["created_at"]}')
    if option[1] != -1:
        print("리스트를 불러옵니다....")
        l = get_clips(get_list()) # 리스트 불러오기
        for i in l:
            print(f'{i["title"]} 를 다운로드 시작...')
            get_clip_file(i["slug"])
    if option[2] != -1:
        print("영상을 합칠 준비를 하는중...")
        index = 0
        try:
            index = int(sys.argv[option[2]+1])
        except:
            index = -1
        l = get_list_week_file(index)

        print("\n\n 영상 리스트 - 순차적으로 들어 갑니다!\n")
        for i in l:
            print(i)

        print("\n\n 영상 합치기를 시작합니다... 영상 개수에 따라 5~20분정도 소요됩니다! \n")
        combine_video(l)

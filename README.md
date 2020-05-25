# twitch_clips

파일명 : clip.exe

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

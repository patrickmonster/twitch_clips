const {ipcRenderer, remote,shell, Menu, MenuItem} = require('electron');
const {execFile,execFileSync}= require('child_process');
const fs = require('fs');

const clientkey = "2ezfro5oy437x6a54ha5u5pm5s4vbs";
const values = {"down_list":[],"down_loading":[],"video_list":[],isProcessing:false};
const tag_id_options = {};
const tag_to_file = {};

const download_clip = function(key,callback){
  // if(!file_date)file_date = "%(upload_date)s";
  var youtube_dl =  __dirname + '\\lib\\youtube-dl.exe';
  values.down_loading.push(key);//'clip/%(title)s_%(uploader)s_'+file_date+'.%(ext)s'
  execFile('./lib/youtube-dl.exe', ['-f','720','--output','clip/%(title)s$'+key+'.%(ext)s','https://clips.twitch.tv/embed?clip='+key],  (error, stdout, stderr) => {
    if(error){
      console.log("error" , key,error);
      if (i != -1)down_list.splice(i,1);
      alert(key+"를 받는 도중, 에러가 발생하였습니다!");
    }else{
      console.log("load" , key);
      var i = values.down_loading.indexOf(key);
      if (i != -1)values.down_loading.splice(i,1);
    }
    if(callback)callback(key);
  });
};
const download_clips = function(keys,callback){
  if (values.isProcessing){
    alert("선 작업 진행중입니다! 끝난후에 다시 시도해 주세요!");
    return;
  }
  console.log(keys)
  ipcRenderer.send("PROCESSING-WORKING","ture");
  values.isProcessing = true;// 선 프로세서 작업
  var index = 0;
  keys.forEach(function(k){
    download_clip(k,function(key){
      // if (index != keys.length)return;
      if (callback)callback(key,index+1,keys.length);//현재 / 전채
      index ++;// 완료
      if (index+1 == keys.length){
        values.isProcessing = false;//프로세싱 완료
        ipcRenderer.send("PROCESSING-WORKING","false");
        if (callback)callback(keys.length + "작업완료!",0,0);//현재 / 전채
        values.down_loading.length = 0;
        reload();
      }
    });
  });
}

const get_file_lists = function(target,callback){
  fs.readdir(target, function(err, filelist){  // 배열 형태로 출력
    if(err)callback([]);
    else callback(filelist)
  })
}

const load_file = function(target){
  var element = target;
  remote.dialog.showOpenDialog(null,{filters: [
      { name: '비디오', extensions: ['mp4'] }
  ]}).then(result => {
    if(result.canceled)return;
    target.data("file",result.filePaths[0]);
    target.style.background="#70b0ff";
  }).catch(err => {
    console.log(err)
  });
}

function pad(n, width) {
  n = n + '';
  return n.length >= width ? n : new Array(width - n.length + 1).join('0') + n;
}

function getFormatDate(date){
    var year = date.getFullYear();              //yyyy
    var month = (1 + date.getMonth());          //M
    month = month >= 10 ? month : '0' + month;  //month 두자리로 저장
    var day = date.getDate();                   //d
    day = day >= 10 ? day : '0' + day;          //day 두자리로 저장
    return [year, month, day].join('_');
}

const convert_video_name = function(l){
  var out = {};
  l.forEach((i,j)=>{
    out[i] = pad(j,l.length)+".mp4";
  });
  return out;
}


const convert_video = function(callback){
  if(values.video_list.length <= 1){
    alert("선택된 파일이 없습니다!\n 최대 2개 이상 선택해주세요!");
    return;
  }
  if (values.isProcessing){
    alert("선 작업 진행중입니다! 끝난후에 다시 시도해 주세요!");
    return;
  }
  values.isProcessing = true;// 선 프로세서 작업
  ipcRenderer.send("PROCESSING-WORKING","true");
  alert("파일 병합에 들어갑니다 - (cpu 점유 100%)");
  if(callback)callback("변환을 준비중..." + values.video_list.length);
  var convert_org_list = [];
  values.video_list.forEach(i => {
    convert_org_list.push(tag_to_file[i]);
  });

  var list = convert_video_name(convert_org_list);
  //파일명 변경 리스트

  var convert_list = [];

  var f = document.getElementById("video_clip_in");
  if (f.data("file")) {
    execFileSync('./lib/ffmpeg.exe', ['-i',f.data("file"),'-y','-codec:v','h264','-vf','scale=1280x720','-codec:a','copy','.\\clip\\start.mp4']);
    convert_list.push("start.mp4");
  }

  // f = document.getElementById("video_clip_middle");
  // if (f.data("file")) {
  //   execFileSync('./lib/ffmpeg.exe', ['-i',f.data("file"),'-y','-codec:v','h264','-vf','scale=1280x720','-codec:a','copy','.\\clip\\in.mp4']);
  // }
  var count = 0;
  for (var i in list){
    count++;
    if(callback)callback("수정:" + list[i] + "/" + i + "\t" + count+"/"+convert_org_list.length);
    fs.renameSync('.\\clip\\'+i,'.\\clip\\tmp.mp4');
    execFileSync('./lib/ffmpeg.exe', ['-i','.\\clip\\tmp.mp4','-y','-codec:v','h264','-vf','scale=1280x720','-codec:a','copy','.\\clip\\'+list[i]]);
    convert_list.push(list[i]);
    if(f.data("file"))convert_list.push("in.mp4");// 중간 화면전환
  }


  f = document.getElementById("video_clip_out");
  if (f.data("file")) {
    execFileSync('./lib/ffmpeg.exe', ['-i',f.data("file"),'-y','-codec:v','h264','-vf','scale=1280x720','-codec:a','copy','.\\clip\\end.mp4']);
    convert_list.push("end.mp4");
  }

  console.log(convert_list);

  var cmd = "";
  convert_list.forEach(i => {
    cmd += "file '"+i+"'\r\n";
  });

  fs.writeFileSync('.\\clip\\cmd.txt',cmd);// 변환파일
  var out_file_name = getFormatDate(new Date())+".mp4";
  if(callback)callback("파일을 병합하는중...." + out_file_name);
  execFileSync('./lib/ffmpeg.exe', ['-f','concat','-i','./clip/cmd.txt','-y','-c','copy','.\\video\\'+out_file_name]);

  if(callback)callback("파일을 원상복귀 하는중...");
  for (var i in list){
    fs.renameSync('.\\clip\\'+list[i],'.\\clip\\'+i);
  }
  fs.unlinkSync('.\\clip\\tmp.mp4');
  fs.unlinkSync('.\\clip\\cmd.txt');
  if(callback)callback("병합완료");
  // shell.openExternal('.\\video\\'+out_file_name);
  values.isProcessing = false;// 선 프로세서 작업
  ipcRenderer.send("PROCESSING-WORKING","false");
}

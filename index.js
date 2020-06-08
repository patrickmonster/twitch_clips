const {app,net, BrowserWindow,Menu, shell, ipcMain} = require('electron');
const fs = require('fs');// 파일 리스트
const mkdir =  dir=>{!fs.existsSync(dir) && fs.mkdirSync(dir);}

let mainWindow;
let isProcessing = "false";
app.on('ready', createWindow);

ipcMain.on("PROCESSING-WORKING", (event,arg)=>{
    console.log("이벤트",arg);
    isProcessing = arg;
});

// 폴더 없으면 생성
mkdir("video");mkdir("clip");

function createWindow(){
  mainWindow = new BrowserWindow({
      height:900,
      width: 800,
      // frame: false,
      webPreferences: {
          nodeIntegration: true
          // webSecurity: false
      }
  });
//   mainWindow.setMenuBarVisibility(false);// 매뉴 숨기기
  require('./js/title_menu.js');//매뉴
//   mainWindow.webContents.openDevTools();//개발자 툴
    mainWindow.on('close', (event) => {
        console.log(isProcessing, isProcessing === "true");
        if(isProcessing === "true") {
            console.log("다이얼로그 생성");
            let response = dialog.showMessageBoxSync({
                title: '잠깐만요!',
                type: 'warning',
                buttons: ["확인"],
                message: '프로세서가 동작중입니다!'
            });
        }
    });
  mainWindow.loadURL(`file://${__dirname}/index.html`)
}

app.on('window-all-closed', () => {
    if(process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if(BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});

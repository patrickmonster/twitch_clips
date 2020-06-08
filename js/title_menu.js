const {Menu, shell} = require('electron');
const menu = Menu.buildFromTemplate( [
  {
      label: '개발자',
      submenu: [
          {label: '방송 이펙트',click:function(){shell.openExternal('https://patrickmonster.github.io/tgd/');}}
      ]
  }
]);
Menu.setApplicationMenu(menu);

/* eslint-disable no-param-reassign */
const { app, BrowserWindow, ipcMain } = require("electron");
const path = require("path");
const fs = require("fs");
const { spawn } = require("child_process");
const spawnWIN = require('cross-spawn');
const { stderr, kill } = require("process");
const open = require("open");
const isDev = require("electron-is-dev");
const treekill = require("tree-kill");

const binary_dir = path.join(__dirname, "../binaries");

let cache_dir;
if (isDev) {
  console.log("Running in development");
  cache_dir = binary_dir;
} else {
  console.log("Running in production");
  cache_dir = path.join(app.getPath("cache"), app.getName());
}
console.log("cache dir is", cache_dir);
spawn("mkdir", [`"${cache_dir}"`], {detached:true,shell: process.platform == 'win32'});

let pyCliStat = {
  process: null,
  running: false,
  numInstances: 0,
  stdout: "",
  stderr: "",
  error: null,
};

// Handle creating/removing shortcuts on Windows when installing/uninstalling.
// eslint-disable-next-line global-require
if (require("electron-squirrel-startup")) {
  // eslint-disable-line global-require
  app.quit();
}

const createWindow = () => {
  // Create the browser window.
  const mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nodeIntegration: true,
    },
  });

  mainWindow.maximize();
  // and load the index.html of the app.
  mainWindow.loadFile(path.join(__dirname, "index.html"));

  // Open the DevTools.
  if(isDev)
    mainWindow.webContents.openDevTools();
};

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.on("ready", createWindow);

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    if (pyCliStat.process) {
      if(process.platform == 'win32')
        treekill(pyCliStat.process.pid);
      else
        kill(pyCliStat.process.pid);
    }
    app.quit();
  }
});

app.on("activate", () => {
  // On OS X it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and import them here.

ipcMain.on("switch_page", (event, arg) => {
  const filePath = path.join(__dirname, arg);
  const windows = BrowserWindow.getAllWindows();

  if (!fs.existsSync(filePath) || windows.length !== 1) return;
  windows[0].loadFile(filePath);
});

const runCLI = async (arg) => {
  const commandArgs = [];
  arg.files.forEach((file) => {
    commandArgs.push("-f");
    commandArgs.push(`"${file}"`);
  });
  if (arg.onlyHost) {
    commandArgs.push("--only-host");
  }

  if (arg.qr) {
    commandArgs.push("--qr");
  }
  const command = `"${binary_dir.toString()}/LocalParty${process.platform == 'win32'?'.exe':''}"`;
  console.log(command);
  
  const pyCli = spawnWIN(command, commandArgs, {
    cwd: cache_dir,
    shell: true,
    detached: false,
  });
  
  pyCliStat.process = pyCli;
  pyCliStat.numInstances += 1;

  pyCli.stdout.on("data", (data) => {
    console.log(`${data}`);
    pyCliStat.stdout += data;
  });

  pyCli.stderr.on("data", (data) => {
    console.log(stderr);
    pyCliStat.stderr += data;
  });

  pyCli.on("error", (error) => {
    pyCliStat.error = error;
    console.log(error);
  });

  pyCli.on("close", (code) => {
    console.log(`child process exited with code ${code}`);

    pyCliStat = {
      process: null,
      running: false,
      numInstances: 0,
      stdout: "",
      stderr: "",
      error: null,
    };
  });
};

ipcMain.on("start_cli", async (event, arg) => {
  if (pyCliStat.process) return;
  runCLI(arg);
});

// eslint-disable-next-line no-unused-vars
ipcMain.on("terminalOutput", (event, arg) => {
  if (!pyCliStat.process) {
    event.reply("terminalOutput", "No process found");
    return;
  }
  event.reply("terminalOutput", pyCliStat.stdout);
  event.reply("terminalOutput", pyCliStat.stderr);
  pyCliStat.stdout = "";
  pyCliStat.stderr = "";
});

// eslint-disable-next-line no-unused-vars
ipcMain.on("show_qr", (event) => {
  open(path.join(cache_dir, "invite_link.png"));
});
// eslint-disable-next-line no-unused-vars
ipcMain.on("killCLI", (event, arg) => {
  if (!pyCliStat.process) return;

  if(process.platform == 'win32')
    treekill(pyCliStat.process.pid);
  else
    kill(pyCliStat.process.pid);

  console.log("CLI killed");

  pyCliStat = {
    process: null,
    running: false,
    numInstances: 0,
    stdout: "",
    stderr: "",
    error: null,
  };
});

// eslint-disable-next-line no-unused-vars
ipcMain.on("show_video", (event, arg) => {
  const streamLink = fs.readFileSync(path.join(cache_dir, "invite_link.txt"), {
    encoding: "utf-8",
    flag: "r",
  });
  const hostLink = streamLink.replace("client", "host");
  open(hostLink);
});

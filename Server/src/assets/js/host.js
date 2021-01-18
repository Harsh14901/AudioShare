/* eslint-disable no-undef */
/* eslint-disable no-unused-vars */
const addr = location.host;
console.log(addr);
const getParams = function (url) {
  const params = {};
  const parser = document.createElement('a');
  parser.href = url;
  const query = parser.search.substring(1);
  const vars = query.split('&');
  for (let i = 0; i < vars.length; i++) {
    const pair = vars[i].split('=');
    params[pair[0]] = decodeURIComponent(pair[1]);
  }
  return params;
};

let current_video_index = 0;

const search = vidioFile => {
  videoPaths.forEach(file => {
    if (file === vidioFile) return file;
  });
};

const ogg2mkv = file => {
  return file.substr(0, file.length - 3) + 'mkv';
};

const mkv2ogg = file => {
  return file.substr(0, file.length - 3) + 'ogg';
};

const url_from_file = filePath => {
  return `http://${addr}/api/listen?path=${encodeURIComponent(
    ogg2mkv(filePath)
  )}`;
};

const socket = io(`http://${addr}/`);

const maxError = 0.4;
const eventTimeDiff = 1;
const interval = 1000;
let networkOffset = 0;
let disableEventListener = false;
let onlyHost = false;

let userId = '';
const roomId = getParams(location.href).roomId;
const videoPaths = [];
// let trackId = '';

const getNetworkOffset = async () => {
  const reqStart = new Date().getTime();
  const response = await axios.get(`http://${addr}/time`);
  const time = response.data.time;
  const reqEnd = new Date().getTime();
  networkOffset = ((reqEnd + reqStart) / 2 - time) / 1000;
  console.log('Network Latency predicted as ' + networkOffset);
};
getNetworkOffset();

const video = document.getElementById('videosrc');
let lastState = {};
let lastRecievedAt = 0;

setInterval(() => {
  if (video.readyState !== 4 || lastState === {}) return;
  if (lastState.is_playing) video.play();
  else video.pause();
  const expectedPosition = lastState.is_playing
    ? new Date().getTime() / 1000 -
      lastState.last_updated +
      lastState.position -
      networkOffset
    : lastState.position;
  if (Math.abs(video.currentTime - expectedPosition) >= maxError) {
    console.log('Syncing now...');
    disableEventListener = true;
    video.currentTime = expectedPosition;
    setTimeout(() => {
      disableEventListener = false;
    }, interval);
  } else {
    console.log('The sync offset is less than 1sec');
  }
}, interval);

const setPlaybackTime = data => {
  lastRecievedAt = new Date().getTime() / 1000;
  console.log('Recieved data at' + lastRecievedAt);
  video.currentTime =
    data.position + lastRecievedAt - data.last_updated - networkOffset;
  console.log('setting current time to ' + video.currentTime);
};
document.getElementById('startParty').addEventListener('click', () => {
  socket.emit('joinRoom', {
    roomId: roomId,
  });
  socket.emit('makeMeHost', {
    roomId: roomId,
  });
});

const getFileNameFromPath = path => {
  let fileName = path.substring(path.lastIndexOf('\\') + 1);
  if (fileName.endsWith('ogg'))
    fileName = fileName.substring(0, fileName.length - 3);
  return fileName;
};

socket.on('roomDetails', data => {
  console.log('Recieved room details');
  $('#startParty')
    .text('success')
    .addClass('btn-success')
    .removeClass('btn-outline-success');
  const fileName = getFileNameFromPath(data.currentAudioPath);
  setTimeout(() => {
    $('#startParty').hide();
    $('#track-info')
      .show()
      .find('span')
      .text(`${fileName} - (${current_video_index})`);
  }, 2000);
  console.log(data);
  lastState = data.state;
  onlyHost = data.onlyHost;
  data.audioPaths.forEach(p => {
    videoPaths.push(ogg2mkv(p));
  });
  current_video_index = data.audioPaths.indexOf(data.currentAudioPath);
  console.log(current_video_index);
  video.src = url_from_file(data.currentAudioPath);
});

socket.on('addTrack', data => {
  videoPaths.push(ogg2mkv(data.audioPath));
});
socket.on('joinRoom', data => {
  console.log('Present state is: ');
  console.log(data.state);
  lastState = data.state;
  onlyHost = data.onlyHost;
});

socket.on('userId', data => {
  console.log(data);
  userId = data.userId;
});

socket.on('sendMessage', msg => {
  console.log('Recieved a message from the server');
  console.log(msg);
});

socket.on('pause', data => {
  disableEventListener = true;

  console.log('Pausing playback');
  video.currentTime = data.position;
  video.pause();
  console.log(data);
  lastState = data;
  setTimeout(() => {
    disableEventListener = false;
  }, interval);
});

socket.on('play', data => {
  disableEventListener = true;

  console.log('playing audio');
  console.log('Play data recieved');
  console.log(data);

  setPlaybackTime(data);
  video.play();
  console.log(data);
  lastState = data;

  setTimeout(() => {
    disableEventListener = false;
  }, interval);
});

socket.on('seek', data => {
  disableEventListener = true;
  console.log('Seeking audio buffer');
  setPlaybackTime(data);
  console.log('Is playing: ' + data.is_playing);
  lastState = data;
  console.log('Seek data recieved');
  console.log(data);

  setTimeout(() => {
    disableEventListener = false;
  }, interval);
});

$('#back').on('click', () => {
  console.log('back clicked');
  if (current_video_index === 0) return;

  video.src = url_from_file(videoPaths[current_video_index - 1]);
  const fileName = getFileNameFromPath(videoPaths[current_video_index - 1]);
  $('#track-name').text(`${fileName} - (${current_video_index - 1})`);

  lastState.last_updated = new Date().getTime() / 1000;
  lastState.expectedPosition = 0;
  lastState.is_playing = false;
  video.pause();

  socket.emit('changeTrack', {
    audioPath: mkv2ogg(videoPaths[current_video_index - 1]),
    state: lastState,
  });
  current_video_index--;
});

$('#next').on('click', () => {
  console.log('next clicked');
  if (current_video_index === videoPaths.length - 1) return;

  video.src = url_from_file(videoPaths[current_video_index + 1]);
  const fileName = getFileNameFromPath(videoPaths[current_video_index + 1]);
  $('#track-name').text(`${fileName} - (${current_video_index + 1})`);

  lastState.last_updated = new Date().getTime() / 1000;
  lastState.position = 0;
  lastState.is_playing = false;
  video.pause();
  socket.emit('changeTrack', {
    audioPath: mkv2ogg(videoPaths[current_video_index + 1]),
    state: lastState,
  });
  current_video_index++;
});

video.addEventListener('play', event => {
  if (disableEventListener || onlyHost) return;
  console.log('Play event detected');
  lastState.last_updated = new Date().getTime() / 1000 - networkOffset;
  lastState.position = video.currentTime;
  lastState.is_playing = true;
  socket.emit('play', lastState);
});
video.addEventListener('pause', event => {
  if (disableEventListener || onlyHost) return;
  console.log('Pause event detected');
  lastState.last_updated = new Date().getTime() / 1000 - networkOffset;
  lastState.position = video.currentTime;
  lastState.is_playing = false;
  socket.emit('pause', lastState);
});
video.addEventListener('seeked', event => {
  if (disableEventListener || !video.paused || onlyHost) return;
  console.log('audio.paused is :' + video.paused);
  console.log('Seek event detected');
  lastState.last_updated = new Date().getTime() / 1000 - networkOffset;
  lastState.position = video.currentTime;
  console.log(lastState);
  socket.emit('seek', lastState);
});

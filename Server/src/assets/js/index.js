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

const socket = io(`http://${addr}/`);

const maxError = 0.15;
const eventTimeDiff = 1;
const interval = 1000;
let networkOffset = 0;
let disableEventListener = false;
let onlyHost = false;

let userId = '';
const roomId = getParams(location.href).roomId;
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

const audio = document.getElementById('audiosrc');
let lastState = {};
let lastRecievedAt = 0;

setInterval(() => {
  if (audio.readyState !== 4 || lastState === {}) return;
  if (lastState.is_playing) audio.play();
  else audio.pause();
  const expectedPosition = lastState.is_playing
    ? new Date().getTime() / 1000 -
      lastState.last_updated +
      lastState.position -
      networkOffset +
      0.2
    : lastState.position;
  console.log(audio.currentTime - expectedPosition);
  if (Math.abs(audio.currentTime - expectedPosition) >= maxError) {
    console.log('Syncing now...');
    disableEventListener = true;
    audio.currentTime = expectedPosition;
    setTimeout(() => {
      disableEventListener = false;
    }, interval);
  } else {
    console.log('The sync offset is less than 1sec');
  }
}, interval);

const setPlaybackTime = data => {
  lastRecievedAt = new Date().getTime() / 1000;
  console.log('Recieved data at ' + lastRecievedAt);
  audio.currentTime =
    data.position + lastRecievedAt - data.last_updated - networkOffset;
  console.log('setting current time to ' + audio.currentTime);
};
document.getElementById('joinRoom').addEventListener('click', () => {
  socket.emit('joinRoom', {
    roomId: roomId,
  });
});

socket.on('joinRoom', data => {
  console.log('Present state is: ');
  console.log(data);
  lastState = data.state;
  onlyHost = data.onlyHost;
});

socket.on('userId', data => {
  console.log(data);
  userId = data.userId;
});

socket.on('audioPath', data => {
  console.log(data);
  audioPath = data.audioPath;
  audio.src = `http://${addr}/api/listen?path=${audioPath}`;
  $('#joinRoom')
    .text('success')
    .addClass('btn-success')
    .removeClass('btn-outline-success');
  console.log();
});

socket.on('sendMessage', msg => {
  console.log('Recieved a message from the server');
  console.log(msg);
});

socket.on('pause', data => {
  disableEventListener = true;

  console.log('Pausing playback');
  audio.currentTime = data.position;
  audio.pause();
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
  audio.play();
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

audio.addEventListener('play', event => {
  if (disableEventListener || onlyHost) return;
  console.log('Play event detected');
  lastState.last_updated = new Date().getTime() / 1000 - networkOffset;
  lastState.position = audio.currentTime;
  lastState.is_playing = true;
  socket.emit('play', lastState);
});
audio.addEventListener('pause', event => {
  if (disableEventListener || onlyHost) return;
  console.log('Pause event detected');
  lastState.last_updated = new Date().getTime() / 1000 - networkOffset;
  lastState.position = audio.currentTime;
  lastState.is_playing = false;
  socket.emit('pause', lastState);
});
audio.addEventListener('seeked', event => {
  if (disableEventListener || !audio.paused || onlyHost) return;
  console.log('audio.paused is :' + audio.paused);
  console.log('Seek event detected');
  lastState.last_updated = new Date().getTime() / 1000 - networkOffset;
  lastState.position = audio.currentTime;
  console.log(lastState);
  socket.emit('seek', lastState);
});

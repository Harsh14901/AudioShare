import app from './app';

const server = app.listen(app.get('port'), () => {
  console.log(`App is Running at http://localhost:${app.get('port')}`);
  console.log('  Press CTRL-C to stop\n');
});

import * as socketio from 'socket.io';
const io = socketio.listen(server);
import socket from './sockets';
socket(io);

export default server;

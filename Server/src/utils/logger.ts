import * as winston from 'winston';
import {format} from 'winston';
import * as traverse from 'traverse';

const isSensitive = (key: string | undefined) => {
  switch (key) {
    case 'password':
    case 'token':
      return true;
  }
  return false;
};

const removeSensitiveData = format(info => {
  traverse(info).forEach(function (_) {
    if (isSensitive(this.key)) this.update('[REDACTED]');
  });
  return info;
});

const logger = winston.createLogger({
  format: format.combine(removeSensitiveData(), format.json()),
  transports: [
    new winston.transports.Console({
      level: process.env.NODE_ENV === 'production' ? 'error' : 'debug',
    }),
    new winston.transports.File({filename: 'debug.log', level: 'debug'}),
  ],
});

if (process.env.NODE_ENV !== 'production') {
  logger.debug('Logging initialized at debug level');
}

export default logger;

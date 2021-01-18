import * as express from 'express';
import {listen_local} from '../controllers/track';

const router = express.Router();

// router.post('/upload', upload, postAudio);
router.get('/listen', listen_local);

export default router;

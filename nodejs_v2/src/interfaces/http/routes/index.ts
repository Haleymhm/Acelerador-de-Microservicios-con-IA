import { Router } from 'express';
import multer from 'multer';
import { AIController } from '../controllers/AIController';

const router = Router();
const upload = multer({ storage: multer.memoryStorage() });

router.post('/generate-text', AIController.generateText);
router.post('/analyze-image', upload.single('image'), AIController.analyzeImage);

export default router;

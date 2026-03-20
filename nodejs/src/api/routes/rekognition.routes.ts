import { Router } from "express";
import multer from "multer";
import { detectLabelsController } from "../controllers/rekognition.controller";

const router = Router();
const upload = multer({ storage: multer.memoryStorage() });

router.post("/detect-labels", upload.single("image"), detectLabelsController);

export default router;

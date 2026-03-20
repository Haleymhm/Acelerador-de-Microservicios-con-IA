import { Router } from "express";
import { synthesizeSpeechController } from "../controllers/polly.controller";

const router = Router();

router.post("/synthesize-speech", synthesizeSpeechController);

export default router;

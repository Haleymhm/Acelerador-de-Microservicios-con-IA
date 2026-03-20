import { Router } from "express";
import { detectSentimentController } from "../controllers/comprehend.controller";

const router = Router();

router.post("/detect-sentiment", detectSentimentController);

export default router;

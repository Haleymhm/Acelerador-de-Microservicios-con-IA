import { Router } from "express";
import rekognitionRoutes from "./rekognition.routes";
import comprehendRoutes from "./comprehend.routes";
import pollyRoutes from "./polly.routes";

const router = Router();

router.use("/rekognition", rekognitionRoutes);
router.use("/comprehend", comprehendRoutes);
router.use("/polly", pollyRoutes);

export default router;

import { Request, Response } from "express";
import { detectLabelsInImage } from "../services/rekognition.service";

export const detectLabelsController = async (req: Request, res: Response) => {
  if (!req.file) {
    return res.status(400).send("No file uploaded.");
  }

  try {
    const labels = await detectLabelsInImage(req.file.buffer);
    res.json(labels);
  } catch (error) {
    res.status(500).send(error.message);
  }
};

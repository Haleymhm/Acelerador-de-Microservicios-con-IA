import { Request, Response } from "express";
import { synthesizeSpeechFromText } from "../services/polly.service";
import { Readable } from "stream";

export const synthesizeSpeechController = async (req: Request, res: Response) => {
  const { text } = req.body;

  if (!text) {
    return res.status(400).send("The 'text' field is required in the request body.");
  }

  try {
    const audioStream = await synthesizeSpeechFromText(text);

    if (audioStream instanceof Readable) {
      res.setHeader("Content-Type", "audio/mpeg");
      audioStream.pipe(res);
    } else {
      throw new Error("Audio stream is not available.");
    }
  } catch (error) {
    res.status(500).send(error.message);
  }
};

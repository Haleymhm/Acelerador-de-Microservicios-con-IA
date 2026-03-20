import { Request, Response } from "express";
import { detectSentimentInText } from "../services/comprehend.service";

export const detectSentimentController = async (req: Request, res: Response) => {
  const { text } = req.body;

  if (!text) {
    return res.status(400).send("The 'text' field is required in the request body.");
  }

  try {
    const sentiment = await detectSentimentInText(text);
    res.json(sentiment);
  } catch (error) {
    res.status(500).send(error.message);
  }
};

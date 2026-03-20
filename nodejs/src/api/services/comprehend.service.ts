import { DetectSentimentCommand, DetectSentimentCommandInput } from "@aws-sdk/client-comprehend";
import { comprehendClient } from "../../config/aws";

export const detectSentimentInText = async (text: string) => {
  const input: DetectSentimentCommandInput = {
    Text: text,
    LanguageCode: "en", // o el idioma que prefieras
  };

  const command = new DetectSentimentCommand(input);

  try {
    const response = await comprehendClient.send(command);
    return {
      Sentiment: response.Sentiment,
      SentimentScore: response.SentimentScore,
    };
  } catch (error) {
    console.error("Error detecting sentiment:", error);
    throw new Error("Failed to detect sentiment in the text.");
  }
};

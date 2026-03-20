import { DetectLabelsCommand, DetectLabelsCommandInput } from "@aws-sdk/client-rekognition";
import { rekognitionClient } from "../../config/aws";

export const detectLabelsInImage = async (imageBuffer: Buffer) => {
  const input: DetectLabelsCommandInput = {
    Image: {
      Bytes: imageBuffer,
    },
    MaxLabels: 10,
    MinConfidence: 90,
  };

  const command = new DetectLabelsCommand(input);
  
  try {
    const response = await rekognitionClient.send(command);
    return response.Labels;
  } catch (error) {
    console.error("Error detecting labels:", error);
    throw new Error("Failed to detect labels in the image.");
  }
};

import { SynthesizeSpeechCommand, SynthesizeSpeechCommandInput } from "@aws-sdk/client-polly";
import { pollyClient } from "../../config/aws";

export const synthesizeSpeechFromText = async (text: string) => {
  const input: SynthesizeSpeechCommandInput = {
    Text: text,
    OutputFormat: "mp3",
    VoiceId: "Joanna", // Puedes elegir la voz que prefieras
  };

  const command = new SynthesizeSpeechCommand(input);

  try {
    const response = await pollyClient.send(command);
    // El SDK v3 devuelve el stream de audio en la propiedad 'AudioStream'
    return response.AudioStream;
  } catch (error) {
    console.error("Error synthesizing speech:", error);
    throw new Error("Failed to synthesize speech from the text.");
  }
};

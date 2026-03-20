import { PollyClient, SynthesizeSpeechCommand, VoiceId } from '@aws-sdk/client-polly';
import { IAudioService } from '../../../domain/ports/IAudioService';
import { configService } from '../../../shared/config/ConfigService';
import { AppError } from '../../../shared/errors/AppError';
import { logger } from '../../../shared/logger';
import { Readable } from 'stream';

export class AwsPollyService implements IAudioService {
  private client: PollyClient;

  constructor() {
    this.client = new PollyClient({ region: configService.config.AWS_REGION });
  }

  async synthesizeSpeech(text: string, voiceId?: string): Promise<Buffer> {
    const command = new SynthesizeSpeechCommand({
      Engine: 'neural',
      OutputFormat: 'mp3',
      Text: text,
      VoiceId: (voiceId || 'Joanna') as VoiceId,
    });

    try {
      const response = await this.client.send(command);
      const audioStream = response.AudioStream as Readable;
      
      if (!audioStream) {
        throw new Error('No audio stream returned.');
      }

      return new Promise<Buffer>((resolve, reject) => {
        const chunks: Buffer[] = [];
        audioStream.on('data', chunk => chunks.push(chunk));
        audioStream.on('end', () => resolve(Buffer.concat(chunks)));
        audioStream.on('error', err => reject(err));
      });
      
    } catch (error: any) {
      logger.error(`Polly synthesizeSpeech error: ${error.message}`, { error });
      throw new AppError(`Failed to synthesize speech: ${error.message}`, 502);
    }
  }
}

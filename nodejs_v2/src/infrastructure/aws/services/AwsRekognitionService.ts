import { RekognitionClient, DetectLabelsCommand, DetectFacesCommand } from '@aws-sdk/client-rekognition';
import { IVisionService, ILabel, IFaceDetail } from '../../../domain/ports/IVisionService';
import { configService } from '../../../shared/config/ConfigService';
import { AppError } from '../../../shared/errors/AppError';
import { logger } from '../../../shared/logger';

export class AwsRekognitionService implements IVisionService {
  private client: RekognitionClient;

  constructor() {
    this.client = new RekognitionClient({ region: configService.config.AWS_REGION });
  }

  async detectLabels(imageBuffer: Buffer): Promise<ILabel[]> {
    const command = new DetectLabelsCommand({
      Image: { Bytes: imageBuffer },
      MaxLabels: 10,
      MinConfidence: 75,
    });

    try {
      const response = await this.client.send(command);
      return (response.Labels || []).map(label => ({
        name: label.Name || 'Unknown',
        confidence: label.Confidence || 0,
      }));
    } catch (error: any) {
      logger.error(`Rekognition detectLabels error: ${error.message}`, { error });
      throw new AppError(`Vision Service failed: ${error.message}`, 502);
    }
  }

  async detectFaces(imageBuffer: Buffer): Promise<IFaceDetail[]> {
    const command = new DetectFacesCommand({
      Image: { Bytes: imageBuffer },
      Attributes: ['ALL'],
    });

    try {
      const response = await this.client.send(command);
      return (response.FaceDetails || []).map(face => ({
        confidence: face.Confidence || 0,
        gender: face.Gender?.Value,
        emotions: face.Emotions?.map(e => ({ type: e.Type || 'Unknown', confidence: e.Confidence || 0 })),
      }));
    } catch (error: any) {
      logger.error(`Rekognition detectFaces error: ${error.message}`, { error });
      throw new AppError(`Vision Service failed: ${error.message}`, 502);
    }
  }
}

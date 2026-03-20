import { TextractClient, DetectDocumentTextCommand, StartDocumentTextDetectionCommand, GetDocumentTextDetectionCommand } from '@aws-sdk/client-textract';
import { IDocumentService } from '../../../domain/ports/IDocumentService';
import { configService } from '../../../shared/config/ConfigService';
import { AppError } from '../../../shared/errors/AppError';
import { logger } from '../../../shared/logger';

export class AwsTextractService implements IDocumentService {
  private client: TextractClient;

  constructor() {
    this.client = new TextractClient({ region: configService.config.AWS_REGION });
  }

  async extractText(documentBuffer: Buffer): Promise<string> {
    const command = new DetectDocumentTextCommand({
      Document: { Bytes: documentBuffer },
    });

    try {
      const response = await this.client.send(command);
      const lines = (response.Blocks || [])
        .filter(block => block.BlockType === 'LINE')
        .map(block => block.Text || '');
        
      return lines.join('\n');
    } catch (error: any) {
      logger.error(`Textract extractText error: ${error.message}`, { error });
      throw new AppError(`Document Text Extraction failed: ${error.message}`, 502);
    }
  }

  async startTextExtractionJob(s3Bucket: string, s3Key: string): Promise<string> {
    const command = new StartDocumentTextDetectionCommand({
      DocumentLocation: { S3Object: { Bucket: s3Bucket, Name: s3Key } },
    });

    try {
      const response = await this.client.send(command);
      if (!response.JobId) throw new Error('No JobId returned from AWS Textract.');
      return response.JobId;
    } catch (error: any) {
      logger.error(`Textract startTextExtractionJob error: ${error.message}`, { error });
      throw new AppError(`Failed to start async document text extraction: ${error.message}`, 502);
    }
  }

  async getJobResults(jobId: string): Promise<string> {
    const command = new GetDocumentTextDetectionCommand({ JobId: jobId });

    try {
      const response = await this.client.send(command);
      
      if (response.JobStatus === 'IN_PROGRESS') {
        throw new AppError('Job is still in progress.', 202);
      }
      
      if (response.JobStatus === 'FAILED') {
        throw new AppError('AWS Textract job failed.', 502);
      }

      const lines = (response.Blocks || [])
        .filter(block => block.BlockType === 'LINE')
        .map(block => block.Text || '');

      return lines.join('\n');
    } catch (error: any) {
      if (error instanceof AppError) throw error;
      logger.error(`Textract getJobResults error: ${error.message}`, { error });
      throw new AppError(`Failed to retrieve text extraction results: ${error.message}`, 502);
    }
  }
}

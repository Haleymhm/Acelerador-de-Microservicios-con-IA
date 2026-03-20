import { Request, Response, NextFunction } from 'express';
import { GenerateTextUseCase } from '../../../application/use-cases/GenerateTextUseCase';
import { AnalyzeImageUseCase } from '../../../application/use-cases/AnalyzeImageUseCase';
import { AwsBedrockService } from '../../../infrastructure/aws/services/AwsBedrockService';
import { AwsRekognitionService } from '../../../infrastructure/aws/services/AwsRekognitionService';
import { z } from 'zod';

const generateTextSchema = z.object({
  prompt: z.string().min(1, 'Prompt is required'),
});

// Assuming manual dependency injection here for boilerplate simplicity
const bedrockService = new AwsBedrockService();
const rekognitionService = new AwsRekognitionService();

const generateTextUseCase = new GenerateTextUseCase(bedrockService);
const analyzeImageUseCase = new AnalyzeImageUseCase(rekognitionService);

export class AIController {
  
  static async generateText(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const validatedBody = generateTextSchema.parse(req.body);
      const result = await generateTextUseCase.execute({ prompt: validatedBody.prompt });
      
      res.json({ success: true, data: result });
    } catch (error) {
      next(error);
    }
  }

  static async analyzeImage(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const file = req.file; // From multer
      
      if (!file) {
        res.status(400).json({ success: false, message: 'Image file is required' });
        return;
      }

      const detectFaces = req.body.detectFaces === 'true';

      const result = await analyzeImageUseCase.execute({
        imageBuffer: file.buffer,
        detectFaces
      });

      res.json({ success: true, data: result });
    } catch (error) {
      next(error);
    }
  }
}

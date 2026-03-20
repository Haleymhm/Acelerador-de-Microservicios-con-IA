import { IVisionService, ILabel, IFaceDetail } from '../../domain/ports/IVisionService';

export interface AnalyzeImageDto {
  imageBuffer: Buffer;
  detectFaces?: boolean;
}

export interface AnalyzeImageResult {
  labels: ILabel[];
  faces?: IFaceDetail[];
}

export class AnalyzeImageUseCase {
  constructor(private readonly visionService: IVisionService) {}

  async execute(dto: AnalyzeImageDto): Promise<AnalyzeImageResult> {
    if (!dto.imageBuffer || dto.imageBuffer.length === 0) {
      throw new Error('Image buffer is required and cannot be empty.');
    }

    const labels = await this.visionService.detectLabels(dto.imageBuffer);
    
    let faces: IFaceDetail[] | undefined;
    if (dto.detectFaces) {
      faces = await this.visionService.detectFaces(dto.imageBuffer);
    }

    return {
      labels,
      faces,
    };
  }
}

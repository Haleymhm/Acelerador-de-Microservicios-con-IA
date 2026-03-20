export interface ILabel {
  name: string;
  confidence: number;
}

export interface IFaceDetail {
  confidence: number;
  gender?: string;
  emotions?: Array<{ type: string; confidence: number }>;
}

export interface IVisionService {
  /**
   * Detects labels in a given image buffer.
   * Estimated AWS Cost (Rekognition): $0.001 per image
   */
  detectLabels(imageBuffer: Buffer): Promise<ILabel[]>;

  /**
   * Detects faces and their attributes in a given image buffer.
   * Estimated AWS Cost (Rekognition): $0.001 per image
   */
  detectFaces(imageBuffer: Buffer): Promise<IFaceDetail[]>;
}

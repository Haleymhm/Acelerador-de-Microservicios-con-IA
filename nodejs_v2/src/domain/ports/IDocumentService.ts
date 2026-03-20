export interface IDocumentService {
  /**
   * Extracts text synchronously from an image or PDF buffer.
   * Estimated AWS Cost (Textract): $0.0015 per page
   */
  extractText(documentBuffer: Buffer): Promise<string>;

  /**
   * Starts an asynchronous job to extract text from a multi-page PDF in S3.
   * Returns a JobId.
   */
  startTextExtractionJob(s3Bucket: string, s3Key: string): Promise<string>;

  /**
   * Retrieves the results of an asynchronous text extraction job.
   */
  getJobResults(jobId: string): Promise<string>;
}

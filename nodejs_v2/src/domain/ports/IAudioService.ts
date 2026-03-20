export interface IAudioService {
  /**
   * Synthesizes text to speech natively.
   * Estimated AWS Cost (Polly Neural): $16.00 per 1 million characters
   * @returns Buffer containing the audio (e.g., MP3 stream)
   */
  synthesizeSpeech(text: string, voiceId?: string): Promise<Buffer>;
}

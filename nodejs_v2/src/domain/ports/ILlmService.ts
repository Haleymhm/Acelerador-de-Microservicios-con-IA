export interface IMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface ILlmGenerateOptions {
  modelId?: string;
  temperature?: number;
  maxTokens?: number;
}

export interface ILlmService {
  /**
   * Invokes an LLM model to generate text
   * Estimated AWS Cost: Depends on model (e.g. Claude 3 Haiku: $0.25/1M input, $1.25/1M output)
   */
  generateText(prompt: string, options?: ILlmGenerateOptions): Promise<string>;

  /**
   * Invokes an LLM model with conversational memory
   */
  chat(messages: IMessage[], options?: ILlmGenerateOptions): Promise<string>;
}

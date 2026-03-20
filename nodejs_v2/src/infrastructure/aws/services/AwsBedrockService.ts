import { BedrockRuntimeClient, InvokeModelCommand } from '@aws-sdk/client-bedrock-runtime';
import { ILlmService, ILlmGenerateOptions, IMessage } from '../../../domain/ports/ILlmService';
import { configService } from '../../../shared/config/ConfigService';
import { AppError } from '../../../shared/errors/AppError';
import { logger } from '../../../shared/logger';

export class AwsBedrockService implements ILlmService {
  private client: BedrockRuntimeClient;

  constructor() {
    this.client = new BedrockRuntimeClient({ region: configService.config.AWS_REGION });
  }

  async generateText(prompt: string, options?: ILlmGenerateOptions): Promise<string> {
    const modelId = options?.modelId || 'anthropic.claude-3-haiku-20240307-v1:0';
    
    // Using Claude 3 Messages API format
    const payload = {
      anthropic_version: 'bedrock-2023-05-31',
      max_tokens: options?.maxTokens || 1000,
      temperature: options?.temperature || 0.7,
      messages: [{ role: 'user', content: prompt }]
    };

    const command = new InvokeModelCommand({
      body: JSON.stringify(payload),
      contentType: 'application/json',
      accept: 'application/json',
      modelId,
    });

    try {
      const response = await this.client.send(command);
      const responseBody = JSON.parse(new TextDecoder().decode(response.body));
      return responseBody.content[0].text;
    } catch (error: any) {
      logger.error(`Bedrock generateText error: ${error.message}`, { error });
      throw new AppError(`Failed to generate text using Bedrock: ${error.message}`, 502);
    }
  }

  async chat(messages: IMessage[], options?: ILlmGenerateOptions): Promise<string> {
    const modelId = options?.modelId || 'anthropic.claude-3-haiku-20240307-v1:0';
    
    const payload = {
      anthropic_version: 'bedrock-2023-05-31',
      max_tokens: options?.maxTokens || 1000,
      temperature: options?.temperature || 0.7,
      messages: messages.map(m => ({ role: m.role, content: m.content }))
    };

    const command = new InvokeModelCommand({
      body: JSON.stringify(payload),
      contentType: 'application/json',
      accept: 'application/json',
      modelId,
    });

    try {
      const response = await this.client.send(command);
      const responseBody = JSON.parse(new TextDecoder().decode(response.body));
      return responseBody.content[0].text;
    } catch (error: any) {
      logger.error(`Bedrock chat error: ${error.message}`, { error });
      throw new AppError(`Failed to chat using Bedrock: ${error.message}`, 502);
    }
  }
}

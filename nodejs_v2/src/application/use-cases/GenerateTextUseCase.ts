import { ILlmService } from '../../domain/ports/ILlmService';

export interface GenerateTextDto {
  prompt: string;
}

export class GenerateTextUseCase {
  constructor(private readonly llmService: ILlmService) {}

  async execute(dto: GenerateTextDto): Promise<string> {
    if (!dto.prompt) {
      throw new Error('Prompt is required.');
    }
    
    // Additional business logic could go here before or after calling the LLM
    const result = await this.llmService.generateText(dto.prompt);
    
    return result;
  }
}

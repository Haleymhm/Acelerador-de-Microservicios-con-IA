import { GenerateTextUseCase } from './GenerateTextUseCase';
import { ILlmService } from '../../domain/ports/ILlmService';

describe('GenerateTextUseCase', () => {
  let useCase: GenerateTextUseCase;
  let mockLlmService: jest.Mocked<ILlmService>;

  beforeEach(() => {
    mockLlmService = {
      generateText: jest.fn(),
      chat: jest.fn(),
    };
    useCase = new GenerateTextUseCase(mockLlmService);
  });

  it('should throw an error if prompt is empty', async () => {
    await expect(useCase.execute({ prompt: '' })).rejects.toThrow('Prompt is required.');
  });

  it('should call llmService.generateText and return the result', async () => {
    const mockResponse = 'Hello from AI';
    mockLlmService.generateText.mockResolvedValue(mockResponse);

    const result = await useCase.execute({ prompt: 'Say hello' });

    expect(mockLlmService.generateText).toHaveBeenCalledWith('Say hello');
    expect(result).toBe(mockResponse);
  });
});

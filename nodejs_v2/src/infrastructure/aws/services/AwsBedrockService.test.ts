import { AwsBedrockService } from './AwsBedrockService';
import { BedrockRuntimeClient, InvokeModelCommand } from '@aws-sdk/client-bedrock-runtime';
import { mockClient } from 'aws-sdk-client-mock';

// We must mock configService before AwsBedrockService gets imported
jest.mock('../../../shared/config/ConfigService', () => ({
  configService: {
    config: { AWS_REGION: 'us-east-1' }
  }
}));

jest.mock('../../../shared/logger', () => ({
  logger: { error: jest.fn() }
}));

const bedrockMock = mockClient(BedrockRuntimeClient);

describe('AwsBedrockService', () => {
  let service: AwsBedrockService;

  beforeEach(() => {
    bedrockMock.reset();
    service = new AwsBedrockService();
  });

  it('should successfully generate text using Bedrock SDK', async () => {
    // Mock the SDK response
    const fakeResponseBody = {
      content: [{ text: 'Mocked output from Bedrock' }]
    };

    bedrockMock.on(InvokeModelCommand).resolves({
      body: Buffer.from(JSON.stringify(fakeResponseBody)) as any
    });

    const result = await service.generateText('Tell me a joke');

    expect(result).toBe('Mocked output from Bedrock');
    expect(bedrockMock.calls().length).toBe(1);
  });

  it('should throw AppError if Bedrock request fails', async () => {
    bedrockMock.on(InvokeModelCommand).rejects(new Error('ThrottlingException'));

    await expect(service.generateText('Tell me a joke')).rejects.toThrow(/Failed to generate text/);
  });
});

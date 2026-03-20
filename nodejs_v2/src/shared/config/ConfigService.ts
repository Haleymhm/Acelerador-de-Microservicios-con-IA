import { z } from 'zod';
import dotenv from 'dotenv';

dotenv.config();

const envSchema = z.object({
  PORT: z.string().default('3000').transform(Number),
  NODE_ENV: z.enum(['development', 'production', 'test']).default('development'),
  AWS_REGION: z.string().min(1, "AWS_REGION is required"),
});

export type EnvConfig = z.infer<typeof envSchema>;

class ConfigService {
  private static instance: ConfigService;
  private configData: EnvConfig;

  private constructor() {
    const parsed = envSchema.safeParse(process.env);
    if (!parsed.success) {
      console.error('❌ Invalid environment variables:', parsed.error.format());
      process.exit(1);
    }
    this.configData = parsed.data;
  }

  public static getInstance(): ConfigService {
    if (!ConfigService.instance) {
      ConfigService.instance = new ConfigService();
    }
    return ConfigService.instance;
  }

  public get config(): EnvConfig {
    return this.configData;
  }
}

export const configService = ConfigService.getInstance();

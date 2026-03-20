import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import { configService } from './shared/config/ConfigService';
import { logger } from './shared/logger';
import { errorHandler } from './interfaces/http/middlewares/errorHandler';
import aiRoutes from './interfaces/http/routes/index';

const app = express();

app.use(helmet());
app.use(cors());
app.use(express.json());

// Routes
app.use('/api/v1/ai', aiRoutes);

// Health check
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'UP', timestamp: new Date() });
});

// Error handling must be the last middleware
app.use(errorHandler);

const PORT = configService.config.PORT;

app.listen(PORT, () => {
  logger.info(`🚀 AI Microservices Accelerator is running on http://localhost:${PORT}`);
  logger.info(`Environment: ${configService.config.NODE_ENV}`);
});

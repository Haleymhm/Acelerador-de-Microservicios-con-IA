import { Request, Response, NextFunction } from 'express';
import { AppError } from '../../../shared/errors/AppError';
import { logger } from '../../../shared/logger';

export function errorHandler(
  err: Error,
  req: Request,
  res: Response,
  next: NextFunction
): void {
  if (err instanceof AppError) {
    logger.warn(`Operational Error: ${err.message}`);
    res.status(err.statusCode).json({
      status: 'error',
      message: err.message,
    });
    return;
  }

  // Formatting Validation Errors (Like Zod)
  if (err.name === 'ZodError') {
    res.status(400).json({
      status: 'error',
      message: 'Validation Error',
      details: err,
    });
    return;
  }

  // Unhandled / Programming Errors
  logger.error(`Critical Error: ${err.message}`, { stack: err.stack });
  res.status(500).json({
    status: 'error',
    message: 'Internal Server Error',
  });
}

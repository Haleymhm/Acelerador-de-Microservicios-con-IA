import express, { Request, Response } from 'express';
import cors from 'cors';
import apiRoutes from './api/routes';
import { connectDB } from './config/database';

const startServer = async () => {
  // Conectar a la base de datos
  await connectDB();

  const app = express();
  const port = process.env.PORT || 3000;

  app.use(cors());
  app.use(express.json());

  // API Routes
  app.use('/api', apiRoutes);

  app.get('/', (req: Request, res: Response) => {
    res.send('Hello, World!');
  });

  app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
  });
};

startServer();

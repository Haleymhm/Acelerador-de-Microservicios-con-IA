import request from 'supertest';
import express from 'express';
import { Request, Response } from 'express';

// Creamos una pequeña app de Express para probar,
// en un caso real, importarías tu app principal.
const app = express();
app.get('/', (req: Request, res: Response) => {
  res.send('Hello, World!');
});

describe('GET /', () => {
  it('should return 200 OK with "Hello, World!"', async () => {
    const response = await request(app).get('/');
    expect(response.status).toBe(200);
    expect(response.text).toBe('Hello, World!');
  });
});

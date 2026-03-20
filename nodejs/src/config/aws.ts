import { RekognitionClient } from "@aws-sdk/client-rekognition";
import { ComprehendClient } from "@aws-sdk/client-comprehend";
import { PollyClient } from "@aws-sdk/client-polly";
import { S3Client } from "@aws-sdk/client-s3";

// Configura la región de AWS. Es recomendable usar una variable de entorno.
const region = process.env.AWS_REGION || "us-east-1";

// Crea y exporta los clientes de AWS para que puedan ser reutilizados en la aplicación.
export const s3Client = new S3Client({ region });
export const rekognitionClient = new RekognitionClient({ region });
export const comprehendClient = new ComprehendClient({ region });
export const pollyClient = new PollyClient({ region });

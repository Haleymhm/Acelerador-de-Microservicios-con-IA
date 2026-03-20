import { Sequelize } from "sequelize";
import dotenv from "dotenv";

dotenv.config();

// Se recomienda usar una URL de conexión para entornos de producción.
// Formato: postgres://user:password@host:port/database
const dbUrl = process.env.DATABASE_URL || "postgres://postgres:password@localhost:5432/mydatabase";

if (!process.env.DATABASE_URL) {
  console.warn("DATABASE_URL environment variable not set. Using default local connection.");
}

export const sequelize = new Sequelize(dbUrl, {
  dialect: "postgres",
  logging: false, // Desactiva los logs de SQL en la consola. Actívalo si necesitas depurar.
});

export const connectDB = async () => {
  try {
    await sequelize.authenticate();
    console.log("PostgreSQL connection has been established successfully.");
    // Sincroniza los modelos con la base de datos.
    // 'force: false' evita que se borren las tablas existentes.
    // En desarrollo, podrías usar 'force: true' para recrear las tablas en cada reinicio.
    await sequelize.sync({ force: false }); 
    console.log("All models were synchronized successfully.");
  } catch (error) {
    console.error("Unable to connect to the database:", error);
    process.exit(1); // Detiene la aplicación si no se puede conectar a la BD
  }
};

import { DataTypes, Model } from "sequelize";
import { sequelize } from "../config/database";

// Definición de la interfaz para el modelo Log
interface LogAttributes {
  id?: number;
  service: string;
  requestData: object;
  responseData: object;
}

class Log extends Model<LogAttributes> implements LogAttributes {
  public id!: number;
  public service!: string;
  public requestData!: object;
  public responseData!: object;
}

Log.init(
  {
    id: {
      type: DataTypes.INTEGER,
      autoIncrement: true,
      primaryKey: true,
    },
    service: {
      type: DataTypes.STRING,
      allowNull: false,
    },
    requestData: {
      type: DataTypes.JSONB, // JSONB es más eficiente para búsquedas en PostgreSQL
      allowNull: false,
    },
    responseData: {
      type: DataTypes.JSONB,
      allowNull: false,
    },
  },
  {
    sequelize,
    tableName: "logs",
    timestamps: true, // Añade createdAt y updatedAt
  }
);

export default Log;

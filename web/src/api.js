import axios from "axios";
import { toCamelCase, toSnakeCase } from "@/utils";

const API_BASE_URL = `/api`;

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// 🔥 Функция нормализации путей
function normalizePath(path) {
  if (typeof path !== "string") return path;
  return path.replace(/\\/g, "/"); // Заменяем `\` на `/`
}

// Глобальная функция API-запросов с автоматической обработкой параметров
export async function apiRequest(method, endpoint, params = {}) {
  try {
    const isGetRequest = method.toUpperCase() === "GET";
    let config = { method, url: endpoint };

    // 🔥 Преобразуем все пути в параметрах
    const normalizedParams = JSON.parse(
      JSON.stringify(toSnakeCase(params), (key, value) => normalizePath(value))
    );

    if (isGetRequest) {
      // Конвертируем параметры в snake_case и добавляем в URL
      const queryParams = new URLSearchParams(normalizedParams).toString();
      config.url += queryParams ? `?${queryParams}` : "";
    } else {
      // Для POST, PUT, DELETE передаём данные в body (с нормализацией)
      config.data = normalizedParams;
    }

    const response = await apiClient(config);
    const responseData = toCamelCase(response.data); // Конвертируем обратно

    console.log(`🔹 ${method.toUpperCase()} ${config.url} → Ответ:`, responseData);
    return responseData;
  } catch (error) {
    console.error(`❌ Ошибка запроса ${method.toUpperCase()} ${endpoint}:`, error);
    throw error;
  }
}

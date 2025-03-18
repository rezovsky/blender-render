// Функция: конвертирует объект snake_case → camelCase
export function toCamelCase(obj) {
    if (Array.isArray(obj)) {
      return obj.map((v) => toCamelCase(v));
    } else if (obj !== null && obj.constructor === Object) {
      return Object.keys(obj).reduce((acc, key) => {
        const camelKey = key.replace(/_([a-z])/g, (_, char) => char.toUpperCase());
        acc[camelKey] = toCamelCase(obj[key]);
        return acc;
      }, {});
    }
    return obj;
  }
  
  // Функция: конвертирует объект camelCase → snake_case
  export function toSnakeCase(obj) {
    if (Array.isArray(obj)) {
      return obj.map((v) => toSnakeCase(v));
    } else if (obj !== null && obj.constructor === Object) {
      return Object.keys(obj).reduce((acc, key) => {
        const snakeKey = key.replace(/[A-Z]/g, (char) => `_${char.toLowerCase()}`);
        acc[snakeKey] = toSnakeCase(obj[key]);
        return acc;
      }, {});
    }
    return obj;
  }
  
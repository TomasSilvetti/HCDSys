// Mock de import.meta.env para Jest
const viteEnv = {
  VITE_API_URL: 'http://localhost:8000',
  MODE: 'test',
  DEV: true,
  PROD: false,
  SSR: false
};

// Exportar el objeto como default y también como named export
export default viteEnv;
export { viteEnv };

// Asignar a global.import.meta
if (!global.import) {
  global.import = {};
}

if (!global.import.meta) {
  global.import.meta = {};
}

global.import.meta.env = viteEnv;

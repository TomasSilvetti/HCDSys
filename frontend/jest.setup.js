// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom';

// Mock para import.meta.env
if (!global.import) {
  global.import = {};
}

if (!global.import.meta) {
  global.import.meta = {};
}

global.import.meta.env = {
  VITE_API_URL: 'http://localhost:8000',
  MODE: 'test',
  DEV: true,
  PROD: false,
  SSR: false
};

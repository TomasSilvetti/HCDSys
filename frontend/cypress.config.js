import { defineConfig } from 'cypress';

export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:5173',
    setupNodeEvents(on, config) {
      // Configurar el generador de informes
      require('cypress-mochawesome-reporter/plugin')(on);
      return config;
    },
    reporter: 'cypress-mochawesome-reporter',
    reporterOptions: {
      charts: true,
      reportPageTitle: 'HCDSys - Cypress Test Results',
      embeddedScreenshots: true,
      inlineAssets: true,
      saveAllAttempts: false,
    },
  },
  env: {
    apiUrl: 'http://localhost:8000',
  },
  viewportWidth: 1280,
  viewportHeight: 720,
  video: true,
  videoCompression: 32,
  screenshotOnRunFailure: true,
});

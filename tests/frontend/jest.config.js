const nextJest = require('next/jest');

const createJestConfig = nextJest({
  // Provide the path to your Next.js app to load next.config.js and .env files
  dir: './src/frontend',
});

/** @type {import('jest').Config} */
const config = {
  testEnvironment: 'jsdom',
  rootDir: '../..',
  testMatch: ['<rootDir>/tests/frontend/**/*.test.ts', '<rootDir>/tests/frontend/**/*.test.tsx'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/frontend/src/$1',
  },
  setupFilesAfterEnv: ['<rootDir>/tests/frontend/setup.ts'],
};

module.exports = createJestConfig(config);

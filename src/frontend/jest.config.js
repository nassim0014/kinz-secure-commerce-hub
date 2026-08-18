const nextJest = require('next/jest');

const createJestConfig = nextJest({
  // Provide the path to your Next.js app to load next.config.js and .env files
  dir: './',
});

/** @type {import('jest').Config} */
const config = {
  testEnvironment: 'jsdom',
  rootDir: '../..',
  testMatch: ['<rootDir>/tests/frontend/**/*.test.ts', '<rootDir>/tests/frontend/**/*.test.tsx'],
  // The test files live at <rootDir>/tests/frontend, outside the package that owns
  // their dependencies. Jest resolves node_modules by walking UP from each test file,
  // and src/frontend/node_modules is not an ancestor of tests/frontend — so point the
  // resolver at it explicitly or every import from a devDependency fails to resolve.
  moduleDirectories: ['node_modules', '<rootDir>/src/frontend/node_modules'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/frontend/src/$1',
  },
  setupFilesAfterEnv: ['<rootDir>/tests/frontend/setup.ts'],
};

module.exports = createJestConfig(config);

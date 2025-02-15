module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['@testing-library/jest-dom'],
  moduleNameMapper: {
    '\\.(css|less|scss|sass)$': '<rootDir>/src/mocks/styleMock.js',
  },
  transform: {
    '^.+\\.(js|jsx)$': ['babel-jest', { configFile: './babel.config.cjs' }],
  },
  transformIgnorePatterns: ['/node_modules/(?!axios)/'],
  globals: {
    'import.meta': {
      env: { VITE_API_BASE_URL: 'http://localhost:8000' },
    },
  },
  maxWorkers: '50%',
  bail: false,
  verbose: false,
  cache: true,
  testTimeout: 10000,
};

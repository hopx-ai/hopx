import { defineConfig } from 'vitest/config';

export default defineConfig({
    test: {
        // Run test files sequentially to avoid API rate limits
        // TODO: Enable parallelism when API will handle VMs created with status error
        fileParallelism: false,

        // Optional: Add a delay between test files
        // This gives the API time to recover between test suites
        sequence: {
            hooks: 'stack',
        },

        // Increase timeout for all tests (optional)
        testTimeout: 30000,

        // Show console output
        silent: false,

        // Better error reporting with verbose output
        reporters: ['verbose'],
    },
});

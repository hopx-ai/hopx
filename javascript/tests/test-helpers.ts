/**
 * Helper utilities for tests
 */

/**
 * Add a delay to prevent API rate limiting
 * Use this in beforeAll hooks when running multiple test suites
 */
export async function delayForRateLimit(ms: number = 2000): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Retry a function with exponential backoff
 */
export async function retryWithBackoff<T>(
    fn: () => Promise<T>,
    maxRetries: number = 3,
    initialDelay: number = 1000
): Promise<T> {
    let lastError: Error;

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
            return await fn();
        } catch (error) {
            lastError = error as Error;

            if (attempt < maxRetries) {
                const delay = initialDelay * Math.pow(2, attempt - 1);
                console.log(`⚠️ Attempt ${attempt}/${maxRetries} failed, retrying in ${delay}ms...`);
                await new Promise(resolve => setTimeout(resolve, delay));
            }
        }
    }

    throw lastError!;
}

/**
 * Create a sandbox with retry logic for error states
 * Retries if the VM ends up in an error state after creation
 */
export async function createSandboxWithRetry(
    options: any,
    maxRetries: number = 3,
    initialDelay: number = 2000
): Promise<any> {
    const { Sandbox } = await import('../src/index.js');
    let lastError: Error;

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
            console.log(`🚀 Creating sandbox (attempt ${attempt}/${maxRetries})...`);
            const sandbox = await Sandbox.create(options);

            // Check sandbox status
            const info = await sandbox.getInfo();

            if (info.status === 'error' || info.status === 'failed') {
                console.warn(`⚠️ Sandbox ${sandbox.sandboxId} created in error state: ${info.status}`);

                // Clean up failed sandbox
                try {
                    await sandbox.kill();
                } catch (e) {
                    // Ignore cleanup errors
                }

                if (attempt < maxRetries) {
                    const delay = initialDelay * Math.pow(2, attempt - 1);
                    console.log(`   Retrying in ${delay}ms...`);
                    await new Promise(resolve => setTimeout(resolve, delay));
                    continue;
                }

                throw new Error(`Sandbox creation failed after ${maxRetries} attempts: VM in ${info.status} state`);
            }

            console.log(`✅ Sandbox ${sandbox.sandboxId} created successfully (status: ${info.status})`);
            return sandbox;

        } catch (error) {
            lastError = error as Error;
            console.error(`❌ Attempt ${attempt}/${maxRetries} failed:`, (error as Error).message);

            if (attempt < maxRetries) {
                const delay = initialDelay * Math.pow(2, attempt - 1);
                console.log(`   Retrying in ${delay}ms...`);
                await new Promise(resolve => setTimeout(resolve, delay));
            }
        }
    }

    throw lastError!;
}

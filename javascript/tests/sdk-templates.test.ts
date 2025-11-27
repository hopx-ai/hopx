import { describe, it, expect } from 'vitest';
import { Sandbox } from '../src/index.js';

describe('Sandbox Templates', () => {
    it('should list templates', async () => {
        console.log('📋 Testing listTemplates...');
        const templates = await Sandbox.listTemplates({
            apiKey: process.env['HOPX_API_KEY'],
        });
        expect(Array.isArray(templates)).toBe(true);
        expect(templates.length).toBeGreaterThan(0);
        console.log(`✅ Found ${templates.length} templates`);
    });

    it('should get a specific template', async () => {
        console.log('🔍 Testing getTemplate...');
        // 'code-interpreter' is a standard template
        const templateName = 'code-interpreter';
        const template = await Sandbox.getTemplate(templateName, {
            apiKey: process.env['HOPX_API_KEY'],
        });

        expect(template).toBeDefined();
        expect(template.name).toBe(templateName);
        expect(template.defaultResources).toBeDefined();
        console.log(`✅ Retrieved template: ${template.name}`);
    });

    it('should filter templates by category', async () => {
        console.log('🔍 Testing listTemplates with filter...');
        // Assuming there are categories, let's try to list and pick one
        const allTemplates = await Sandbox.listTemplates({ apiKey: process.env['HOPX_API_KEY'] });
        if (allTemplates.length > 0 && allTemplates[0].category) {
            const category = allTemplates[0].category;
            const filtered = await Sandbox.listTemplates({
                category,
                apiKey: process.env['HOPX_API_KEY'],
            });
            expect(filtered.length).toBeGreaterThan(0);
            expect(filtered[0].category).toBe(category);
            console.log(`✅ Filtered by category: ${category}`);
        } else {
            console.log('⚠️ No categories found to test filtering');
        }
    });
});

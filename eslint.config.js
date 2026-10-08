import eslint from '@eslint/js';
import prettier from 'eslint-config-prettier';
import tsParser from '@typescript-eslint/parser';
import tsPlugin from '@typescript-eslint/eslint-plugin';
import globals from 'globals';

export default [
  { ignores: ['dist/**', '.astro/**', 'node_modules/**', 'coverage/**'] },
  eslint.configs.recommended,
  { languageOptions: { globals: { ...globals.browser, ...globals.node, ...globals.es2021 } } },
  {
    files: ['**/*.{ts,tsx}'],
    languageOptions: {
      parser: tsParser,
      parserOptions: { sourceType: 'module', ecmaFeatures: { jsx: true } },
    },
    plugins: { '@typescript-eslint': tsPlugin },
    rules: { ...tsPlugin.configs.recommended.rules, '@typescript-eslint/no-explicit-any': 'error' },
  },
  prettier,
];

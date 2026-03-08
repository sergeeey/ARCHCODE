module.exports = {
  root: true,
  parser: "@typescript-eslint/parser",
  parserOptions: {
    ecmaVersion: "latest",
    sourceType: "module",
    ecmaFeatures: { jsx: true },
  },
  env: {
    browser: true,
    node: true,
    es2021: true,
  },
  ignorePatterns: [
    "node_modules/",
    "dist/",
    "results/",
    "data/",
    "manuscript/",
    "external/",
  ],
  rules: {},
};

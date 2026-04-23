import js from "@eslint/js";
import globals from "globals";

export default [
  js.configs.recommended,
  {
    files: ["**/*.js"],
    languageOptions: {
      globals: {
        ...globals.node,
      },
      ecmaVersion: 2021,
      sourceType: "script",
    },
    rules: {
      "no-unused-vars": "warn", // or "error" if you want it to fail CI
    },
  },
];

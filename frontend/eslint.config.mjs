import js from "@eslint/js";
import globals from "globals";
import { defineConfig } from "eslint/config";

export default defineConfig([
  {
    files: ["**/*.{js,mjs,cjs}"],
    plugins: { js },
    extends: ["js/recommended"],
    languageOptions: {
      globals: globals.node, // <-- key fix
    },
    rules: {
      "no-unused-vars": "warn", // so `err` doesn't fail CI, OR set to "error" and use err
    },
  },
]);

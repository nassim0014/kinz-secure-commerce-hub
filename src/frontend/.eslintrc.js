// ESLint config for the Next.js dashboard.
//
// This file previously contained `{ output: 'standalone' }` — a next.config.js
// option pasted into the wrong file, which made `next lint` reject the whole
// config with "Unexpected top-level property 'output'". That option is already
// correctly set in next.config.js and is not an ESLint setting.
const config = {
  root: true,
  extends: ['next/core-web-vitals'],
};
module.exports = config;

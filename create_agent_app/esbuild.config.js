const esbuild = require('esbuild');

const buildOptions = {
  entryPoints: ['index.ts'],
  bundle: true,
  platform: 'node',
  target: 'node16',
  sourcemap: true,
  external: ['fs', 'path'], // Node.js built-ins
};

// Build both formats
Promise.all([
  // CommonJS build
  esbuild.build({
    ...buildOptions,
    format: 'cjs',
    outfile: 'dist/index.js',
  }),
  // ESM build
  esbuild.build({
    ...buildOptions,
    format: 'esm',
    outfile: 'dist/index.esm.js',
  }),
]).catch(() => process.exit(1));
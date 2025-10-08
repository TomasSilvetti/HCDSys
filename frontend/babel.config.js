export default {
  presets: [
    ['@babel/preset-env', { targets: { node: 'current' } }],
    ['@babel/preset-react', { runtime: 'automatic' }]
  ],
  plugins: [
    ['module-resolver', {
      root: ['./src'],
      alias: {
        '@': './src',
      }
    }]
  ]
};

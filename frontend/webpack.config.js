const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');

module.exports = (env, argv) => {
  const isDevelopment = argv.mode === 'development';

  return {
    entry: './src/index.tsx',
    output: {
      path: path.resolve(__dirname, 'dist'),  // Ensure this matches Docker COPY path
      filename: 'bundle.js',
      publicPath: '/' // Prevents issues with React routes in production
    },
    resolve: {
      extensions: ['.tsx', '.ts', '.js']
    },
    module: {
      rules: [
        {
          test: /\.tsx?$/,
          use: 'ts-loader',
          exclude: /node_modules/
        },
        {
          test: /\.css$/,
          use: ['style-loader', 'css-loader']
        }
      ]
    },
    plugins: [
      new CleanWebpackPlugin(),
      new HtmlWebpackPlugin({
        template: 'public/index.html',
        filename: 'index.html'
      })
    ],
    devServer: isDevelopment
      ? {
          static: './dist',
          port: 3000,
          hot: true
        }
      : undefined,
    mode: isDevelopment ? 'development' : 'production',
    performance: {
      hints: false, // Disable performance hints; enable later after PoC done.
    },
  };
};

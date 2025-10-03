const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');
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
        },
        {
          test: /\.(png|jpg|jpeg|gif|svg)$/,
          use: [
            {
              loader: 'file-loader',
              options: {
                name: 'assets/[name].[hash].[ext]',
              },
            },
          ],
        },
      ]
    },
    plugins: [
      new CleanWebpackPlugin(),
      new HtmlWebpackPlugin({
        template: 'public/index.html',
        filename: 'index.html'
      }),
      new CopyWebpackPlugin({
        patterns: [
          { from: 'lib/assets', to: 'assets' } // Copy assets from lib/assets to dist/assets
        ],
      }),
    ],
    devServer: isDevelopment
      ? {
          static: './dist',
          port: 3000,
          host: '0.0.0.0', // Allow external connections (for Docker)
          hot: true,
          liveReload: true,
          watchFiles: ['src/**/*', 'lib/**/*'], // Watch for changes
          historyApiFallback: true, // Support React Router
          client: {
            overlay: {
              errors: true,
              warnings: false,
            },
          },
        }
      : undefined,
    mode: isDevelopment ? 'development' : 'production',
    performance: {
      hints: false, // Disable performance hints; enable later after PoC done.
    },
  };
};

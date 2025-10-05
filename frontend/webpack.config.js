const path = require('path');
const webpack = require('webpack');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');


module.exports = (env, argv) => {
  const isDevelopment = argv.mode === 'development';
  const isAnalyze = env && env.analyze;

  return {
    entry: './src/index.tsx',
    output: {
      path: path.resolve(__dirname, 'dist'),
      filename: isDevelopment ? 'bundle.js' : '[name].[contenthash].js',
      chunkFilename: isDevelopment ? '[name].chunk.js' : '[name].[contenthash].chunk.js',
      publicPath: '/',
      clean: true
    },
    resolve: {
      extensions: ['.tsx', '.ts', '.js'],
      alias: {
        '@': path.resolve(__dirname, 'src')
      }
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
          type: 'asset/resource',
          generator: {
            filename: 'assets/[name].[hash][ext]'
          }
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
          { from: 'lib/assets', to: 'assets', noErrorOnMissing: true }
        ],
      }),
      new webpack.DefinePlugin({
        'process.env.REACT_APP_API_URL': JSON.stringify(process.env.REACT_APP_API_URL || 'http://localhost:8080'),
        'process.env.REACT_APP_WHISPER_URL': JSON.stringify(process.env.REACT_APP_WHISPER_URL || 'http://localhost:8000'),
        'process.env.NODE_ENV': JSON.stringify(isDevelopment ? 'development' : 'production')
      }),
      ...(isAnalyze ? [new BundleAnalyzerPlugin()] : [])
    ],
    optimization: isDevelopment ? {} : {
      splitChunks: {
        chunks: 'all',
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            priority: 10
          },
          react: {
            test: /[\\/]node_modules[\\/](react|react-dom)[\\/]/,
            name: 'react',
            priority: 20
          },
          query: {
            test: /[\\/]node_modules[\\/]@tanstack[\\/]/,
            name: 'query',
            priority: 15
          }
        }
      }
    },
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
    devtool: isDevelopment ? 'eval-source-map' : 'source-map',
    performance: {
      hints: isDevelopment ? false : 'warning',
      maxEntrypointSize: 512000,
      maxAssetSize: 512000
    },
  };
};

// config.js
import { isDev } from './env.js';

// 开发环境下使用 Vite 代理，这里的 /api 要和 Vite 代理配置的前缀一致
const devBaseURL = '/api';
// 生产环境下使用真实的后端接口地址，需要替换为实际地址
const prodBaseURL = '/api';

// 根据环境变量 isDev 来决定使用哪个 baseURL
export const apiBaseURL = isDev ? devBaseURL : prodBaseURL;
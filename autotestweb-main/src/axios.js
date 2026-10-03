import axios from "axios";
import { useCookies } from "@vueuse/integrations/useCookies";
import { apiBaseURL } from '../config.js';

// 创建 axios 实例，并根据环境变量设置 baseURL
const service = axios.create({
    baseURL: apiBaseURL
});
// const service = axios.create({
//     // baseURL: "http://127.0.0.1:5000"
//     // baseURL: "/proxy"
//     // baseURL: ""
//     baseURL: "/api" // 与Vite代理前缀一致



// });
// 获取 cookie
const cookie = useCookies();
let router;
// 设置路由实例
export const setRouter = (r) => {
    router = r;
};
// 设置请求拦截器
service.interceptors.request.use(config => {
    console.log("进入了请求拦截器")
    // 从 cookie 中获取 token
    const token = cookie.get('l-token');
    if (token) {
        // 在请求头中添加 token
        config.headers['Authorization'] = `Bearer ${token}`;
    }
    // 携带 access_user_id
    const access_user_id = cookie.get('l-access_user_id');
    console.log("access_user_id",access_user_id)
    if (access_user_id) {
        config.headers['access-user-id'] = access_user_id; // 直接传递用户名
    }
    return config;
}, error => {
    // 处理请求错误
    console.error('请求拦截器出错:', error);
    return Promise.reject(error);
});
// 设置响应拦截器
service.interceptors.response.use(
    response => {
        // 正常响应直接返回
        return response;
    },
    error => {
        if (error.response) {
            const { status } = error.response;
            if (status === 401) {
                console.log("进入了响应拦截器")
                // 清除 cookie 中的 token
                cookie.remove('l-token');
                cookie.remove('l-access_user_id'); // 同时清除唯一id
                // 跳转到登录页
                router.push('/login');
            }
        }
        return Promise.reject(error);
    }
);

export default service;
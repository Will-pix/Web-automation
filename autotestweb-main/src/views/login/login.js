import axios from "~/axios";

export function login(username,password){
    return axios.post("/login",{
        username,
        password
    })
}

export function getFeishuConfig() {
    return axios.get("/feishu/config");
}

export function doFeishuLogin(code) {
    return axios.post("/feishu/login", { code });
}

export function getLoginConfig() {
    return axios.get("/login/config");
}

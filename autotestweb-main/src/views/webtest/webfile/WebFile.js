import axios from "~/axios";

// 模块名
const module_name = "WebFile"

// 分页查询
export function queryByPage(data){
    return axios.post(`/${module_name}/queryByPage`, data)
}

// 单个数据查询
export function queryById(id){
    return axios.get(`/${module_name}/queryById?id=${id}`)
}

// 新增数据
export function insertData(data){
    return axios.post(`/${module_name}/insert`,data)
}

// 修改数据
export function uptateData(data){
    return axios.put(`/${module_name}/update`,data)
}

// 删除数据
export function deleteData(id){
    return axios.delete(`/${module_name}/delete?id=${id}`)
}

// 上传
export function upload(file){
    return axios.post(`/${module_name}/upload`,file)
}

// 正则匹配
export function get_regular_expression(file_name){
    return axios.post(`/${module_name}/get_regular_expression`,file_name)
}
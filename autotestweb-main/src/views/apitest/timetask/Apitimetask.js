import axios from "~/axios";

// 模块名
const module_name = "ApiTimeTask"

// 查询所有数据
export function queryByPage(data) {
    return axios.post(`/${module_name}/queryByPage`, data)
}

// 新增数据
export function insertData(data){
    return axios.post(`/${module_name}/insert`,data)
}

// 单个数据查询
export function queryById(id){
    return axios.get(`/${module_name}/queryById?id=${id}`)
}

// 修改数据
export function uptateData(data){
    return axios.put(`/${module_name}/update`,data)
}
// 删除数据
export function deleteData(id){
    return axios.delete(`/${module_name}/delete?id=${id}`)
}
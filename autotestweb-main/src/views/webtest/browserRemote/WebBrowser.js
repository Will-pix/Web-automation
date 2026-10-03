import axios from "~/axios";

// 模块名
const module_name = "WebBrowser"

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

export function testBrowserConnection(id){
    return axios.post(`/${module_name}/testConnection`, { id })
}

// 查询项目列表
// export function queryAll(){
//     return axios.get(`/${module_name}/queryAll`)
// }


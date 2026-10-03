import axios from "~/axios";

// 模块名
const module_name = "QualityDashboard"

// 分页查询
export function queryByPage(data){
    return axios.post(`/${module_name}/getQualityData`, data)
}

// 明细查询
export function queryByDetail(data){
    return axios.post(`/${module_name}/getQualityDetail`, data)
}

// AI分析
export function getQualityAIData(data){
    return axios.post(`/${module_name}/getQualityAIData`, data)
}
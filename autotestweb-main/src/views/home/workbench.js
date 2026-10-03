import axios from "~/axios"

const module_name = "Workbench"

export function getExecutionRecords(data) {
    return axios.post(`/${module_name}/getExecutionRecords`, {
        page: data.page,
        pageSize: data.pageSize,
        trigger_type: data.trigger_type || ""
    })
}

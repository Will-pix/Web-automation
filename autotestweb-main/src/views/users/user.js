import axios from "~/axios";

// export function getUserBypage(page){
//     return axios.get(`/user/queryByPage?page=${page}&limit=10`)
// }

// 请求全部数据
export function getUserBypage(page){
    const data = {
        page:page,
        pageSize:100
    }
    return axios.post('/user/queryByPage',data)
}

export function addUser(username,password,role = "user"){    
    return axios.post("/user/insert",{
        username,
        password,
        role
    })
}

export function editUser(id,username,password,role = "user"){
    return axios.put("/user/update",{
        id,
        username,
        password,
        role
    })
}

export function delUser(id){
    return axios.delete(`/user/delete?id=${id}`)
}

// 新增：获取所有人ID（用于下拉框）
export function queryAllCreateBy(){
    return axios.get(`/user/queryAllCreateBy`)
}

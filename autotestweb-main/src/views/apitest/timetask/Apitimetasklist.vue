<template>
<!-- 查询新建 -->
    <!-- inline代表form的元素行级显示 -->
    <el-form ref="searchFormRef" :model="searchForm" :inline="true">
        <el-form-item label="任务名称">
            <el-input v-model="searchForm.task_name" placeholder="输入任务名称"></el-input>
        </el-form-item>
        <el-form-item label="所属项目" style="width: 200px;">
            <el-select v-model="searchForm.project_id" placeholder="集合所属项目" clearable @change="projectChange">
                <el-option v-for="project in projectlist" :key="project.id" :label="project.project_name" :value="project.id"></el-option>
            </el-select>
        </el-form-item>
        <el-form-item label="所属集合"  style="width: 200px;">
            <el-select v-model="searchForm.collection_id" placeholder="项目筛选集合" clearable multiple>
                <el-option v-for="collection in collectionlist" :key="collection.id" :label="collection.collection_name" :value="collection.id"></el-option>
            </el-select>
        </el-form-item>
        <el-row class="mb-4" type="flex" justify="end">
            <el-button type="primary" @click="loadData(-1)">查询</el-button>
            <el-button type="warning" @click="onDataForm()">新增任务</el-button>
        </el-row>
    </el-form>
    <!-- 数据表格 -->
     <el-table :data="tableData">
        <el-table-column v-for="task in tasklist" :prop="task.prop" :label="task.label" :key="task.prop"></el-table-column>
        <!-- 操作 -->
         <el-table-column fixed="right" label="操作">
            <template #default="scope">
                <el-button link type="primary" size="small"  @click.prevent="onedit(scope.$index)">编辑</el-button>
                <el-button link type="primary" size="small"  @click.prevent="showApiHistoryDialog(scope.$index)">执行记录</el-button>
                <el-popconfirm title="是否删除" confirm-button-text="确认" cancel-button-text="取消" @confirm="onDelete(scope.$index)">
                        <template #reference="scope">
                            <el-button link type="primary" size="small">删除</el-button>
                        </template>
                    </el-popconfirm>
                <!-- <el-button link type="primary" size="small"  @click.prevent="deltime(scope.$index)">删除</el-button> -->
            </template>
         </el-table-column>
     </el-table>
             
     <div>
        <!-- 分页 total总数，currentPage页码，pageSize每页展示数量 handleSizeChange切换每页展示数量，handleCurrentChange切换页码-->
        <el-pagination v-model:current-page="pagination.currentPage" v-model:page-size="pagination.limit" :page-sizes="[10, 20, 30, 50]"
            layout="total, sizes, prev, pager, next, jumper" :total="pagination.total" @size-change="handleSizeChange"
            @current-change="handleCurrentChange" />
    </div>
    <!-- 新建/编辑弹窗 -->
    <el-dialog v-model="create_edit" title="定时任务">
        <el-form :model="taskForm" :rules="rules" ref="formRef">
            <el-form-item label="任务名称" label-width="130px" prop="task_name">
                <el-input placeholder="输入任务名称"  v-model="taskForm.task_name"></el-input>
            </el-form-item>
            <el-form-item label="选择任务类型" label-width="130px" prop="task_type">
                <el-select  v-model="taskForm.task_type">
                    <el-option label="间隔任务" value="interval_task"></el-option>
                    <el-option label="定时任务" value="fixed_task"></el-option>
                </el-select>
            </el-form-item>
            <el-form-item label="间隔-执行时间" v-if="taskForm.task_type === 'interval_task'" label-width="130px" prop="interval_time">
                <el-input placeholder="小时为单位,输入整数如：1" v-model="taskForm.interval_time"></el-input>
            </el-form-item>
            <el-form-item label="定时-执行时间" v-if="taskForm.task_type === 'fixed_task'" label-width="130px" prop="fixed_time">
                <el-input placeholder="每天几点执行,如：18：02（英文：）" v-model="taskForm.fixed_time"></el-input>
            </el-form-item>
            <el-form-item label="测试集所属项目" label-width="130px" prop="project_id">
                <el-select  clearable @change="innerProjectChange" v-model="taskForm.project_id" :disabled="isEditDisabled">
                    <el-option v-for="project in innerProjectList" :key="project.id" :label="project.project_name" :value="project.id"></el-option>
                </el-select>
            </el-form-item>
            <el-form-item label="需要执行测试集" label-width="130px" prop="collection_id">
            <el-select placeholder="项目筛选集合" clearable v-model="taskForm.collection_id" @change="handleCollectionChange" :disabled="isEditDisabled">
                <el-option v-for="collection in innerCollectionList" :key="collection.id" :label="collection.collection_name" :value="collection.id"></el-option>
            </el-select>
            </el-form-item>
            <el-row type="flex" justify="end">
                <el-button type="primary" @click="saveTask">保存</el-button>
                <el-button @click="closetask">取消</el-button>
            </el-row>
        </el-form>
    </el-dialog>
        <!-- 报告弹窗 -->
    <el-dialog v-model="apiHistoryDialogFormVisible" title="执行记录">
        <el-form-item>
            <el-table :data="apiHistoryList" style="width: 100%;">
                <el-table-column prop="id" label="报告编号" min-width="20%" show-overflow-tooltip="true"></el-table-column>
            <el-table-column prop="history_desc" label="执行情况简述" min-width="30%" show-overflow-tooltip="true"></el-table-column>
            <el-table-column prop="create_time" label="执行时间" min-width="30%" show-overflow-tooltip="true"></el-table-column>
            <el-table-column fixed="right" label="操作" min-width="20%">
                <template #default="scope">
                    <el-button type="primary" size="small" @click.prevent="showApiHistory(scope.$index)">
                        查看报告
                    </el-button>
                </template>
            </el-table-column>
            </el-table>
        </el-form-item>
        <el-form-item>
            <el-pagination :current-page="currentApiHistoryPage" :page-size="apiHistoryPageSize" :total="apiHistoryTotal"
                @current-change="handleApiHistoryCurrentChange"></el-pagination>
        </el-form-item>
    </el-dialog>
</template>
<script setup>
import {ref,reactive, watch} from "vue"
import { queryAll as projectqueryall } from "../project/ApiProject.js"
import {queryByPage as collectionqueryall} from '~/views/apitest/collection/ApiCollection.js'
import { ElMessage } from "element-plus";
// ===============以下为筛选
// 搜索的双向绑定数据
const searchForm = reactive({
    "task_name":"",
    "project_id":"",
    "collection_id":[]
})
// 项目的列表值
const projectlist = ref([])
// 项目的获取
const getprojectlist = () =>{
    projectqueryall().then((res)=>{
        console.log("项目的列表值为:",res.data.data)
        projectlist.value= res.data.data
    })
}
getprojectlist()
// 触发集合查询
const projectChange = () =>{
    // 先清空集合列表
    searchForm.collection_id = []
    // 复用-清理弹窗表单
    // taskForm.collection_id = ''
    getcollectionlist()
}
// 集合的列表值
const collectionlist = ref([])
// 新增一个映射对象-集合列表
const collectionIdToNameMap = ref({});
// 集合的获取
const getcollectionlist = () =>{
    collectionqueryall({
        "page":1,
        "pageSize":9999999,
        "project_id":searchForm.project_id
    }).then((res)=>{
        console.log("集合的列表值为:",res.data.data)
        collectionlist.value = res.data.data
        // 构建映射对象
        const map = {};
        res.data.data.forEach((collection) => {
            map[collection.id] = collection.collection_name;
        });
        collectionIdToNameMap.value = map;
        console.log("collectionIdToNameMap",collectionIdToNameMap.value)
    })
}
// 新增任务
const onDataForm = () =>{
    create_edit.value = true
    taskForm.id = 0,
    taskForm.task_name='',
    taskForm.task_type='',
    taskForm.interval_time='',
    taskForm.fixed_time='',
    taskForm.project_id='',
    taskForm.collection_id='',
    taskForm.collection_name=''
    getInnerProjectList()
    isEditDisabled.value = false;

}
// ===============以上为筛选
// ===============以下为表格
// 表格数据
const tableData = ref([])
// 表格列
const tasklist = ref([
    {prop:"id",label:"任务id"},
    {prop:"task_name",label:"任务名称"},
    {prop:"task_type",label:"执行类型"},
    {prop:"collection_id",label:"测试集id"},
    {prop:"collection_name",label:"测试集名称"},
    {prop:"last_time",label:"最近执行时间"},
    {prop:"is_state",label:"最近执行状态"},
    {prop:"task_num",label:"执行总次数"},
    {prop:"create_time",label:"创建时间"},
])
// 定义 is_state 布尔值到文字的映射
const isStateMap = {
  true: "通过",
  false: "未通过"
};
// 定义 task_type 英文状态到中文的映射
const taskTypeMap = {
  "interval_task": "间隔任务",
  "fixed_task":"定时任务"
  // 可以添加更多英文状态及其对应的中文翻译
};
// 分页参数
const pagination = ref({
    total: 0,
    limit: 10,
    currentPage: 1
  })
// 页码变更
const handleCurrentChange =(val)=>{
    pagination.value.currentPage = val
    loadDate()
}
// 分页数据大小变更
const handleSizeChange =(val)=>{
    pagination.value.limit = val
    loadData()
}
import {queryByPage,insertData,queryById,uptateData,deleteData} from '~/views/apitest/timetask/Apitimetask.js'
// 获取所有数据
const loadData = () =>{
    let searchdata = searchForm
    searchdata["page"] = pagination.value.currentPage //这是页码
    searchdata["pageSize"] = pagination.value.limit  //这是每页多少条数据
    // 传出的数据为
    console.log("传出的数据为",searchdata)
    // 请求
    getcollectionlist()
    queryByPage(searchdata).then((res)=>{
        console.log("获取的数据为",res.data.data)
        // 直接对后端返回的数据进行处理并赋值给 tableData
        tableData.value = res.data.data.map((task) => ({
        ...task,
        is_state: isStateMap[task.is_state],
        task_type: taskTypeMap[task.task_type],
        collection_name: collectionIdToNameMap.value[task.collection_id] || ''
    }));
        console.log("此时的tableData等于",tableData.value)
        // 更新分页的总数据量
        pagination.value.total = res.data.total; 
})}
loadData()
// ==============以下为弹窗
// 弹窗内项目的列表值
const innerProjectList = ref([]);
// 弹窗内项目的获取
const getInnerProjectList = () => {
    projectqueryall().then((res) => {
        console.log("弹窗内项目的列表值为:", res.data.data);
        innerProjectList.value = res.data.data;
    });
};
// 弹窗内集合的列表值
const innerCollectionList = ref([]);
// 弹窗内集合的获取
const getInnerCollectionList = () => {
    collectionqueryall({
        "page": 1,
        "pageSize": 9999999,
        "project_id": taskForm.project_id
    }).then((res) => {
        console.log("弹窗内集合的列表值为:", res.data.data);
        innerCollectionList.value = res.data.data;
    });
};
// 弹窗内项目切换
const innerProjectChange = () => {
    // 先清空弹窗内集合列表
    taskForm.collection_id = '';
    getInnerCollectionList();
};
// 弹窗状态
const create_edit = ref(false)
// 弹窗数据
const taskForm = reactive({
    id:0,
    task_name:'',
    task_type:'',
    interval_time:'',
    fixed_time:'',
    project_id:'',
    collection_id:'',
    // collection_name:''
})
// 表单的引用
const formRef = ref(null)
// 效验
const rules = reactive({
    task_name: [{ required: true, message: '请输入任务名称', trigger: 'blur' }], 
    task_type: [{ required: true, message: '请选择任务类型', trigger: 'change' }],
    interval_time: [{
      validator: (rule, value, callback) => {
        if (taskForm.task_type === 'interval_task' && !value) {
          callback(new Error('请输入间隔时间'));
        } else {
          callback();
        }
      },
      trigger: 'blur'
    }],
    fixed_time: [    {
      validator: (rule, value, callback) => {
        if (taskForm.task_type === 'fixed_task' && !value) {
          callback(new Error('请输入定时时间'));
        } else {
          callback();
        }
      },
      trigger: 'blur'
    }],
    project_id: [{ required: true, message: '请选择项目', trigger: 'change' }],
    collection_id: [{ required: true, message: '请选择集合', trigger: 'change' }]

})
// 保存任务
const saveTask = () =>{
    // 通过表单实例获取验证
    formRef.value.validate((vaild)=>{
        if(vaild){
            if(taskForm.id>0){
                uptateData(taskForm).then((res)=>{
                    ElMessage.success("修改成功");
                        closetask()
                        loadData()
                }).catch((err)=>{
                    ElMessage.error("修改失败");
                    console.log("新增表单数据失败:", err);
                })
                console.log("修改表单数据:", taskForm);
            }else{
                insertData(taskForm).then((res)=>{
                    if(res.data.code != -1){
                        ElMessage.success("新增成功");
                        closetask()
                        loadData()
                    }else{
                        ElMessage.error("新增失败");
                    }
                }).catch((err)=>{
                    ElMessage.error("新增失败");
                    console.log("新增表单数据失败:", err);
                })
                console.log("新增表单数据:", taskForm);
            }
        }else{
            console.log("表单校验不通过");
        }
    })
}
// 关闭弹窗
const closetask = () =>{
    taskForm.id = 0,
    taskForm.task_name='',
    taskForm.task_type='',
    taskForm.interval_time='',
    taskForm.fixed_time='',
    taskForm.project_id='',
    taskForm.collection_id='',
    // taskForm.collection_name=''
    create_edit.value = false
}
// ==========编辑
const onedit = (index) =>{
    console.log("要发送的index为",index)
    // 通过index获取请求id
    let id = tableData.value[index]["id"]
    console.log("id是",id)
    // 获取单条数据
    queryById(id).then((res)=>{
       // 回显数据并打开弹窗
       const data = res.data.data;
        taskForm.id = data.id;
        taskForm.task_name = data.task_name;
        taskForm.task_type = data.task_type;
        taskForm.interval_time = data.interval_time;
        taskForm.fixed_time = data.fixed_time;
        taskForm.project_id = data.project_id;
        taskForm.collection_id = data.collection_id;
        // taskForm.collection_name = data.collection_name;
        create_edit.value = true; // 打开弹窗
        getInnerProjectList()
        getInnerCollectionList()
        console.log("此时的taskForm值为", taskForm);
    })
}
// 删除操作
const onDelete= (index)=>{
 // 调用删除函数
    console.log(tableData.value[index]["id"])
    deleteData(tableData.value[index]["id"]).then((res)=>{
        ElMessage.success("删除成功");
        loadData()
    })
}
// 控制是否禁用编辑的标志
const isEditDisabled = ref(false);
// 监听 taskForm.id 的变化
watch(() => taskForm.id, (newValue) => {
    console.log("监听的数据为",taskForm.id)
  if (newValue > 0) {
    isEditDisabled.value = true;
  }
});
// =========报告弹窗
import {queryByPage as queryApiHistoryByPage} from '~/views/apitest/collection/ApiHistory.js'
// 执行记录弹窗的状态
const apiHistoryDialogFormVisible = ref(false)
// 当前展示的执行记录关联的 collectionId-临时存储
const currentCollectionId = ref(0) 
// 报告事件-执行记录
const showApiHistoryDialog = (index)=>{
    // 打开弹窗
    apiHistoryDialogFormVisible.value=true
    // 清空弹窗的全部信息
    apiHistoryTotal.value = 0
    apiHistoryPageSize.value = 10
    currentApiHistoryPage.value = 1
    apiHistoryList.value = []
    // 通过传入的index，获取表单的测试集id
    currentCollectionId.value = tableData.value[index]["collection_id"]
    // 并且发送请求获取该集合id下的所有报告信息
    loadApiHistorys()
}
// 获取集合下的所有报告信息
const loadApiHistorys = () =>{
    let searchData = {}
    searchData["collection_id"] = currentCollectionId.value
    searchData["page"] = currentApiHistoryPage.value
    searchData["pageSize"] = apiHistoryPageSize.value
    queryApiHistoryByPage(searchData).then((res)=>{
        apiHistoryList.value = res.data.data
        apiHistoryTotal.value = res.data.total
        console.log("此时的apiHistoryList为:",apiHistoryList.value)
    })
}
// 分页数据
const currentApiHistoryPage = ref(1) // 页码
const apiHistoryPageSize = ref(10) // 每页大小
const apiHistoryTotal = ref(0) //总数
// 翻页
const handleApiHistoryCurrentChange = (val) => {
    currentApiHistoryPage.value = val
    loadApiHistorys()
}
// 单独打开某个报告的详情
const showApiHistory = (index) =>{
    // 注意： 这个地方的测试报告服务器地址，是需要根据后端服务器修改的，这里写死了，后面要改成配置文件
    var report_id = apiHistoryList.value[index]["history_detail"]
    window.open("http://127.0.0.1:5000/ApiHistory/"+report_id+"/index.html", '_blank');

}
// 弹窗的数据
const apiHistoryList = ref([])


</script>
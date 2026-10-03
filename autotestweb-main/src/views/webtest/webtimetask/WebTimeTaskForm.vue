<template>
        <!-- 新建/编辑弹窗 -->
        <el-dialog v-model="props.create_edit" title="定时任务" @close="handleClose">
        <el-form :model="taskForm" :rules="rules" ref="editFormRef">
            <el-form-item label="任务名称" label-width="130px" prop="task_name">
                <el-input placeholder="输入任务名称"  v-model="taskForm.task_name"></el-input>
            </el-form-item>
            <el-form-item label="选择任务类型" label-width="130px" prop="task_type">
                <el-select  v-model="taskForm.task_type">
                    <el-option label="间隔任务" value="interval_task"></el-option>
                    <el-option label="定时任务" value="fixed_task"></el-option>
                    <el-option label="cron自定义时间" value="cron_task"></el-option>
                </el-select>
            </el-form-item>
            <el-form-item label="间隔-执行时间" v-if="taskForm.task_type === 'interval_task'" label-width="130px" prop="interval_time">
                <el-input placeholder="小时为单位,输入整数如：1" v-model="taskForm.interval_time"></el-input>
            </el-form-item>
            <el-form-item label="定时-执行时间" v-if="taskForm.task_type === 'fixed_task'" label-width="130px" prop="fixed_time">
                <el-input placeholder="每天几点执行,如：18：02（英文：）" v-model="taskForm.fixed_time"></el-input>
            </el-form-item>
            <el-form-item label="cron-执行时间" v-if="taskForm.task_type === 'cron_task'" label-width="130px" prop="cron_time">
                <el-input placeholder="按照Unix crontab 5字段格式" v-model="taskForm.cron_time"></el-input>
            </el-form-item>
            <el-form-item label="测试集所属项目" label-width="130px" prop="project_id">
                <el-select  clearable @change="innerProjectChange" v-model="taskForm.project_id" :disabled="isEditDisabled">
                    <el-option v-for="project in innerProjectList" :key="project.id" :label="project.project_name" :value="project.id"></el-option>
                </el-select>
            </el-form-item>

            <!-- 新增：执行环境筛选框（必选、项目下方） -->
            <el-form-item label="测试集所属环境" label-width="130px" prop="collection_env_type">
                <el-select 
                clearable 
                @change="innerEnvChange" 
                v-model="taskForm.collection_env_type" 
                :disabled="isEditDisabled"
                placeholder="选择执行环境"
                >
                <el-option 
                    v-for="item in envTypeOptions" 
                    :key="item.value" 
                    :label="item.label" 
                    :value="item.value"
                ></el-option>
                </el-select>
            </el-form-item>

            <el-form-item label="需要执行测试集" label-width="130px" prop="collection_id">
            <el-select placeholder="项目筛选集合" clearable v-model="taskForm.collection_id" @change="handleCollectionChange" :disabled="isEditDisabled">
                <el-option v-for="collection in innerCollectionList" :key="collection.id" :label="collection.collection_name" :value="collection.id"></el-option>
            </el-select>
            </el-form-item>
            <el-row type="flex" justify="end">
                <el-button type="primary" @click="saveTask">保存</el-button>
                <el-button @click="handleClose">取消</el-button>
            </el-row>
        </el-form>
    </el-dialog>
</template>

<script setup>
import {ref,reactive, watch,onMounted} from "vue"
import { ElMessage } from "element-plus";
import {insertData,queryById,uptateData} from "./Webtimetask.js"
// 接收的信息
const props = defineProps(["create_edit","edit"]); // 接收父组件传递的显示状态
// 发送的信息
const emit = defineEmits(["close","updatelist"]);
// 关闭-发送
const handleClose = () => {
  emit("close");  // 通知父组件关闭弹窗
};
// 弹窗数据
const taskForm = reactive({
    id:0,
    task_name:'',
    task_type:'',
    interval_time:'',
    fixed_time:'',
    project_id:'',
    collection_id:'',
    cron_time:'',
    collection_env_type:''
})
// 模版实例
const editFormRef = ref(null)
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
    cron_time: [    {
      validator: (rule, value, callback) => {
        if (taskForm.task_type === 'cron_task' && !value) {
          callback(new Error('请输入cron表达式'));
        }else if (taskForm.task_type === 'cron_task' && !validateCronExpression(value)) {
          callback(new Error('请输入有效的Unix crontab 5字段表达式'));
        }else {
          callback();
        }
      },
      trigger: 'blur'
    }],
    project_id: [{ required: true, message: '请选择项目', trigger: 'change' }],
    collection_id: [{ required: true, message: '请选择集合', trigger: 'change' }],
    collection_env_type: [{ required: true, message: '请选择执行环境', trigger: 'change' }], // 新增：环境必选

})
// 弹窗内项目的列表值
import { queryAll as projectqueryall} from "../project/WebProject";
const innerProjectList = ref([]);
// 弹窗内项目的获取
const getInnerProjectList = () => {
    projectqueryall().then((res) => {
        console.log("弹窗内项目的列表值为:", res.data.data);
        innerProjectList.value = res.data.data;
    });
};
getInnerProjectList()
// 弹窗内项目切换
const innerProjectChange = () => {
    // 先清空弹窗内集合列表
    taskForm.collection_id = '';
    getInnerProjectList();
    getcollectionlist()
};
// 测试集
const innerCollectionList = ref([])
// 获取测试集
import { queryByPage as collectionqueryall} from "../collection/WebCollectionInfo.js";
// 集合的获取
const getcollectionlist = () =>{
    collectionqueryall({
        "page":1,
        "pageSize":9999999,
        "project_id":taskForm.project_id,
        "collection_env_type": taskForm.collection_env_type // 新增：环境筛选
    }).then((res)=>{
        console.log("集合的列表值为:",res.data.data)
        innerCollectionList.value = res.data.data
    })
}
// 保存任务
const saveTask = () =>{
    // 通过表单实例获取验证
    editFormRef.value.validate((vaild)=>{
        if(vaild){
            if(taskForm.id>0){
                uptateData(taskForm).then((res)=>{
                    ElMessage.success("修改成功");
                        emit("close");
                        emit("updatelist")
                }).catch((err)=>{
                    ElMessage.error("修改失败");
                    console.log("新增表单数据失败:", err);
                })
                console.log("修改表单数据:", taskForm);
            }else{
                insertData(taskForm).then((res)=>{
                    if(res.data.code != -1){
                        ElMessage.success("新增成功");
                        emit("close");
                        emit("updatelist")                     
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
// 获取数据
const loadTaskData = (id) => {
    console.log("props.edit",props.edit)
    if (id > 0) {
        // 编辑模式：从API获取数据
        queryById(id).then((res) => {
            // 修正属性名，确保正确赋值
            taskForm.id = res.data.data.id;
            taskForm.task_name = res.data.data.task_name;
            taskForm.task_type = res.data.data.task_type;
            taskForm.interval_time = res.data.data.interval_time;
            taskForm.fixed_time = res.data.data.fixed_time;
            taskForm.project_id = res.data.data.project_id;
            taskForm.collection_id = res.data.data.collection_id;
            taskForm.cron_time = res.data.data.cron_time;
            taskForm.collection_env_type = res.data.data.collection_env_type || ''; // 新增：回显环境
        });
    }else{
    taskForm.id = 0
    taskForm.task_name = ''
    taskForm.task_type = ''
    taskForm.interval_time = ''
    taskForm.fixed_time = ''
    taskForm.project_id = ''
    taskForm.collection_id = ''
    taskForm.cron_time = ''
    taskForm.collection_env_type = '' // 新增：清空环境
    }
};
// 监听props.edit变化
watch(() => props.edit, (newId) => {
    console.log("监听到edit变化:", newId);
    loadTaskData(newId);
    if(newId>0){
        console.log("执行禁用")
        isEditDisabled.value = true
        // getcollectionlist()
        // 延迟执行：确保taskForm.project_id和collection_env_type已赋值
        setTimeout(() => {
            getcollectionlist();
            }, 100);
    }else{
        isEditDisabled.value = false
    }
});
// 禁止编辑状态
const isEditDisabled = ref(false); // 初始为可编辑状态

// Cron表达式验证函数
const validateCronExpression = (expression) => {
    if (!expression) return false;
    
    // 去除首尾空格并分割字段
    const fields = expression.trim().split(/\s+/);
    
    // 必须恰好有5个字段
    if (fields.length !== 5) {
        return false;
    }
    
    // 定义每个字段的有效范围和允许的字符
    const fieldSpecs = [
        { name: '分钟', min: 0, max: 59 },
        { name: '小时', min: 0, max: 23 },
        { name: '日', min: 1, max: 31 },
        { name: '月', min: 1, max: 12 },
        { name: '星期', min: 0, max: 7 } // 0和7都代表周日
    ];
    
    // 验证每个字段
    for (let i = 0; i < 5; i++) {
        const field = fields[i];
        const spec = fieldSpecs[i];
        
        // 验证字段是否只包含允许的字符
        if (!/^[\d\*\/\-\,]+$/.test(field)) {
            return false;
        }
        
        // 如果不是星号，进一步验证数字范围
        if (field !== '*') {
            // 分割多个值（逗号分隔）
            const parts = field.split(',');
            
            for (const part of parts) {
                // 处理范围（如 1-5）
                if (part.includes('-')) {
                    const range = part.split('-');
                    if (range.length !== 2) return false;
                    
                    const start = parseInt(range[0], 10);
                    const end = parseInt(range[1], 10);
                    
                    if (isNaN(start) || isNaN(end) || start < spec.min || end > spec.max || start > end) {
                        return false;
                    }
                }
                // 处理间隔（如 */2）
                else if (part.includes('/')) {
                    const intervalParts = part.split('/');
                    if (intervalParts.length !== 2 || intervalParts[0] !== '*') return false;
                    
                    const step = parseInt(intervalParts[1], 10);
                    if (isNaN(step) || step <= 0) return false;
                }
                // 处理单个数字
                else {
                    const num = parseInt(part, 10);
                    if (isNaN(num) || num < spec.min || num > spec.max) {
                        return false;
                    }
                }
            }
        }
    }
    
    return true;
};

// 新增：弹窗内环境切换事件
const innerEnvChange = () => {
  taskForm.collection_id = ''; // 清空选中的集合
  getcollectionlist(); // 重新查询（项目+环境）
};

// 新增：环境枚举列表
const envTypeOptions = ref([
  { label: '通用环境', value: 'common' },
  { label: '测试环境', value: 'test' },
  { label: '预发布环境', value: 'stage' },
  { label: '生产环境', value: 'online' }
])
</script>
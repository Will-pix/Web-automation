from apscheduler.schedulers.background import BackgroundScheduler
from flask import current_app
# from apitest.model.ApiTimeTaskModel import ApiTimeTask
from webtest.model.WebTimeTaskModel import WebTimeTask
# from apitest.api.ApiCollectionController import execute_test_task
from webtest.api.WebCollectionInfoController import excuteTest_run
from datetime import datetime, time
from extensions import database
# from app import application  # Moved inside functions
from apscheduler.triggers.cron import CronTrigger

scheduler = BackgroundScheduler()

# 封装 execute_test 函数的调用逻辑，并更新任务表数据
def execute_test_and_update_task(collection_id, task_id):
    print("执行了execute_test_and_update_task")
    print(f"=== 执行任务：task_id={task_id}，collection_id={collection_id} ===")
    try:
        from app import application
        with application.app_context():  # 使用 application 的上下文
            # 查询任务表的免打扰是否开启
            task = WebTimeTask.query.get(task_id)
            inform_value = task.inform
            # 调用 execute_test 函数并获取返回结果
            response = excuteTest_run(collection_id,inform_value,task)
            result = response.get_json()  # 将 Response 对象转换为字典
            print("定时任务调用的返回值", result)
            is_success = result.get('msg') == '执行结束，测试成功'
            # 获取当前时间
            now = datetime.now()
            # 获取任务对象
            task = WebTimeTask.query.get(task_id)
            if task:
                # 更新任务的最近执行时间
                task.last_time = now
                # 更新任务的执行状态
                task.is_state = is_success
                # 更新任务的执行总次数
                task.task_num = (task.task_num or 0) + 1
                # 提交数据库更改
                database.session.commit()
        return result
    except Exception as e:
        print(f"执行定时测试任务时出错: {e}")
        return {'success': False, 'error': str(e)}

# 重新加载所有定时任务
def reload_tasks():
    print("执行了reload_tasks")
    from app import application
    with application.app_context():
      # 查询任务表
        tasks = WebTimeTask.query.all()
        # 提取任务表的所有id
        db_task_ids = {str(task.id) for task in tasks}
        # 移除数据库中不存在的任务
        for job in scheduler.get_jobs():
            job_id_str = str(job.id)
            if job_id_str != job_id_name() and job_id_str not in db_task_ids:
                scheduler.remove_job(job.id)
                print(f"已移除任务 ID: {job.id}")
            # 查询出要执行的集合id，执行方式，执行时间
        for task in tasks:
            task_id = task.id
            collection_id = task.collection_id
            task_type = task.task_type
            interval_time = task.interval_time
            fixed_time = task.fixed_time
            cron_time = task.cron_time

            # 如果这个taskid已经有任务了就放进existing_job
            existing_job = scheduler.get_job(str(task_id))
            print("当前已存在的任务配置信息:",existing_job)
            # 如果是间隔任务
            if task_type == 'interval_task':
                try:
                    # 小时间隔
                    hours = int(interval_time)
                    # 如果当前的任务是存在的
                    if existing_job:
                        existing_job_trigger = str(existing_job.trigger)
                        print("existing_job得信息:", str(existing_job_trigger))
                        # 构造数据
                        strvalue = "interval[{}:00:00]".format(hours)
                        # strvalue = "interval[0:01:00]"  #测试使用
                        print("构造的数据为:",strvalue)
                        if existing_job_trigger!= strvalue:
                            print("他们不相等！")
                            # 配置有变化，更新任务
                            scheduler.reschedule_job(str(task_id), trigger='interval', hours=hours)
                            print(f"更新了间隔任务,id为：{task_id}")
                            print("更新后当前的值为:",scheduler.get_job(str(task_id)))
                    else:
                        # 任务不存在，添加新任务
                        # scheduler.add_job(func=lambda: execute_test_and_update_task(collection_id, task_id),
                        #                   trigger='interval', hours=hours, id=str(task_id))
                        scheduler.add_job(
                            # 用默认参数 cid=collection_id、tid=task_id 捕获当前值
                            func=lambda cid=collection_id, tid=task_id: execute_test_and_update_task(cid, tid),
                            trigger='interval', hours=hours, id=str(task_id)
                        )
                        print("添加了间隔任务,id为：", task_id)

                except ValueError:
                    print(f"无效的间隔时间: {interval_time}")
            # 如果是定时任务
            elif task_type == 'fixed_task':
                try:
                    # 分钟间隔
                    target_time = time(*map(int, fixed_time.split(':')))
                    if existing_job:
                        # 使用 split 方法按冒号切割字符串
                        hour, minute = fixed_time.split(':')
                        # 将 minute 转换为整数再转回字符串以去掉前导零-这里为了分钟省略0
                        minute = str(int(minute))
                        # 构造一个字符串与当前的对比
                        strvalue = "cron[hour='{}', minute='{}']".format(hour,minute)
                        print("构造的数据为:",strvalue)
                        # 当前的值
                        existing_job_trigger = str(existing_job.trigger)
                        print("existing_job得信息:", str(existing_job_trigger))
                        if strvalue!= existing_job_trigger:
                            print("他们不相等")
                            # 配置有变化，更新任务
                            scheduler.reschedule_job(str(task_id), trigger='cron', hour=target_time.hour,
                                                     minute=target_time.minute)
                            print(f"更新了定时任务,id为：{task_id}")
                            print("更新后当前的值为:",scheduler.get_job(str(task_id)))

                    else:
                        # 任务不存在，添加新任务
                        # scheduler.add_job(func=lambda: execute_test_and_update_task(collection_id, task_id),
                        #                   trigger='cron', hour=target_time.hour, minute=target_time.minute,
                        #                   id=str(task_id))
                        scheduler.add_job(
                            func=lambda cid=collection_id, tid=task_id: execute_test_and_update_task(cid, tid),
                            trigger='cron', hour=target_time.hour, minute=target_time.minute,
                            id=str(task_id)
                        )
                        print("添加了定时任务,id为：", task_id)
                except ValueError:
                    print(f"无效的固定时间: {fixed_time}")
            # 如果是cron自定义任务
            elif task_type == 'cron_task':
                try:
                    cron_expr = cron_time
                    print("表达式为:",cron_expr)
                    # 直接使用 CronTrigger.from_crontab() 解析表达式
                    trigger = CronTrigger.from_crontab(cron_expr)
                    if not cron_expr:
                        raise ValueError("Cron表达式为空")

                    if existing_job:
                        # 关键：用数据库表达式创建临时触发器，获取其字符串格式
                        temp_trigger = CronTrigger.from_crontab(cron_expr)
                        target_trigger_str = str(temp_trigger)  # 转换为如 "cron[month='*', ...]" 的格式
                        # print("从现有数据库构造的表达式:", target_trigger_str)

                        # 直接获取现有触发器的字符串
                        existing_trigger_str = str(existing_job.trigger)

                        print("从现有触发器构造的表达式:", existing_trigger_str)
                        print("从现有数据库构造的表达式:", target_trigger_str)

                        if existing_trigger_str != target_trigger_str:
                            print("他们不相等")
                            scheduler.reschedule_job(
                                str(task_id),
                                trigger=trigger,
                            )
                            print(f"更新了Cron任务,id为：{task_id}")
                            print("更新后当前的值为:",scheduler.get_job(str(task_id)))
                    else:
                        # scheduler.add_job(
                        #     func=lambda: execute_test_and_update_task(collection_id, task_id),
                        #     trigger=trigger,
                        #     id=str(task_id)
                        # )
                        scheduler.add_job(
                            func=lambda cid=collection_id, tid=task_id: execute_test_and_update_task(cid, tid),
                            trigger=trigger,
                            id=str(task_id)
                        )
                        print(f"添加了Cron任务,id为：{task_id}")
                except Exception as e:
                    print(f"无效的Cron表达式: {task.cron_time}, 错误: {str(e)}")
# 任务调用需要执行的
def setup_scheduler():
    print("执行了setup_scheduler")
    try:
        job_id = job_id_name()
        scheduler.add_job(func=reload_tasks, trigger='interval', minutes=1, id=job_id)
        scheduler.start()
        print(f"调度器是否正在运行: {scheduler.running}")
    except Exception as e:
        print(f"调度器启动时出错: {e}")

def job_id_name():
    return "lunxunrenwuid"
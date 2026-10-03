def exec_script(script, step, context):
    # 如果没有前置脚本什么都不做
    if script is None: return
    # 导包的目的是为了让脚本能够使用function里的方法
    script = "from apitest.tool.apirunner.extend.functions import * \n" + script
    # exec执行python代码-并将步骤和全局变量都带进去
    exec(script, {"step": step, "context": context})
    print("++++++++++++++++++++++++++++++++++++++++++")
    print("前/后事件全局变量:",context)
    print("++++++++++++++++++++++++++++++++++++++++++")


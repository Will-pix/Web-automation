import subprocess
from datetime import datetime


def auto_commit_py_files():
    """提交/app/webtest/keyswords目录下的py文件变更并推送，详细打印日志"""
    project_dir = "/app"
    generated_dir = "webtest/keyswords"
    branch = "main"  # 确保与远程分支名一致

    # 执行Git命令并详细打印日志
    def git(cmd):
        print(f"\n===== 执行Git命令: {cmd} =====")
        result = subprocess.run(
            cmd,
            cwd=project_dir,
            shell=True,
            capture_output=True,
            text=True
        )
        # 打印命令结果
        print(f"返回码: {result.returncode}")  # 0表示成功，非0表示失败
        if result.stdout:
            print(f"标准输出:\n{result.stdout}")
        if result.stderr:
            print(f"错误输出:\n{result.stderr}")
        return result

    try:
        # 1. 检查文件变更
        status_result = git(f"git status --porcelain {generated_dir}/*.py")
        status_output = status_result.stdout
        print(f"===== 检测到的文件状态 =====")
        print(status_output)

        # 判断是否有.py文件变更
        has_py_changes = any(line.endswith(".py") for line in status_output.splitlines())
        if not has_py_changes:
            print("没有.py文件变更，无需提交")
            return False

        # 2. 暂存文件
        add_result = git(f"git add {generated_dir}/*.py")
        if add_result.returncode != 0:
            print("git add 失败，终止流程")
            return False

        # 3. 提交变更
        commit_msg = f"自动提交: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        commit_result = git(f'git commit -m "{commit_msg}"')
        if commit_result.returncode != 0:
            print("git commit 失败，可能无实际变更（如文件内容未修改）")
            return False

        # 4. 推送变更
        push_result = git(f"git push -u origin {branch}")
        if push_result.returncode == 0:
            print(f"\n===== 推送成功！提交信息: {commit_msg} =====")
            return True
        else:
            print(f"\n===== 推送失败！返回码: {push_result.returncode} =====")
            return False

    except Exception as e:
        print(f"\n===== 提交流程发生异常: {str(e)} =====")
        return False
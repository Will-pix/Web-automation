import os
import shutil
import platform
from datetime import datetime, timedelta
import time


def get_folder_creation_time(folder_path):
    """
    获取文件夹的创建时间（兼容不同操作系统）
    返回时间戳（秒）
    """
    if platform.system() == 'Windows':
        # Windows系统使用创建时间
        return os.path.getctime(folder_path)
    else:
        # macOS/Linux系统，先尝试获取创建时间( Birth time )
        try:
            stat = os.stat(folder_path)
            # macOS的创建时间在st_birthtime属性
            if hasattr(stat, 'st_birthtime'):
                return stat.st_birthtime
            else:
                # Linux系统没有统一的创建时间属性，使用状态改变时间替代
                return stat.st_ctime
        except Exception as e:
            print(f"获取 {folder_path} 创建时间失败: {e}")
            return os.path.getmtime(folder_path)  # fallback to modification time


def get_folder_size(folder_path):
    """获取指定文件夹的大小，返回字节数"""
    if not os.path.isdir(folder_path):
        raise ValueError(f"路径 {folder_path} 不是一个有效的目录")

    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.exists(fp):
                try:
                    total_size += os.path.getsize(fp)
                except OSError as e:
                    print(f"获取文件 {fp} 大小失败: {e}")
    return total_size


def format_size(size_bytes):
    """将字节数转换为人类可读的格式"""
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    size = size_bytes
    unit_index = 0

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    return f"{size:.2f} {units[unit_index]}"


def delete_old_folders(folder_path, days=3):
    """
    只删除指定文件夹中超过指定天数的子文件夹（根据创建时间判断）
    """
    if not os.path.isdir(folder_path):
        raise ValueError(f"路径 {folder_path} 不是一个有效的目录")

    # 计算截止时间（days天前）
    cutoff_seconds = time.time() - (days * 86400)  # 86400秒 = 1天
    cutoff_time = datetime.fromtimestamp(cutoff_seconds)

    print(f"将删除 {folder_path} 中创建时间早于 {cutoff_time} 的文件夹")

    deleted_folders_count = 0
    deleted_size = 0

    # 获取绝对路径，避免相对路径问题
    abs_folder_path = os.path.abspath(folder_path)

    # 遍历所有直接子文件夹
    for item in os.listdir(abs_folder_path):
        item_path = os.path.join(abs_folder_path, item)

        # 只处理文件夹
        if os.path.isdir(item_path):
            try:
                # 获取文件夹的创建时间（兼容不同系统）
                ctime = get_folder_creation_time(item_path)
                ctime_str = datetime.fromtimestamp(ctime).strftime('%Y-%m-%d %H:%M:%S')

                # 打印每个文件夹的信息，方便调试
                # print(f"检查文件夹: {item_path}，创建时间: {ctime_str}")

                if ctime < cutoff_seconds:
                    # 计算要删除的文件夹大小
                    folder_size = get_folder_size(item_path)

                    # 删除整个文件夹及其内容
                    shutil.rmtree(item_path)
                    deleted_folders_count += 1
                    deleted_size += folder_size
                    print(f"已删除文件夹: {item_path}")

            except PermissionError:
                print(f"没有权限操作文件夹 {item_path}")
            except Exception as e:
                print(f"处理文件夹 {item_path} 时出错: {str(e)}")

    return {
        'deleted_folders_count': deleted_folders_count,
        'deleted_size': deleted_size,
        'deleted_size_human': format_size(deleted_size)
    }


def folder_cleanup_main(folder_path='../report', retention_days= 7, size_threshold=7 * (1024 ** 3), force_clean=False):
    """
    文件夹清理总函数，根据创建时间清理旧的子文件夹
    该接口按指定 (../report 目录) 按创建时间清理 7 天前的子文件夹，当目录超 7GB 时触发，也可强制清理。
    """
    print("进入执行报告处理")
    result = {
        'folder_path': folder_path,
        'success': False,
        'cleaned': False,
        'error': None
    }

    try:
        # 转换为绝对路径
        folder_path = os.path.abspath(folder_path)
        print("folder_path",folder_path)

        if not os.path.isdir(folder_path):
            result['error'] = f"路径 {folder_path} 不是一个有效的目录"
            return result

        # 获取当前文件夹大小
        current_size = get_folder_size(folder_path)
        current_size_human = format_size(current_size)
        result['previous_size'] = current_size
        result['previous_size_human'] = current_size_human

        print(f"文件夹 {folder_path} 当前大小: {current_size_human}")

        # 决定是否需要清理
        need_clean = False
        if force_clean:
            need_clean = True
        elif size_threshold is None:
            need_clean = True
        elif current_size >= size_threshold:
            need_clean = True

        if not need_clean:
            print(f"未超过阈值 {format_size(size_threshold)}，无需清理")
            result['success'] = True
            return result

        # 执行清理（只清理文件夹）
        print(f"开始清理 {retention_days} 天前创建的子文件夹...")
        delete_result = delete_old_folders(folder_path, retention_days)

        # 计算清理后的大小
        new_size = get_folder_size(folder_path)
        new_size_human = format_size(new_size)

        print(f"清理完成: 删除了 {delete_result['deleted_folders_count']} 个文件夹，"
              f"释放了 {delete_result['deleted_size_human']} 空间")
        print(f"清理后文件夹大小: {new_size_human}")

        # 更新结果
        result.update({
            'success': True,
            'cleaned': True,
            'new_size': new_size,
            'new_size_human': new_size_human, **delete_result
        })

    except Exception as e:
        error_msg = f"处理文件夹时出错: {str(e)}"
        print(error_msg)
        result['error'] = error_msg

    return result


# 使用示例
if __name__ == "__main__":
    folder_path = "../report"
    retention_days = 3
    # size_threshold = 7 * (1024 ** 3)  # 7GB
    # size_threshold = 10 * (1024 ** 2)  # 10MB

    force_clean = False
    folder_cleanup_main(folder_path='../report', retention_days= 7, size_threshold=7 * (1024 ** 3), force_clean=False)
    """    按创建时间清理指定目录下的过期子文件夹，支持条件触发和强制清理
    
    参数:
        folder_path (str): 待清理的根目录路径。
            示例: "../report" 或 "/data/reports"
            默认值: "../report"
        
        retention_days (int): 子文件夹保留天数（创建时间超过此时长会被清理）。
            示例: 3（保留3天内的文件夹）
            默认值: 7
        
        size_threshold (int): 触发清理的目录大小阈值（字节）。
            当根目录总大小 ≥ 此值时才清理（force_clean=True时忽略）。
            示例: 10*(1024**2) 表示10MB，7*(1024**3)表示7GB
            默认值: 7*(1024**3)（7GB）
        
        force_clean (bool): 是否强制清理，忽略size_threshold限制。
            True: 无论目录大小，直接清理过期文件夹
            False: 仅当目录大小超过阈值时清理
            默认值: False"""


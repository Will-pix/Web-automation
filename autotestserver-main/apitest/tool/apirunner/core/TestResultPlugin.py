# import pytest
#
#
# class TestResultPlugin:
#     def __init__(self):
#         self.results = []
#         self.output = []
#
#
#     def pytest_runtest_logreport(self, report):
#         if report.when == "call":
#             self.results.append({
#                 "nodeid": report.nodeid,
#                 "outcome": report.outcome
#             })
#
#
#
#     def pytest_collectreport(self, report):
#         if report.outcome != 'passed':
#             self.results.append({
#                 "nodeid": report.nodeid,
#                 "outcome": report.outcome
#             })

import pytest



import pytest

class ResultPlugin:
    def __init__(self):
        self.results = []
        self.output = []

    def pytest_runtest_logreport(self, report):
        if report.when == "call":
            # 获取测试用例的标准输出
            stdout = report.capstdout
            # 获取测试用例的标准错误输出
            stderr = report.capstderr

            result = {
                "nodeid": report.nodeid,
                "outcome": report.outcome,
                "stdout": stdout,
                "stderr": stderr
            }
            self.results.append(result)
            # 可以根据需要将 stdout 和 stderr 合并存储
            combined_output = f"stdout:\n{stdout}\nstderr:\n{stderr}"
            self.output.append(combined_output)

    def pytest_collectreport(self, report):
        if report.outcome != 'passed':
            self.results.append({
                "nodeid": report.nodeid,
                "outcome": report.outcome
            })
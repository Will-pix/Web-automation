import os

# 确保 Scoop shims 在 PATH 中（Windows 上 subprocess 需要）
scoop_shims = os.path.expanduser("~/scoop/shims")
if os.path.isdir(scoop_shims) and scoop_shims not in os.environ.get("PATH", ""):
    os.environ["PATH"] = scoop_shims + os.pathsep + os.environ.get("PATH", "")

from flask import Flask
from flask_cors import CORS

from extensions import database, jwt, migrate
from platformconfig.service.runtime_store import load_settings


application = Flask(__name__)
flask_env = os.getenv("FLASK_ENV", "development")

if flask_env == "production":
    config_file = "config/prod_settings.py"
else:
    config_file = "config/dev_settings.py"

application.config.from_pyfile(config_file)

runtime_settings = load_settings()
application.config["OPENAI_API_KEY"] = runtime_settings["ai"].get(
    "api_key", application.config.get("OPENAI_API_KEY", "")
)
application.config["AI_MODEL_NAME"] = runtime_settings["ai"].get(
    "model_name", application.config.get("AI_MODEL_NAME", "")
)
application.config["AI_API_BASE"] = runtime_settings["ai"].get(
    "api_base", application.config.get("AI_API_BASE", "")
)
application.config["FEISHU_APP_ID"] = runtime_settings.get("feishu", {}).get(
    "app_id", ""
) or application.config.get("FEISHU_APP_ID", "")
application.config["FEISHU_APP_SECRET"] = runtime_settings.get("feishu", {}).get(
    "app_secret", ""
) or application.config.get("FEISHU_APP_SECRET", "")

if flask_env == "production":
    @application.before_request
    def before_request():
        from core.auth_decocator import jwt_middleware

        result = jwt_middleware()
        if result:
            return result


CORS(application, resources=r"/*")
database.init_app(application)
jwt.init_app(application)
migrate.init_app(application, database)
application.config["JSON_AS_ASCII"] = False


def setup_application_web():
    if flask_env == "production":
        from webtest.api.scheduler_task import setup_scheduler

        setup_scheduler()


from login.api import LoginController
from platformconfig.api import PlatformSettingsController
from sysmanage.api import userController
from login.api import feishu_login

application.register_blueprint(LoginController.module_route, url_prefix="/api")
application.register_blueprint(feishu_login.module_route, url_prefix="/api")
application.register_blueprint(userController.module_route, url_prefix="/api")
application.register_blueprint(PlatformSettingsController.module_route, url_prefix="/api")

from apitest.api import (
    ApiCaseController,
    ApiCollectionController,
    ApiHistoryController,
    ApiInfoController,
    ApiModuleController,
    ApiProjectController,
    ApiTimeTaskController,
)

application.register_blueprint(ApiProjectController.module_route, url_prefix="/api")
application.register_blueprint(ApiModuleController.module_route, url_prefix="/api")
application.register_blueprint(ApiInfoController.module_route, url_prefix="/api")
application.register_blueprint(ApiCollectionController.module_route, url_prefix="/api")
application.register_blueprint(ApiCaseController.module_route, url_prefix="/api")
application.register_blueprint(ApiHistoryController.module_route, url_prefix="/api")
application.register_blueprint(ApiTimeTaskController.module_route, url_prefix="/api")

from webtest.api import (
    QualityDashboardController,
    WebBrowserController,
    WebCollectionDetailController,
    WebCollectionInfoController,
    WebDbBaseController,
    WebFileController,
    WebHistoryController,
    WebHistoryTimeController,
    WebInfoController,
    WebInfoPreController,
    WebInfoStepController,
    WebKeyWordController,
    WebOperationTypeController,
    WebProjectController,
    WebReportController,
    WebTimeTaskController,
    WorkbenchController,
)

application.register_blueprint(WebProjectController.module_route, url_prefix="/api")
application.register_blueprint(WebDbBaseController.module_route, url_prefix="/api")
application.register_blueprint(WebBrowserController.module_route, url_prefix="/api")
application.register_blueprint(WebOperationTypeController.module_route, url_prefix="/api")
application.register_blueprint(WebKeyWordController.module_route, url_prefix="/api")
application.register_blueprint(WebInfoController.module_route, url_prefix="/api")
application.register_blueprint(WebInfoStepController.module_route, url_prefix="/api")
application.register_blueprint(WebReportController.module_route, url_prefix="/api")
application.register_blueprint(WebCollectionInfoController.module_route, url_prefix="/api")
application.register_blueprint(WebCollectionDetailController.module_route, url_prefix="/api")
application.register_blueprint(WebHistoryController.module_route, url_prefix="/api")
application.register_blueprint(WebTimeTaskController.module_route, url_prefix="/api")
application.register_blueprint(WebFileController.module_route, url_prefix="/api")
application.register_blueprint(WebInfoPreController.module_route, url_prefix="/api")
application.register_blueprint(WebHistoryTimeController.module_route, url_prefix="/api")
application.register_blueprint(QualityDashboardController.module_route, url_prefix="/api")
application.register_blueprint(WorkbenchController.module_route, url_prefix="/api")

setup_application_web()

if __name__ == "__main__":
    application.run()

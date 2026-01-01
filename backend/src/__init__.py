from robyn import Robyn, SubRouter, ALLOW_CORS

# 导入各个业务模块的 Router
from .routes.jobs import jobs_router
from .routes.data_processing import datasets_router
from .routes.statistics import statistics_router
from .routes.patterns import patterns_router
from .routes.reports import reports_router
from .routes.recommendations import recommendations_router
from .routes.dashboard import dashboard_router
from .routes.anomalies import anomalies_router
from .routes.alerts import alerts_router
from .routes.simulations import simulations_router
from .routes.behavior import behavior_router
from .routes.agent import qa_router

# 初始化 App
app = Robyn(__file__)

# 配置 CORS (根据 API 文档 3.2 节)
ALLOW_CORS(app, origins=["*"])

# 定义 API v1 主路由
api_v1 = SubRouter(__name__, prefix="/api/v1")

# 将各个模块挂载到 v1 路由下
# 注意：Robyn 的 SubRouter 会自动拼接 prefix
api_v1.include_router(jobs_router)            # /api/v1/jobs
api_v1.include_router(datasets_router)        # /api/v1/datasets
api_v1.include_router(statistics_router)      # /api/v1/statistics
api_v1.include_router(patterns_router)        # /api/v1/load-patterns
api_v1.include_router(reports_router)         # /api/v1/reports
api_v1.include_router(recommendations_router) # /api/v1/recommendations
api_v1.include_router(dashboard_router)       # /api/v1/dashboards
api_v1.include_router(anomalies_router)       # /api/v1/anomalies
api_v1.include_router(alerts_router)          # /api/v1/alert-config
api_v1.include_router(simulations_router)     # /api/v1/simulations
api_v1.include_router(behavior_router)        # /api/v1/behavior-analyses
api_v1.include_router(qa_router)              # /api/v1/qa

# 将 v1 路由挂载到主 App
app.include_router(api_v1)

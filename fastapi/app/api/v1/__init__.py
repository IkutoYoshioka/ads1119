# app/api/v1/__init__.py
from fastapi import APIRouter

from . import (
    auth,
    password_reset,
    employees,
    sites,
    offices,
    assignments,
    evaluation_tasks,
    evaluation_results,
    feedbacks,
    facility_results,
    analysis,
    progress,
    question_master,
    evaluation_forms,
    notices,
    admin_password_reset_requests,
    login_ip_policies,
    dashboard,
    exports,
    imports,
    audit_logs,
    periods,
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(password_reset.router)
api_router.include_router(employees.router)
api_router.include_router(sites.router)
api_router.include_router(offices.router)
api_router.include_router(assignments.router)
api_router.include_router(evaluation_tasks.router)
api_router.include_router(evaluation_results.router)
api_router.include_router(feedbacks.router)
api_router.include_router(facility_results.router)
api_router.include_router(analysis.router)
api_router.include_router(progress.router)
api_router.include_router(question_master.router)
api_router.include_router(evaluation_forms.router)
api_router.include_router(notices.router)
api_router.include_router(admin_password_reset_requests.router)
api_router.include_router(login_ip_policies.router)
api_router.include_router(dashboard.router)
api_router.include_router(exports.router)
api_router.include_router(imports.router)
api_router.include_router(audit_logs.router)
api_router.include_router(periods.router)

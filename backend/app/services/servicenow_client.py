import logging
from dataclasses import dataclass
from typing import Any

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class ServiceNowConfigError(RuntimeError):
    """Raised when ServiceNow configuration is missing."""


class ServiceNowAPIError(RuntimeError):
    """Raised when a ServiceNow API call fails."""


@dataclass
class ServiceNowIncidentCreateInput:
    short_description: str
    description: str
    category: str
    impact: str = "2"
    urgency: str = "2"
    comments: str | None = None
    work_notes: str | None = None


@dataclass
class ServiceNowIncidentResult:
    number: str
    sys_id: str
    short_description: str
    state: str | None = None
    category: str | None = None
    priority: str | None = None
    impact: str | None = None
    urgency: str | None = None
    comments: str | None = None
    work_notes: str | None = None


class ServiceNowClient:
    """
    Thin ServiceNow Table API client.

    Supports:
    - Create incident
    - Retrieve incident by number
    - Retrieve incident by sys_id
    - Update incident comments/work notes
    """

    def __init__(self) -> None:
        self.settings = get_settings()
        self._validate_config()

        self.base_url = self.settings.servicenow_instance_url.rstrip("/")
        self.auth = (
            self.settings.servicenow_username,
            self.settings.servicenow_password,
        )

        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def _validate_config(self) -> None:
        missing = []

        if not self.settings.servicenow_instance_url:
            missing.append("SERVICENOW_INSTANCE_URL")

        if not self.settings.servicenow_username:
            missing.append("SERVICENOW_USERNAME")

        if not self.settings.servicenow_password:
            missing.append("SERVICENOW_PASSWORD")

        if missing:
            raise ServiceNowConfigError(
                f"Missing ServiceNow configuration values: {', '.join(missing)}"
            )

    def _request(
        self,
        method: str,
        path: str,
        json_payload: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{self.base_url}{path}"

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.request(
                    method=method,
                    url=url,
                    auth=self.auth,
                    headers=self.headers,
                    json=json_payload,
                    params=params,
                )

            if response.status_code >= 400:
                raise ServiceNowAPIError(
                    f"ServiceNow API failed: {response.status_code} {response.text}"
                )

            return response.json()

        except httpx.HTTPError as exc:
            logger.exception("ServiceNow HTTP request failed")
            raise ServiceNowAPIError(f"ServiceNow HTTP request failed: {exc}") from exc

    def map_category_to_servicenow(self, category: str) -> str:
        """
        Maps project categories to simple ServiceNow incident category values.

        PDI category choices can vary, so these are intentionally conservative.
        """

        mapping = {
            "Network / VPN": "network",
            "Password / Account": "inquiry",
            "Software Request": "software",
            "Hardware Issue": "hardware",
            "Email / Outlook": "software",
            "Access Request": "inquiry",
            "Security Incident": "security",
            "Cloud / Account Access": "inquiry",
            "General IT Query": "inquiry",
        }

        return mapping.get(category, "inquiry")

    def map_priority_to_impact_urgency(self, priority: str, urgency: str) -> tuple[str, str]:
        """
        ServiceNow impact/urgency commonly use:
        1 = High
        2 = Medium
        3 = Low
        """

        def map_level(value: str) -> str:
            normalized = value.lower()

            if normalized in {"critical", "high"}:
                return "1"

            if normalized == "medium":
                return "2"

            return "3"

        impact = map_level(priority)
        urgency_value = map_level(urgency)

        return impact, urgency_value

    def create_incident(
        self,
        data: ServiceNowIncidentCreateInput,
    ) -> ServiceNowIncidentResult:
        payload: dict[str, Any] = {
            "short_description": data.short_description,
            "description": data.description,
            "category": data.category,
            "impact": data.impact,
            "urgency": data.urgency,
        }

        if data.comments:
            payload["comments"] = data.comments

        if data.work_notes:
            payload["work_notes"] = data.work_notes

        response = self._request(
            method="POST",
            path="/api/now/table/incident",
            json_payload=payload,
        )

        result = response.get("result", {})

        if not result.get("number") or not result.get("sys_id"):
            raise ServiceNowAPIError(
                f"ServiceNow incident creation returned unexpected response: {response}"
            )

        return ServiceNowIncidentResult(
            number=result["number"],
            sys_id=result["sys_id"],
            short_description=result.get("short_description", data.short_description),
            state=result.get("state"),
            category=result.get("category"),
            priority=result.get("priority"),
            impact=result.get("impact"),
            urgency=result.get("urgency"),
            comments=result.get("comments"),
            work_notes=result.get("work_notes"),
        )

    def get_incident_by_number(self, ticket_number: str) -> ServiceNowIncidentResult:
        response = self._request(
            method="GET",
            path="/api/now/table/incident",
            params={
                "sysparm_query": f"number={ticket_number}",
                "sysparm_limit": "1",
            },
        )

        records = response.get("result", [])

        if not records:
            raise ServiceNowAPIError(f"Incident not found: {ticket_number}")

        result = records[0]

        return ServiceNowIncidentResult(
            number=result["number"],
            sys_id=result["sys_id"],
            short_description=result.get("short_description", ""),
            state=result.get("state"),
            category=result.get("category"),
            priority=result.get("priority"),
            impact=result.get("impact"),
            urgency=result.get("urgency"),
            comments=result.get("comments"),
            work_notes=result.get("work_notes"),
        )

    def get_incident_by_sys_id(self, sys_id: str) -> ServiceNowIncidentResult:
        response = self._request(
            method="GET",
            path=f"/api/now/table/incident/{sys_id}",
        )

        result = response.get("result", {})

        if not result:
            raise ServiceNowAPIError(f"Incident not found for sys_id: {sys_id}")

        return ServiceNowIncidentResult(
            number=result["number"],
            sys_id=result["sys_id"],
            short_description=result.get("short_description", ""),
            state=result.get("state"),
            category=result.get("category"),
            priority=result.get("priority"),
            impact=result.get("impact"),
            urgency=result.get("urgency"),
            comments=result.get("comments"),
            work_notes=result.get("work_notes"),
        )

    def update_incident(
        self,
        sys_id: str,
        comments: str | None = None,
        work_notes: str | None = None,
        state: str | None = None,
    ) -> ServiceNowIncidentResult:
        payload: dict[str, Any] = {}

        if comments:
            payload["comments"] = comments

        if work_notes:
            payload["work_notes"] = work_notes

        if state:
            payload["state"] = state

        if not payload:
            raise ServiceNowAPIError("No update fields provided.")

        response = self._request(
            method="PATCH",
            path=f"/api/now/table/incident/{sys_id}",
            json_payload=payload,
        )

        result = response.get("result", {})

        return ServiceNowIncidentResult(
            number=result["number"],
            sys_id=result["sys_id"],
            short_description=result.get("short_description", ""),
            state=result.get("state"),
            category=result.get("category"),
            priority=result.get("priority"),
            impact=result.get("impact"),
            urgency=result.get("urgency"),
            comments=result.get("comments"),
            work_notes=result.get("work_notes"),
        )
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Protocol

from agents.domain.models import AgentEvent, ChatResult
from agents.interfaces.api.schemas import ChatRequest


@dataclass(frozen=True, slots=True)
class ApiFilterContext:
    agent_name: str
    request: ChatRequest


class ApiFilter(Protocol):
    def transform_chat_request(
        self,
        request: ChatRequest,
        context: ApiFilterContext,
    ) -> ChatRequest | None: ...

    def transform_event(
        self,
        event: AgentEvent,
        context: ApiFilterContext,
    ) -> AgentEvent | None: ...

    def chat_response_fields(
        self,
        result: ChatResult,
        context: ApiFilterContext,
    ) -> dict[str, Any] | None: ...

    def event_fields(
        self,
        event: AgentEvent,
        context: ApiFilterContext,
    ) -> dict[str, Any] | None: ...


class ApiFilterPipeline:
    def __init__(self, filters: Sequence[ApiFilter] | None = None) -> None:
        self._filters = list(filters or ())

    def apply_request(self, request: ChatRequest, *, agent_name: str) -> ChatRequest:
        context = ApiFilterContext(agent_name=agent_name, request=request)
        current = request
        for api_filter in self._filters:
            transformed = api_filter.transform_chat_request(current, context)
            if transformed is not None:
                current = transformed
                context = ApiFilterContext(agent_name=agent_name, request=current)
        return current

    def apply_event(
        self,
        event: AgentEvent,
        *,
        request: ChatRequest,
        agent_name: str,
    ) -> AgentEvent | None:
        context = ApiFilterContext(agent_name=agent_name, request=request)
        current: AgentEvent | None = event
        for api_filter in self._filters:
            if current is None:
                return None
            current = api_filter.transform_event(current, context)
        return current

    def collect_chat_response_fields(
        self,
        result: ChatResult,
        *,
        request: ChatRequest,
        agent_name: str,
    ) -> dict[str, Any] | None:
        context = ApiFilterContext(agent_name=agent_name, request=request)
        payload: dict[str, Any] = {}
        for api_filter in self._filters:
            fields = _invoke_optional(
                api_filter,
                result,
                context,
                primary_method="chat_response_fields",
                fallback_method="chat_response_extras",
            )
            if fields:
                payload.update(fields)
        return payload or None

    def collect_event_fields(
        self,
        event: AgentEvent,
        *,
        request: ChatRequest,
        agent_name: str,
    ) -> dict[str, Any] | None:
        context = ApiFilterContext(agent_name=agent_name, request=request)
        payload: dict[str, Any] = {}
        for api_filter in self._filters:
            fields = _invoke_optional(
                api_filter,
                event,
                context,
                primary_method="event_fields",
                fallback_method="event_extras",
            )
            if fields:
                payload.update(fields)
        return payload or None


class BaseApiFilter:
    def transform_chat_request(
        self,
        request: ChatRequest,
        context: ApiFilterContext,
    ) -> ChatRequest | None:
        return request

    def transform_event(
        self,
        event: AgentEvent,
        context: ApiFilterContext,
    ) -> AgentEvent | None:
        return event

    def chat_response_fields(
        self,
        result: ChatResult,
        context: ApiFilterContext,
    ) -> dict[str, Any] | None:
        return None

    def event_fields(
        self,
        event: AgentEvent,
        context: ApiFilterContext,
    ) -> dict[str, Any] | None:
        return None


def _invoke_optional(
    api_filter: ApiFilter,
    *args: Any,
    primary_method: str,
    fallback_method: str,
) -> dict[str, Any] | None:
    primary = getattr(api_filter, primary_method, None)
    if callable(primary):
        return primary(*args)
    fallback = getattr(api_filter, fallback_method, None)
    if callable(fallback):
        return fallback(*args)
    return None

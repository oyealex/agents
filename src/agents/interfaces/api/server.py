from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

from agents.core.definitions import AgentConfigError, load_agent_registry, load_settings


INSTALL_API_MESSAGE = (
    "API dependencies are required to run the API server. "
    'Install them with: pip install -e ".[api]"'
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Agents API server")
    parser.add_argument(
        "--agent",
        default="default",
        help="Agent profile to serve, defaults to 'default'.",
    )
    parser.add_argument(
        "--agent-config",
        type=Path,
        default=None,
        help="Path to agents.yaml. Defaults to ./agents.yaml when it exists.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if importlib.util.find_spec("fastapi") is None:
        raise SystemExit(INSTALL_API_MESSAGE)

    try:
        import uvicorn
    except ImportError as exc:
        raise SystemExit(INSTALL_API_MESSAGE) from exc

    try:
        settings = load_settings(args.agent_config)
        registry = load_agent_registry(args.agent_config)
    except AgentConfigError as exc:
        raise SystemExit(str(exc)) from exc

    if args.agent not in registry.list_names():
        options = ", ".join(registry.list_names())
        raise SystemExit(f"Unknown agent '{args.agent}'. Available: {options}")

    from agents.interfaces.api.app import create_app

    uvicorn.run(
        create_app(
            agent_name=args.agent,
            agent_config_path=args.agent_config,
            agent_registry=registry,
            settings=settings,
        ),
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level="debug" if settings.debug else "info",
    )

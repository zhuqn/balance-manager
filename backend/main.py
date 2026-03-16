"""
FastAPI backend for Balance Management System.

Provides REST API for the frontend dashboard.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from core.manager import BalanceManager
from core.models import BalanceStatus, PlatformBalance, SystemSummary
from core.exceptions import ManualEntryRequired
from providers import (
    OpenRouterProvider,
    MiniMaxProvider,
    VolcengineProvider,
    BFLProvider,
    ManualProvider,
)
from storage import JSONStorage
from config import load_config, create_default_config, save_config


# ============================================================================
# Pydantic Models for API
# ============================================================================

class PlatformBalanceResponse(BaseModel):
    """API response for platform balance."""
    platform: str
    account_id: str = ""
    balance: float
    currency: str
    usage_this_month: float = 0.0
    usage_total: float = 0.0
    last_updated: str
    status: str
    raw_data: Dict[str, Any] = {}
    
    class Config:
        from_attributes = True


class SystemSummaryResponse(BaseModel):
    """API response for system summary."""
    total_balance: float
    platform_count: int
    platforms_active: int
    platforms_warning: int
    platforms_critical: int
    platforms_error: int
    balances: List[PlatformBalanceResponse]
    generated_at: str


class ManualEntryRequest(BaseModel):
    """Request body for manual balance entry."""
    balance: float = Field(..., gt=0, description="Balance amount")
    currency: str = Field(default="USD", description="Currency code")


class ConfigResponse(BaseModel):
    """API response for configuration."""
    thresholds: Dict[str, float]
    platforms: Dict[str, Dict[str, Any]]
    storage: Dict[str, str]


class ConfigUpdateRequest(BaseModel):
    """Request body for configuration update."""
    warning_threshold: Optional[float] = Field(None, gt=0)
    critical_threshold: Optional[float] = Field(None, gt=0)


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: str


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="Balance Management System API",
    description="REST API for managing third-party service balances",
    version="1.0.0",
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Helper Functions
# ============================================================================

def get_manager() -> BalanceManager:
    """Create and configure BalanceManager instance."""
    config = load_config()
    manager = BalanceManager(
        warning_threshold=config.thresholds.warning,
        critical_threshold=config.thresholds.critical,
    )
    register_providers(manager, config)
    return manager


def get_storage():
    """Get storage instance."""
    config = load_config()
    return JSONStorage(config.storage.path)


def register_providers(manager: BalanceManager, config):
    """Register all configured providers with the manager."""
    for name, pconfig in config.platforms.items():
        if not pconfig.enabled:
            continue
        
        if pconfig.method == "manual":
            provider = ManualProvider(platform_name=name)
        else:
            if name == "openrouter":
                provider = OpenRouterProvider(api_key=pconfig.api_key)
            elif name == "minimax":
                provider = MiniMaxProvider(api_key=pconfig.api_key)
            elif name == "volcengine":
                provider = VolcengineProvider(api_key=pconfig.api_key)
            elif name == "bfl":
                provider = BFLProvider(api_key=pconfig.api_key)
            else:
                provider = ManualProvider(platform_name=name)
        
        manager.register_provider(provider, pconfig)


# ============================================================================
# API Routes
# ============================================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now().isoformat(),
    )


@app.get("/api/summary", response_model=SystemSummaryResponse)
async def get_summary(refresh: bool = False):
    """
    Get summary of all platform balances.
    
    - **refresh**: If true, fetch fresh data from APIs
    """
    try:
        manager = get_manager()
        storage = get_storage()
        
        if refresh:
            summary = manager.check_and_summarize()
            # Save to storage
            storage.save_balances(summary.balances)
        else:
            balances = storage.load_balances()
            if not balances:
                # No data, do a fresh check
                summary = manager.check_and_summarize()
                storage.save_balances(summary.balances)
            else:
                summary = manager.get_summary(balances)
        
        return SystemSummaryResponse(
            total_balance=summary.total_balance,
            platform_count=summary.platform_count,
            platforms_active=summary.platforms_active,
            platforms_warning=summary.platforms_warning,
            platforms_critical=summary.platforms_critical,
            platforms_error=summary.platforms_error,
            balances=[PlatformBalanceResponse(**b.to_dict()) for b in summary.balances],
            generated_at=summary.generated_at.isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/platforms")
async def list_platforms():
    """List all configured platforms."""
    try:
        config = load_config()
        platforms = []
        for name, pconfig in config.platforms.items():
            platforms.append({
                "name": name,
                "enabled": pconfig.enabled,
                "method": pconfig.method,
                "has_api_key": bool(pconfig.api_key),
            })
        return {"platforms": platforms}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/platform/{platform_name}", response_model=PlatformBalanceResponse)
async def get_platform_balance(platform_name: str, refresh: bool = False):
    """
    Get balance for a specific platform.
    
    - **platform_name**: Platform identifier
    - **refresh**: If true, fetch fresh data from API
    """
    try:
        manager = get_manager()
        storage = get_storage()
        
        if refresh:
            balance = manager.check_balance(platform_name)
            # Save to storage
            storage.save_balances([balance])
        else:
            balances = storage.load_balances()
            balance = next((b for b in balances if b.platform == platform_name), None)
            if not balance:
                balance = manager.check_balance(platform_name)
                storage.save_balances([balance])
        
        return PlatformBalanceResponse(**balance.to_dict())
    except ManualEntryRequired:
        raise HTTPException(
            status_code=400,
            detail=f"Platform '{platform_name}' requires manual entry",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/platform/{platform_name}/check")
async def check_platform_balance(platform_name: str):
    """Trigger balance check for a specific platform."""
    try:
        manager = get_manager()
        balance = manager.check_balance(platform_name)
        
        # Save to storage
        storage = get_storage()
        storage.save_balances([balance])
        
        return PlatformBalanceResponse(**balance.to_dict())
    except ManualEntryRequired:
        raise HTTPException(
            status_code=400,
            detail=f"Platform '{platform_name}' requires manual entry",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/platform/{platform_name}/balance")
async def enter_manual_balance(
    platform_name: str,
    request: ManualEntryRequest,
):
    """Manually enter balance for a platform."""
    try:
        config = load_config()
        
        if platform_name not in config.platforms:
            raise HTTPException(
                status_code=404,
                detail=f"Platform '{platform_name}' not found",
            )
        
        provider = ManualProvider(
            platform_name=platform_name,
            stored_balance=request.balance,
            currency=request.currency,
        )
        
        balance = provider.set_balance(request.balance, request.currency)
        
        # Save to storage
        storage = get_storage()
        storage.save_balances([balance])
        
        return PlatformBalanceResponse(**balance.to_dict())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/history/{platform_name}")
async def get_platform_history(
    platform_name: str,
    days: int = 30,
):
    """Get balance history for a platform."""
    try:
        storage = get_storage()
        balances = storage.load_balances()
        
        # Find platform balance
        balance = next((b for b in balances if b.platform == platform_name), None)
        if not balance:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for platform '{platform_name}'",
            )
        
        # Return history (for now, just return current data with history structure)
        # In a real implementation, you'd store historical data
        return {
            "platform": platform_name,
            "days": days,
            "history": [
                {
                    "date": balance.last_updated.isoformat(),
                    "balance": balance.balance,
                    "status": balance.status.value,
                }
            ],
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/config", response_model=ConfigResponse)
async def get_config():
    """Get current configuration."""
    try:
        config = load_config()
        return ConfigResponse(
            thresholds={
                "warning": config.thresholds.warning,
                "critical": config.thresholds.critical,
            },
            platforms={
                name: pconfig.to_dict()
                for name, pconfig in config.platforms.items()
            },
            storage={
                "type": config.storage.type,
                "path": config.storage.path,
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/config/thresholds")
async def update_thresholds(request: ConfigUpdateRequest):
    """Update threshold configuration."""
    try:
        config = load_config()
        
        if request.warning_threshold is not None:
            config.thresholds.warning = request.warning_threshold
        if request.critical_threshold is not None:
            config.thresholds.critical = request.critical_threshold
        
        save_config(config)
        
        return ConfigResponse(
            thresholds={
                "warning": config.thresholds.warning,
                "critical": config.thresholds.critical,
            },
            platforms={},
            storage={},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi import APIRouter, HTTPException, Query, Body
from loguru import logger
from typing import Dict, Any, List
from pydantic import BaseModel

from core.controller import HVACController
from core.schemas import ModeUpdate, TemperatureUpdate, ComponentUpdate
from core.constants import MODES, COMPONENT_GROUPS

router = APIRouter()
controller = HVACController()

class ComponentStatusUpdate(BaseModel):
    status: bool

@router.get("/components")
async def get_components() -> Dict[str, Any]:
    """Get status of all components"""
    try:
        state = controller.get_state()
        return {"components": state["components"]}
    except Exception as e:
        logger.error(f"Error getting components: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/components/groups")
async def get_component_groups() -> Dict[str, List[str]]:
    """Get available component groups"""
    return {"groups": list(COMPONENT_GROUPS.keys())}

@router.post("/components/group/{group_id}")
async def update_component_group(
    group_id: str, 
    status: bool = Query(..., description="Component status to set")
) -> Dict[str, Any]:
    """Update all components in a group"""
    try:
        if group_id not in COMPONENT_GROUPS:
            raise ValueError(f"Invalid group ID. Must be one of: {list(COMPONENT_GROUPS.keys())}")
            
        results = []
        for component_id in COMPONENT_GROUPS[group_id]:
            controller.set_component_status(component_id, status)
            results.append({
                "component_id": component_id,
                "status": status
            })
            
        return {
            "status": "success",
            "group": group_id,
            "components": results
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating component group: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/components/{component_id}")
async def update_component(
    component_id: str,
    status: bool = Query(..., description="Component status to set")
) -> Dict[str, Any]:
    """Update individual component status"""
    try:
        controller.set_component_status(component_id, status)
        return {
            "status": "success",
            "component_id": component_id,
            "active": status
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating component: {e}")
        raise HTTPException(status_code=500, detail=str(e))
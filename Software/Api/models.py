from __future__ import annotations
from typing import Annotated, List, Literal
from pydantic import BaseModel, Field, model_validator

class DispenseItem(BaseModel):
    color: Literal["red", "orange", "yellow", "green", "purple"]
    quantity: Annotated[int, Field(ge=1)]

class CandyBotResponse(BaseModel):
    action: Literal["dispense", "reload", "cancel", "nothing"]
    confidence: Annotated[float, Field(ge=0.0, le=1.0)]
    items: List[DispenseItem] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_action_items(self) -> "CandyBotResponse":
        if self.action == "dispense":
            if not self.items:
                raise ValueError("dispense action must include items")
        else:
            if self.items:
                raise ValueError(f"{self.action} action must not include items")
        
        return self

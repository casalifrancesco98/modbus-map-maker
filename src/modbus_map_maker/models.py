from typing import List, Literal, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator

DType = Literal["INT16","UINT16","INT32","UINT32","INT32R","FLOAT32","FLOAT32R"]
RW = Literal["R","W","RW"]
Function = Literal["HR","IR"]
ByteOrder = Literal["big","little"]
WordOrder = Literal["normal","swapped"]

class MapEntry(BaseModel):
    device: str = Field(..., description="Logical device/card identifier, e.g. RTUINV1_1")
    name: str = Field(..., description="Signal name, e.g. INV1_ET")
    address: int = Field(..., ge=0, description="Register start address")
    dtype: DType
    scale: float = 1.0
    offset: float = 0.0
    unit: Optional[str] = None
    rw: Optional[RW] = "R"
    function: Optional[Function] = "HR"
    byte_order: Optional[ByteOrder] = "big"
    word_order: Optional[WordOrder] = "normal"
    description: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("word_order", mode="before")
    @classmethod
    def infer_word_order(cls, v, info):
        # If dtype contains R (reversed), force swapped
        dtype = info.data.get("dtype")
        if dtype in ("INT32R","FLOAT32R"):
            return "swapped"
        return v or "normal"

class MapSpec(BaseModel):
    entries: List[MapEntry]

    def by_device(self) -> Dict[str, List[MapEntry]]:
        d: Dict[str, List[MapEntry]] = {}
        for e in self.entries:
            d.setdefault(e.device, []).append(e)
        return d

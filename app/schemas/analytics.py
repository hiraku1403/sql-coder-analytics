from pydantic import BaseModel



class ProductAnalytics(BaseModel):
    name: str
    total_sold: int
    revenue: float


class RegionAnalytics(BaseModel):
    region: str
    revenue: float
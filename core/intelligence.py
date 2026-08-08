from __future__ import annotations
from core.smart import SmartAssistant
from core.smart_analytics import SmartAnalytics
from core.forecast import ForecastService
from core.profit_monitor import ProfitMonitor

class BusinessIntelligence:
    def __init__(self, db):
        self.smart=SmartAssistant(db); self.analytics=SmartAnalytics(db); self.forecast=ForecastService(db); self.profit=ProfitMonitor(db)

    def insights(self):
        result=self.smart.insights()+self.analytics.insights()+self.profit.alerts()
        for item in self.forecast.product_forecast()[:10]:
            result.append({'type':'forecast','priority':'high','title':'توقع إعادة طلب','message':f"{item['name']}: تغطية {item['days_cover']} يوم، المقترح {item['suggested_order']}"})
        return result

from core.system import SystemBootstrap
from core.forecast import ForecastService


def test_forecast_shapes(tmp_path):
    app=SystemBootstrap(str(tmp_path/'forecast.db')).initialize()
    service=ForecastService(app.db)
    products=service.product_forecast()
    summary=service.sales_summary()
    assert isinstance(products,list)
    assert {'days','average_daily_sales','days'} <= set(summary)

import os
import pytest

pytestmark = pytest.mark.integration

@pytest.mark.skipif(os.getenv("RMU_DB_TESTS") != "1", reason="ต้องเปิด RMU_DB_TESTS=1 จึงทดสอบ DB จริง")
def test_activities_integration_opt_in():
    pytest.skip("ต้องเตรียมฐานข้อมูลกิจกรรมเฉพาะ environment ที่ opt-in")

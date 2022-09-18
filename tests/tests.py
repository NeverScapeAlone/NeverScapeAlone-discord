import os
import sys
import pytest
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.mark.asyncio
async def test_placeholder():
    assert True == True

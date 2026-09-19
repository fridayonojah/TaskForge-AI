import pytest
from unittest.mock import AsyncMock
from domain.entities.travel_request import TravelRequest
from domain.entities.travel_plan import TravelPlan
from domain.value_objects.thread_id import ThreadId
from use_cases.plan_trip_use_case import PlanTripUseCase
from use_cases.exceptions import EmptyQueryError


@pytest.mark.asyncio
async def test_raises_empty_query_error_when_query_blank():
    mock_planner = AsyncMock()
    use_case = PlanTripUseCase(planner=mock_planner)
    request = TravelRequest(query="  ", thread_id=ThreadId.generate())
    with pytest.raises(EmptyQueryError):
        await use_case(request)


@pytest.mark.asyncio
async def test_delegates_to_planner():
    expected_plan = TravelPlan(
        thread_id=ThreadId.generate(),
        answer="Great plan!",
        flight_results="Flight info",
        hotel_results="Hotel info",
        itinerary="Day 1...",
        llm_calls=2,
    )
    mock_planner = AsyncMock()
    mock_planner.plan.return_value = expected_plan
    use_case = PlanTripUseCase(planner=mock_planner)
    request = TravelRequest(query="Japan trip", thread_id=ThreadId.generate())
    result = await use_case(request)
    assert result == expected_plan
    mock_planner.plan.assert_called_once_with(request)

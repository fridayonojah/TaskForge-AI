import pytest
from unittest.mock import AsyncMock
from domain.entities.slide_request import SlideRequest
from domain.entities.slide_deck import SlideDeck
from domain.value_objects.thread_id import ThreadId
from use_cases.create_slides_use_case import CreateSlidesUseCase
from use_cases.exceptions import EmptyQueryError


@pytest.mark.asyncio
async def test_raises_on_empty_topic():
    mock_creator = AsyncMock()
    use_case = CreateSlidesUseCase(creator=mock_creator)
    req = SlideRequest(topic="", num_slides=5, thread_id=ThreadId.generate())
    with pytest.raises(EmptyQueryError):
        await use_case(req)


@pytest.mark.asyncio
async def test_delegates_to_creator():
    tid = ThreadId.generate()
    expected = SlideDeck(topic="AI", slides_markdown="## Slide 1", thread_id=tid)
    mock_creator = AsyncMock()
    mock_creator.create.return_value = expected
    use_case = CreateSlidesUseCase(creator=mock_creator)
    req = SlideRequest(topic="AI", num_slides=5, thread_id=tid)
    result = await use_case(req)
    assert result == expected

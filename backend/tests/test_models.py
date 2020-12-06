from bridgeapp import models

import pydantic
import pytest


def test_call_with_type_bid_must_have_bid_attribute():
    with pytest.raises(pydantic.ValidationError):
        models.Call(type=models.CallType.bid, bid=None)


@pytest.mark.parametrize(
    "type", [models.CallType.pass_, models.CallType.double, models.CallType.redouble]
)
def test_call_that_is_not_bid_must_not_have_bid_attribute(type):
    with pytest.raises(pydantic.ValidationError):
        models.Call(type=type, bid=models.Bid(strain=models.Strain.clubs, level=1))


def test_bid_level_must_be_at_least_one():
    with pytest.raises(pydantic.ValidationError):
        models.Bid(strain=models.Strain.clubs, level=0)


def test_bid_level_must_be_at_most_seven():
    with pytest.raises(pydantic.ValidationError):
        models.Bid(strain=models.Strain.clubs, level=8)


def test_duplicate_result_score_must_be_nonnegative():
    with pytest.raises(pydantic.ValidationError):
        models.DuplicateResult(partnership=models.Partnership.northSouth, score=-1)

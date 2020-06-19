from contextlib import nullcontext as does_not_raise
from math import isclose

import pytest

from lhotse.cut import CutSet, MixedCut
from lhotse.supervision import SupervisionSegment


# Note:
# Definitions for `cut1`, `cut2` and `cut_set` parameters are standard Pytest fixtures located in test/cut/conftest.py


def test_append_cut_duration_and_supervisions(cut1, cut2, cut_set):
    appended_cut = cut1.append(cut2).with_cut_set(cut_set)

    assert isinstance(appended_cut, MixedCut)
    assert appended_cut.duration == 20.0
    assert appended_cut.supervisions == [
        SupervisionSegment(id='sup-1', recording_id='irrelevant', start=0.5, duration=6.0),
        SupervisionSegment(id='sup-2', recording_id='irrelevant', start=7.0, duration=2.0),
        SupervisionSegment(id='sup-3', recording_id='irrelevant', start=13.0, duration=2.5)
    ]


@pytest.mark.parametrize(
    ['offset', 'expected_duration', 'exception_expectation'],
    [
        (0, 10.0, does_not_raise()),
        (1, 11.0, does_not_raise()),
        (5, 15.0, does_not_raise()),
        (10, 20.0, does_not_raise()),
        (100, 'irrelevant', pytest.raises(ValueError))
    ]
)
def test_overlay_cut_duration_and_supervisions(offset, expected_duration, exception_expectation, cut1, cut2, cut_set):
    with exception_expectation:
        mixed_cut = cut1.overlay(cut2, offset_other_by=offset).with_cut_set(cut_set)

        assert isinstance(mixed_cut, MixedCut)
        assert mixed_cut.duration == expected_duration
        assert mixed_cut.supervisions == [
            SupervisionSegment(id='sup-1', recording_id='irrelevant', start=0.5, duration=6.0),
            SupervisionSegment(id='sup-2', recording_id='irrelevant', start=7.0, duration=2.0),
            SupervisionSegment(id='sup-3', recording_id='irrelevant', start=3.0 + offset, duration=2.5)
        ]


def test_mixed_cut_load_features():
    cut_set = CutSet.from_yaml('test/fixtures/mix_cut_test/overlayed_cut_manifest.yml')
    mixed_cut = cut_set.cuts['mixed-cut-id']
    ingredient_cut2 = cut_set.cuts[mixed_cut.tracks[1].cut_id]

    feats = mixed_cut.with_cut_set(cut_set).load_features()
    expected_duration = mixed_cut.tracks[1].offset + ingredient_cut2.duration
    assert isclose(expected_duration, 13.595)
    expected_frame_count = 1360
    assert feats.shape[0] == expected_frame_count

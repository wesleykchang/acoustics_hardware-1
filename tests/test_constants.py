from picoscope import constants


def test_auto_enum():
    """We want the the auto method to be zero-based
    (as opposed to enum's default 1-based).
    """

    up_enum = constants.SweepType['UP'].value

    assert isinstance(up_enum, int)
    assert up_enum == 0
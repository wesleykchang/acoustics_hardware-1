from picoscope import parameters


def test_auto_enum():
    """We want the the auto method to be zero-based
    (as opposed to enum's default 1-based).
    """

    up_enum = parameters.SweepType['UP'].value

    assert isinstance(up_enum, int)
    assert up_enum == 0


def test_channel():
    channel_A_enum = parameters.Channel.A.value

    assert channel_A_enum == 0


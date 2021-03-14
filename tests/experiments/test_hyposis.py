import hypothesis as hs
import hypothesis.strategies as st


def division(x, y):
    return float(x) / float(y)


@hs.given(x=st.integers())
def test_div(x: int):
    try:
        assert division(x * 2, x) == 2.0
    except Exception as e:
        if isinstance(e, ZeroDivisionError) and x == 0:
            pass
        else:
            raise

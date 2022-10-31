from cstruct import CEnum

class Dummy(CEnum):
  __enum__ = """
    A,
    B,
    C = 2,
    D = 5 + 7,
    E = 2
  """

def test_dummy():
  assert Dummy.A == 0
  assert Dummy.B == 1
  assert Dummy.C == 2
  assert Dummy.D == 12
  assert Dummy.E == 2
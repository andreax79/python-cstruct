#!/usr/bin/env python

import pickle
import cstruct


class Position(cstruct.CStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __def__ = """
        struct {
            unsigned char head;
            unsigned char sector;
            unsigned char cyl;
        }
    """


class MemPosition(cstruct.MemCStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __def__ = """
        struct {
            unsigned char head;
            unsigned char sector;
            unsigned char cyl;
        }
    """


def test_pickle():
    # pickle an object
    original_pos = Position(head=254, sector=63, cyl=134)
    pickled_bytes = pickle.dumps(original_pos)

    # reconstitute a pickled object
    reconstituted_pos = pickle.loads(pickled_bytes)

    assert reconstituted_pos.head == original_pos.head
    assert reconstituted_pos.sector == original_pos.sector
    assert reconstituted_pos.cyl == original_pos.cyl


def test_mem_pickle():
    # pickle an object
    original_pos = MemPosition(head=254, sector=63, cyl=134)
    pickled_bytes = pickle.dumps(original_pos)

    # reconstitute a pickled object
    reconstituted_pos = pickle.loads(pickled_bytes)

    assert reconstituted_pos.head == original_pos.head
    assert reconstituted_pos.sector == original_pos.sector
    assert reconstituted_pos.cyl == original_pos.cyl

# -*- coding: utf-8 -*-
"""-- choices fields should be defined here. --"""


class choice(object):
    @classmethod
    def get_val(cls, key):
        a = cls.__dict__.iteritems()
        maint = None
        for k, v in a:
            if k.lower().find('choices') >= 0:
                maint = v

        for j, h in maint:
            if h.lower().find(key.lower())>=0:
                return j
        return None

class buildingclass(choice):
    BUILDINGCLASS = (
        (1, "w1"),
        (2, "w2"),
        (3, "s1"),
        (4, "s2"),
        (5, "s3"),
        (6, "s4"),
        (7, "s5"),
        (8, "c1"),
        (9, "c2"),
        (10, "c3"),
        (11, "pc1"),
        (12, "pc2"),
        (13, "rm1"),
        (14, "rm2"),
        (15, "urm"),
        )
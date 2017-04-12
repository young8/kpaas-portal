# -*- coding: utf-8 -*-
"""
    kpaas.database
    ~~~~~~~~~~~~~~~
    
    Author: Y.Z.Y
    
"""

from datetime import datetime
from kpaas_portal.extensions import db


class CRUDMixin(object):
    def __repr__(self):
        return "<{}>".format(self.__class__.__name__)

    def to_dict(self, *columns):
        dct = {}
        for col in columns:
            value = getattr(self, col)
            if isinstance(value, datetime.datetime):
                value = value.strftime('%Y-%m-%d %H:%M:%S')
            dct[col] = value

        return dct

    def save(self):
        db.session.add(self)
        db.session.commit()

        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()

        return self
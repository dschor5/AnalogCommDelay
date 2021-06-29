#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exceptions

@author: dario
"""


class LockError(Exception):
    """Raised when there is a timeout after failing to obtain a
    the :class:`LockTimeout`."""
    pass


class SocketSendEmptyMessage(Exception):
    """Raised when trying to send an empty packet."""
    pass


class SocketSendPktInvalidLength(Exception):
    """Raised when trying to send a packet with an invalid length."""
    pass

class SocketRecvEmptyMessage(Exception):
    """Raised when trying to receive an empty packet."""
    pass


class SocketRecvPktInvalidLength(Exception):
    """Raised when trying to receive a packet with an invalid length."""
    pass

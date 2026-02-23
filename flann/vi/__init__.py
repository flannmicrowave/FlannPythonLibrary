"""
.. module:: flann.vi
==============================================
virtual instruments (:mod:`flann.vi`)
==============================================

Provides a class to interact with Flann's programmable instruments
using either serial or ethernet via socket

Flann Instument Classes
-----------------------

====== ========== ======
Series Device     Module
====== ========== ======
024    Attenuator `flann.vi.attenuator.flann024`
624    Attenuator `flann.vi.attenuator.flann624`
625    Attenuator `flann.vi.attenuator.flann625`
337    Switch Box `flann.vi.switch.flann337`
338    Switch Box `flann.vi.switch.flann338`
====== ========== ======

Flann Instrument Base Class
---------------------------
All Flann's instruments are built upon the :class:'FlannProgrammable class. 
This class provides the basic communication methods to interact with the 
instruments and should never be used directly. Instead, use the specific 
instrument classes provided in the submodules.'

"""
from .flann_programmable import FlannProgrammable
from . import attenuator, switch

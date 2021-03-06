# -*- coding: utf-8 -*-
"""
The ImageFormationType definition.
"""

from typing import List
import logging

import numpy

from .base import Serializable, DEFAULT_STRICT, \
    _StringDescriptor, _StringEnumDescriptor, _FloatDescriptor, _IntegerDescriptor, \
    _BooleanDescriptor, _ComplexDescriptor, _DateTimeDescriptor, _IntegerListDescriptor, \
    _SerializableDescriptor, _SerializableListDescriptor, _ParametersDescriptor, ParametersCollection


__classification__ = "UNCLASSIFIED"
__author__ = "Thomas McCullough"


class RcvChanProcType(Serializable):
    """The Received Processed Channels."""
    _fields = ('NumChanProc', 'PRFScaleFactor', 'ChanIndices')
    _required = ('NumChanProc', 'ChanIndices')
    _collections_tags = {
        'ChanIndices': {'array': False, 'child_tag': 'ChanIndex'}}
    _numeric_format = {'PRFScaleFactor': '0.16G'}
    # descriptors
    NumChanProc = _IntegerDescriptor(
        'NumChanProc', _required, strict=DEFAULT_STRICT,
        docstring='Number of receive data channels processed to form the image.')  # type: int
    PRFScaleFactor = _FloatDescriptor(
        'PRFScaleFactor', _required, strict=DEFAULT_STRICT,
        docstring='Factor indicating the ratio of the effective PRF to the actual PRF.')  # type: float
    ChanIndices = _IntegerListDescriptor(
        'ChanIndices', _collections_tags, _required, strict=DEFAULT_STRICT,
        docstring='Index of a data channel that was processed.')  # type: List[int]

    def __init__(self, NumChanProc=None, PRFScaleFactor=None, ChanIndices=None, **kwargs):
        """

        Parameters
        ----------
        NumChanProc : int
        PRFScaleFactor : float
        ChanIndices : List[int]
        kwargs : dict
        """

        if '_xml_ns' in kwargs:
            self._xml_ns = kwargs['_xml_ns']
        self.NumChanProc = NumChanProc
        self.PRFScaleFactor = PRFScaleFactor
        self.ChanIndices = ChanIndices
        super(RcvChanProcType, self).__init__(**kwargs)


class TxFrequencyProcType(Serializable):
    """The transmit frequency range."""
    _fields = ('MinProc', 'MaxProc')
    _required = _fields
    _numeric_format = {'MinProc': '0.16G', 'MaxProc': '0.16G'}
    # descriptors
    MinProc = _FloatDescriptor(
        'MinProc', _required, strict=DEFAULT_STRICT,
        docstring='The minimum transmit frequency processed to form the image, in Hz.')  # type: float
    MaxProc = _FloatDescriptor(
        'MaxProc', _required, strict=DEFAULT_STRICT,
        docstring='The maximum transmit frequency processed to form the image, in Hz.')  # type: float

    def __init__(self, MinProc=None, MaxProc=None, **kwargs):
        """

        Parameters
        ----------
        MinProc : float
        MaxProc : float
        kwargs : dict
        """

        if '_xml_ns' in kwargs:
            self._xml_ns = kwargs['_xml_ns']
        self.MinProc, self.MaxProc = MinProc, MaxProc
        super(TxFrequencyProcType, self).__init__(**kwargs)

    def _apply_reference_frequency(self, reference_frequency):
        if self.MinProc is not None:
            self.MinProc += reference_frequency
        if self.MaxProc is not None:
            self.MaxProc += reference_frequency

    def _basic_validity_check(self):
        condition = super(TxFrequencyProcType, self)._basic_validity_check()
        if self.MinProc is not None and self.MaxProc is not None and self.MaxProc < self.MinProc:
            logging.error(
                'Invalid frequency bounds MinProc ({}) > MaxProc ({})'.format(self.MinProc, self.MaxProc))
            condition = False
        return condition


class ProcessingType(Serializable):
    """The transmit frequency range"""
    _fields = ('Type', 'Applied', 'Parameters')
    _required = ('Type', 'Applied')
    _collections_tags = {'Parameters': {'array': False, 'child_tag': 'Parameter'}}
    # descriptors
    Type = _StringDescriptor(
        'Type', _required, strict=DEFAULT_STRICT,
        docstring='The processing type identifier.')  # type: str
    Applied = _BooleanDescriptor(
        'Applied', _required, strict=DEFAULT_STRICT,
        docstring='Indicates whether the given processing type has been applied.')  # type: bool
    Parameters = _ParametersDescriptor(
        'Parameters', _collections_tags, _required, strict=DEFAULT_STRICT,
        docstring='The parameters collection.')  # type: ParametersCollection

    def __init__(self, Type=None, Applied=None, Parameters=None, **kwargs):
        """

        Parameters
        ----------
        Type : str
        Applied : bool
        Parameters : ParametersCollection|dict
        kwargs : dict
        """

        if '_xml_ns' in kwargs:
            self._xml_ns = kwargs['_xml_ns']
        self.Type = Type
        self.Applied = Applied
        self.Parameters = Parameters
        super(ProcessingType, self).__init__(**kwargs)


class DistortionType(Serializable):
    """Distortion"""
    _fields = (
        'CalibrationDate', 'A', 'F1', 'F2', 'Q1', 'Q2', 'Q3', 'Q4',
        'GainErrorA', 'GainErrorF1', 'GainErrorF2', 'PhaseErrorF1', 'PhaseErrorF2')
    _required = ('A', 'F1', 'Q1', 'Q2', 'F2', 'Q3', 'Q4')
    _numeric_format = {key : '0.16G' for key in _fields[1:]}
    # descriptors
    CalibrationDate = _DateTimeDescriptor(
        'CalibrationDate', _required, strict=DEFAULT_STRICT,
        docstring='The calibration date.')
    A = _FloatDescriptor(
        'A', _required, strict=DEFAULT_STRICT,
        docstring='Absolute amplitude scale factor.')  # type: float
    # receive distorion matrix
    F1 = _ComplexDescriptor(
        'F1', _required, strict=DEFAULT_STRICT,
        docstring='Receive distortion element (2,2).')  # type: complex
    Q1 = _ComplexDescriptor(
        'Q1', _required, strict=DEFAULT_STRICT,
        docstring='Receive distortion element (1,2).')  # type: complex
    Q2 = _ComplexDescriptor(
        'Q2', _required, strict=DEFAULT_STRICT,
        docstring='Receive distortion element (2,1).')  # type: complex
    # transmit distortion matrix
    F2 = _ComplexDescriptor(
        'F2', _required, strict=DEFAULT_STRICT,
        docstring='Transmit distortion element (2,2).')  # type: complex
    Q3 = _ComplexDescriptor(
        'Q3', _required, strict=DEFAULT_STRICT,
        docstring='Transmit distortion element (2,1).')  # type: complex
    Q4 = _ComplexDescriptor(
        'Q4', _required, strict=DEFAULT_STRICT,
        docstring='Transmit distortion element (1,2).')  # type: complex
    # gain estimation error
    GainErrorA = _FloatDescriptor(
        'GainErrorA', _required, strict=DEFAULT_STRICT,
        docstring='Gain estimation error standard deviation (in dB) for parameter A.')  # type: float
    GainErrorF1 = _FloatDescriptor(
        'GainErrorF1', _required, strict=DEFAULT_STRICT,
        docstring='Gain estimation error standard deviation (in dB) for parameter F1.')  # type: float
    GainErrorF2 = _FloatDescriptor(
        'GainErrorF2', _required, strict=DEFAULT_STRICT,
        docstring='Gain estimation error standard deviation (in dB) for parameter F2.')  # type: float
    PhaseErrorF1 = _FloatDescriptor(
        'PhaseErrorF1', _required, strict=DEFAULT_STRICT,
        docstring='Phase estimation error standard deviation (in dB) for parameter F1.')  # type: float
    PhaseErrorF2 = _FloatDescriptor(
        'PhaseErrorF2', _required, strict=DEFAULT_STRICT,
        docstring='Phase estimation error standard deviation (in dB) for parameter F2.')  # type: float

    def __init__(self, CalibrationDate=None, A=None,
                 F1=None, Q1=None, Q2=None, F2=None, Q3=None, Q4=None,
                 GainErrorA=None, GainErrorF1=None, GainErrorF2=None,
                 PhaseErrorF1=None, PhaseErrorF2=None, **kwargs):
        """

        Parameters
        ----------
        CalibrationDate : numpy.datetime64|datetime|date|str
        A : float
        F1 : complex
        Q1 : complex
        Q2 : complex
        F2 : complex
        Q3 : complex
        Q4 : complex
        GainErrorA : float
        GainErrorF1 : float
        GainErrorF2 : float
        PhaseErrorF1 : float
        PhaseErrorF2 : float
        kwargs : dict
        """

        if '_xml_ns' in kwargs:
            self._xml_ns = kwargs['_xml_ns']
        self.CalibrationDate = CalibrationDate
        self.A = A
        self.F1, self.Q1, self.Q2 = F1, Q1, Q2
        self.F2, self.Q3, self.Q4 = F2, Q3, Q4
        self.GainErrorA = GainErrorA
        self.GainErrorF1, self.GainErrorF2 = GainErrorF1, GainErrorF2
        self.PhaseErrorF1, self.PhaseErrorF2 = PhaseErrorF1, PhaseErrorF2
        super(DistortionType, self).__init__(**kwargs)


class PolarizationCalibrationType(Serializable):
    """The polarization calibration"""
    _fields = ('DistortCorrectApplied', 'Distortion')
    _required = _fields
    # descriptors
    DistortCorrectApplied = _BooleanDescriptor(
        'DistortCorrectApplied', _required, strict=DEFAULT_STRICT,
        docstring='Indicates whether the polarization calibration has been applied.')  # type: bool
    Distortion = _SerializableDescriptor(
        'Distortion', DistortionType, _required, strict=DEFAULT_STRICT,
        docstring='The distortion parameters.')  # type: DistortionType

    def __init__(self, DistortCorrectApplied=None, Distortion=None, **kwargs):
        """

        Parameters
        ----------
        DistortCorrectApplied : bool
        Distortion : DistortionType
        kwargs : dict
        """

        if '_xml_ns' in kwargs:
            self._xml_ns = kwargs['_xml_ns']
        self.DistortCorrectApplied = DistortCorrectApplied
        self.Distortion = Distortion
        super(PolarizationCalibrationType, self).__init__(**kwargs)


class ImageFormationType(Serializable):
    """The image formation process parameters."""
    _fields = (
        'RcvChanProc', 'TxRcvPolarizationProc', 'TStartProc', 'TEndProc', 'TxFrequencyProc', 'SegmentIdentifier',
        'ImageFormAlgo', 'STBeamComp', 'ImageBeamComp', 'AzAutofocus', 'RgAutofocus', 'Processings',
        'PolarizationCalibration')
    _required = (
        'RcvChanProc', 'TxRcvPolarizationProc', 'TStartProc', 'TEndProc', 'TxFrequencyProc',
        'ImageFormAlgo', 'STBeamComp', 'ImageBeamComp', 'AzAutofocus', 'RgAutofocus')
    _collections_tags = {'Processings': {'array': False, 'child_tag': 'Processing'}}
    _numeric_format = {'TStartProc': '0.16G', 'EndProc': '0.16G'}
    # class variables
    _DUAL_POLARIZATION_VALUES = (
        'V:V', 'V:H', 'V:RHC', 'V:LHC',
        'H:V', 'H:H', 'H:RHC', 'H:LHC',
        'RHC:V', 'RHC:H', 'RHC:RHC', 'RHC:LHC',
        'LHC:V', 'LHC:H', 'LHC:RHC', 'LHC:LHC',
        'OTHER', 'UNKNOWN')
    _IMG_FORM_ALGO_VALUES = ('PFA', 'RMA', 'RGAZCOMP', 'OTHER')
    _ST_BEAM_COMP_VALUES = ('NO', 'GLOBAL', 'SV')
    _IMG_BEAM_COMP_VALUES = ('NO', 'SV')
    _AZ_AUTOFOCUS_VALUES = _ST_BEAM_COMP_VALUES
    _RG_AUTOFOCUS_VALUES = _ST_BEAM_COMP_VALUES
    # descriptors
    RcvChanProc = _SerializableDescriptor(
        'RcvChanProc', RcvChanProcType, _required, strict=DEFAULT_STRICT,
        docstring='The received processed channels.')  # type: RcvChanProcType
    TxRcvPolarizationProc = _StringEnumDescriptor(
        'TxRcvPolarizationProc', _DUAL_POLARIZATION_VALUES, _required, strict=DEFAULT_STRICT,
        docstring='The combined transmit/receive polarization processed to form the image.')  # type: str
    TStartProc = _FloatDescriptor(
        'TStartProc', _required, strict=DEFAULT_STRICT,
        docstring='Earliest slow time value for data processed to form the image from `CollectionStart`.')  # type: float
    TEndProc = _FloatDescriptor(
        'TEndProc', _required, strict=DEFAULT_STRICT,
        docstring='Latest slow time value for data processed to form the image from `CollectionStart`.')  # type: float
    TxFrequencyProc = _SerializableDescriptor(
        'TxFrequencyProc', TxFrequencyProcType, _required, strict=DEFAULT_STRICT,
        docstring='The range of transmit frequency processed to form the image.')  # type: TxFrequencyProcType
    SegmentIdentifier = _StringDescriptor(
        'SegmentIdentifier', _required, strict=DEFAULT_STRICT,
        docstring='Identifier that describes the image that was processed. '
                  'Must be included when `SICD.RadarCollection.Area.Plane.SegmentList` is included.')  # type: str
    ImageFormAlgo = _StringEnumDescriptor(
        'ImageFormAlgo', _IMG_FORM_ALGO_VALUES, _required, strict=DEFAULT_STRICT,
        docstring="""
        The image formation algorithm used:

        * `PFA` - Polar Format Algorithm

        * `RMA` - Range Migration (Omega-K, Chirp Scaling, Range-Doppler)

        * `RGAZCOMP` - Simple range, Doppler compression.

        """)  # type: str
    STBeamComp = _StringEnumDescriptor(
        'STBeamComp', _ST_BEAM_COMP_VALUES, _required, strict=DEFAULT_STRICT,
        docstring="""
        Indicates if slow time beam shape compensation has been applied.

        * `NO` - No ST beam shape compensation.

        * `GLOBAL` - Global ST beam shape compensation applied.

        * `SV` - Spatially variant beam shape compensation applied.

        """)  # type: str
    ImageBeamComp = _StringEnumDescriptor(
        'ImageBeamComp', _IMG_BEAM_COMP_VALUES, _required, strict=DEFAULT_STRICT,
        docstring="""
        Indicates if image domain beam shape compensation has been applied.

        * `NO` - No image domain beam shape compensation.

        * `SV` - Spatially variant image domain beam shape compensation applied.

        """)  # type: str
    AzAutofocus = _StringEnumDescriptor(
        'AzAutofocus', _AZ_AUTOFOCUS_VALUES, _required, strict=DEFAULT_STRICT,
        docstring='Indicates if azimuth autofocus correction has been applied, with similar '
                  'interpretation as `STBeamComp`.')  # type: str
    RgAutofocus = _StringEnumDescriptor(
        'RgAutofocus', _RG_AUTOFOCUS_VALUES, _required, strict=DEFAULT_STRICT,
        docstring='Indicates if range autofocus correction has been applied, with similar '
                  'interpretation as `STBeamComp`.')  # type: str
    Processings = _SerializableListDescriptor(
        'Processings', ProcessingType, _collections_tags, _required, strict=DEFAULT_STRICT,
        docstring='Parameters to describe types of specific processing that may have been applied '
                  'such as additional compensations.')  # type: List[ProcessingType]
    PolarizationCalibration = _SerializableDescriptor(
        'PolarizationCalibration', PolarizationCalibrationType, _required, strict=DEFAULT_STRICT,
        docstring='The polarization calibration details.')  # type: PolarizationCalibrationType

    def __init__(self, RcvChanProc=None, TxRcvPolarizationProc=None,
                 TStartProc=None, TEndProc=None,
                 TxFrequencyProc=None, SegmentIdentifier=None, ImageFormAlgo=None,
                 STBeamComp=None, ImageBeamComp=None, AzAutofocus=None, RgAutofocus=None,
                 Processings=None, PolarizationCalibration=None, **kwargs):
        """

        Parameters
        ----------
        RcvChanProc : RcvChanProcType
        TxRcvPolarizationProc : str
        TStartProc : float
        TEndProc : float
        TxFrequencyProc : TxFrequencyProcType
        SegmentIdentifier : str
        ImageFormAlgo : str
        STBeamComp : str
        ImageBeamComp :str
        AzAutofocus : str
        RgAutofocus : str
        Processings : List[ProcessingType]
        PolarizationCalibration : PolarizationCalibrationType
        kwargs : dict
        """

        if '_xml_ns' in kwargs:
            self._xml_ns = kwargs['_xml_ns']
        self.RcvChanProc = RcvChanProc
        self.TxRcvPolarizationProc = TxRcvPolarizationProc
        self.TStartProc, self.TEndProc = TStartProc, TEndProc
        if isinstance(TxFrequencyProc, (numpy.ndarray, list, tuple)) and len(TxFrequencyProc) >= 2:
            self.TxFrequencyProc = TxFrequencyProcType(MinProc=TxFrequencyProc[0], MaxProc=TxFrequencyProc[1])
        else:
            self.TxFrequencyProc = TxFrequencyProc
        self.SegmentIdentifier = SegmentIdentifier
        self.ImageFormAlgo = ImageFormAlgo
        self.STBeamComp, self.ImageBeamComp = STBeamComp, ImageBeamComp
        self.AzAutofocus, self.RgAutofocus = AzAutofocus, RgAutofocus
        self.Processings = Processings
        self.PolarizationCalibration = PolarizationCalibration
        super(ImageFormationType, self).__init__(**kwargs)

    def _derive_tx_frequency_proc(self, RadarCollection):
        """
        Populate a default for processed frequency values, based on the assumption that the entire
        transmitted bandwidth was processed. This is expected to be called by SICD parent.

        Parameters
        ----------
        RadarCollection : sarpy.io.complex.sicd_elements.RadarCollection.RadarCollectionType

        Returns
        -------
        None
        """

        if RadarCollection is not None and RadarCollection.TxFrequency is not None and \
                RadarCollection.TxFrequency.Min is not None and RadarCollection.TxFrequency.Max is not None:
            # this is based on the assumption that the entire transmitted bandwidth was processed.
            if self.TxFrequencyProc is not None:
                self.TxFrequencyProc = TxFrequencyProcType(
                    MinProc=RadarCollection.TxFrequency.Min, MaxProc=RadarCollection.TxFrequency.Max)
                # how would it make sense to set only one end?
            elif self.TxFrequencyProc.MinProc is None:
                self.TxFrequencyProc.MinProc = RadarCollection.TxFrequency.Min
            elif self.TxFrequencyProc.MaxProc is None:
                self.TxFrequencyProc.MaxProc = RadarCollection.TxFrequency.Max

    def _apply_reference_frequency(self, reference_frequency):
        """
        If the reference frequency is used, adjust the necessary fields accordingly.
        Expected to be called by SICD parent.

        Parameters
        ----------
        reference_frequency : float
            The reference frequency.

        Returns
        -------
        None
        """

        if self.TxFrequencyProc is not None:
            # noinspection PyProtectedMember
            self.TxFrequencyProc._apply_reference_frequency(reference_frequency)

    def _basic_validity_check(self):
        condition = super(ImageFormationType, self)._basic_validity_check()
        if self.TStartProc is not None and self.TEndProc is not None and self.TEndProc < self.TStartProc:
            logging.error(
                'Invalid time processing bounds '
                'TStartProc ({}) > TEndProc ({})'.format(self.TStartProc, self.TEndProc))
            condition = False
        return condition

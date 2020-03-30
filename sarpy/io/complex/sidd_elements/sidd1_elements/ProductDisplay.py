# -*- coding: utf-8 -*-
"""
The ProductDisplayType definition for SIDD 1.0.
"""
import logging
from typing import Union
from collections import OrderedDict

import numpy

from ..base import DEFAULT_STRICT
# noinspection PyProtectedMember
from ...sicd_elements.base import Serializable, Arrayable, _SerializableDescriptor, \
    _IntegerDescriptor, _FloatDescriptor, _StringDescriptor, _StringEnumDescriptor, \
    _ParametersDescriptor, ParametersCollection, \
    int_func, _create_new_node, _create_text_node, _get_node_value


__classification__ = "UNCLASSIFIED"
__author__ = "Thomas McCullough"


class ColorDisplayRemapType(Serializable, Arrayable):
    """
    LUT-base remap indicating that the color display is done through index-based color.
    """

    __slots__ = ('_remap_lut', )

    def __init__(self, RemapLUT=None, **kwargs):
        """

        Parameters
        ----------
        RemapLUT : numpy.ndarray|list|tuple
        kwargs
        """

        self._remap_lut = None
        if '_xml_ns' in kwargs:
            self._xml_ns = kwargs['_xml_ns']
        self.RemapLUT = RemapLUT
        super(ColorDisplayRemapType, self).__init__(**kwargs)

    @property
    def RemapLUT(self):
        """
        numpy.ndarray: the two dimensional (:math:`N \times 3`) look-up table, where the dtype must be
        `uint8` or `uint16`. The first dimension should correspond to entries (i.e. size of the lookup table), and the
        second dimension must have size 3 and corresponds to `RGB` bands.
        """

        return self._remap_lut

    @RemapLUT.setter
    def RemapLUT(self, value):
        if value is None:
            self._remap_lut = None
            return
        if isinstance(value, (tuple, list)):
            value = numpy.array(value, dtype=numpy.uint8)
        if not isinstance(value, numpy.ndarray) or value.dtype.name not in ('uint8', 'uint16'):
            raise ValueError(
                'RemapLUT for class ColorDisplayRemapType must be a numpy.ndarray of dtype uint8 or uint16.')
        if value.ndim != 2 and value.shape[1] != 3:
            raise ValueError('RemapLUT for class ColorDisplayRemapType must be an N x 3 array.')
        self._remap_lut = value

    @property
    def size(self):
        """
        int: the size of the lookup table
        """
        if self._remap_lut is None:
            return 0
        else:
            return self._remap_lut.shape[0]

    def __len__(self):
        if self._remap_lut is None:
            return 0
        return self._remap_lut.shape[0]

    def __getitem__(self, item):
        return self._remap_lut[item]

    @classmethod
    def from_array(cls, array):
        """
        Create from the lookup table array.

        Parameters
        ----------
        array: numpy.ndarray|list|tuple
            Must be two-dimensional. If not a numpy.ndarray, this will be naively
            interpreted as `uint8`.

        Returns
        -------
        LUTInfoType
        """

        return cls(RemapLUT=array)

    def get_array(self, dtype=numpy.uint8):
        """
        Gets **a copy** of the coefficent array of specified data type.

        Parameters
        ----------
        dtype : numpy.dtype
            numpy data type of the return

        Returns
        -------
        numpy.ndarray
            the lookup table array
        """

        return numpy.array(self._remap_lut, dtype=dtype)

    @classmethod
    def from_node(cls, node, xml_ns, kwargs=None):
        """For XML deserialization.

        Parameters
        ----------
        node : ElementTree.Element
            dom element for serialized class instance
        xml_ns : dict
            The xml namespace dictionary.
        kwargs : None|dict
            `None` or dictionary of previously serialized attributes. For use in inheritance call, when certain
            attributes require specific deserialization.

        Returns
        -------
        LUTInfoType
            corresponding class instance
        """

        lut_node = node.find('RemapLUT') if xml_ns is None else node.find('default:RemapLUT', xml_ns)
        if lut_node is not None:
            dim1 = int_func(lut_node.attrib['size'])
            dim2 = 3
            arr = numpy.zeros((dim1, dim2), dtype=numpy.uint16)
            entries = _get_node_value(lut_node).split()
            i = 0
            for entry in entries:
                if len(entry) == 0:
                    continue
                sentry = entry.split(',')
                if len(sentry) != 3:
                    logging.error('Parsing RemapLUT is likely compromised. Got entry {}, '
                                  'which we are skipping.'.format(entry))
                    continue
                arr[i, :] = [int(el) for el in entry]
                i += 1
            if numpy.max(arr) < 256:
                arr = numpy.cast[numpy.uint8](arr)
            return cls(RemapLUT=arr)
        return cls()

    def to_node(self, doc, tag, parent=None, check_validity=False, strict=DEFAULT_STRICT, exclude=()):
        if parent is None:
            parent = doc.getroot()
        node = _create_new_node(doc, tag, parent=parent)

        if self._remap_lut is not None:
            value = ' '.join('{0:d},{1:d},{2:d}'.format(*entry) for entry in self._remap_lut)
            entry = _create_text_node(doc, 'RemapLUT', value, parent=node)
            entry.attrib['size'] = str(self.size)
        return node

    def to_dict(self,  check_validity=False, strict=DEFAULT_STRICT, exclude=()):
        out = OrderedDict()
        if self.RemapLUT is not None:
            out['RemapLUT'] = self.RemapLUT.tolist()
        return out


class MonochromeDisplayRemapType(Serializable):
    """
    This remap works by taking the input space and using the LUT to map it to a log space (for 8-bit only).

    From the log space the C0 and Ch fields are applied to get to display-ready density space. The density
    should then be rendered by the TTC and monitor comp. This means that the default DRA should not apply
    anything besides the clip points. If a different contrast/brightness is applied it should be done through
    modification of the clip points via DRA.
    """

    _fields = ('RemapType', 'RemapParameters')
    _required = ('RemapType', )
    _collections_tags = {'RemapParameters': {'array': False, 'child_tag': 'RemapParameter'}}
    # Descriptor
    RemapType = _StringDescriptor(
        'RemapType', _required, strict=DEFAULT_STRICT,
        docstring='')  # type: str
    RemapParameters = _ParametersDescriptor(
        'RemapParameters', _collections_tags, required=_required, strict=DEFAULT_STRICT,
        docstring='Textual remap parameter. Filled based upon remap type (for informational purposes only).  '
                  'For example, if the data is linlog encoded a RemapParameter could be used to describe any '
                  'amplitude scaling that was performed prior to linlog encoding '
                  'the data.')  # type: ParametersCollection

    def __init__(self, RemapType=None, RemapLUT=None, RemapParameters=None, **kwargs):
        """

        Parameters
        ----------
        RemapType : str
        RemapLUT : None|numpy.ndarray
        RemapParameters : None|ParametersCollection|dict
        kwargs
        """

        self._remap_lut = None
        if '_xml_ns' in kwargs:
            self._xml_ns = kwargs['_xml_ns']
        self.RemapType = RemapType
        self.RemapLUT = RemapLUT
        self.RemapParameters = RemapParameters
        super(MonochromeDisplayRemapType, self).__init__(**kwargs)

    @property
    def RemapLUT(self):
        """
        numpy.ndarray: the one dimensional Lookup table for remap to log amplitude for display,
        where the dtype must be `uint8`. Used during the "Product Generation Option" portion of the SIPS
        display chain. Required for 8-bit data, and not to be used for 16-bit data.
        """

        return self._remap_lut

    @RemapLUT.setter
    def RemapLUT(self, value):
        if value is None:
            self._remap_lut = None
            return
        if isinstance(value, (tuple, list)):
            value = numpy.array(value, dtype=numpy.uint8)
        if not isinstance(value, numpy.ndarray) or value.dtype.name != 'uint8':
            raise ValueError(
                'RemapLUT for class MonochromeDisplayRemapType must be a numpy.ndarray of dtype uint8.')
        if value.ndim != 1:
            raise ValueError('RemapLUT for class MonochromeDisplayRemapType must be a one-dimensional array.')
        self._remap_lut = value

    @classmethod
    def from_node(cls, node, xml_ns, kwargs=None):
        """For XML deserialization.

        Parameters
        ----------
        node : ElementTree.Element
            dom element for serialized class instance
        xml_ns : dict
            The xml namespace dictionary.
        kwargs : None|dict
            `None` or dictionary of previously serialized attributes. For use in inheritance call, when certain
            attributes require specific deserialization.

        Returns
        -------
        MonochromeDisplayRemapType
            corresponding class instance
        """

        if kwargs is None:
            kwargs = {}

        lut_node = node.find('RemapLUT') if xml_ns is None else node.find('default:RemapLUT', xml_ns)
        if lut_node is not None:
            dim1 = int_func(lut_node.attrib['size'])
            arr = numpy.zeros((dim1, ), dtype=numpy.uint8)
            entries = _get_node_value(lut_node).split()
            i = 0
            for entry in entries:
                if len(entry) == 0:
                    continue
                arr[i] = int(entry)
                i += 1
            kwargs['RemapLUT'] = arr
        return super(MonochromeDisplayRemapType, cls).from_node(node, xml_ns, **kwargs)

    def to_node(self, doc, tag, parent=None, check_validity=False, strict=DEFAULT_STRICT, exclude=()):
        node = super(MonochromeDisplayRemapType, self).to_node(
            doc, tag, parent=parent, check_validity=check_validity, strict=strict)
        if self._remap_lut is not None:
            value = ' '.join('{0:d}'.format(entry) for entry in self._remap_lut)
            entry = _create_text_node(doc, 'RemapLUT', value, parent=node)
            entry.attrib['size'] = str(self._remap_lut.size)
        return node

    def to_dict(self, check_validity=False, strict=DEFAULT_STRICT, exclude=()):
        out = super(MonochromeDisplayRemapType, self).to_dict(
            check_validity=check_validity, strict=strict, exclude=exclude)
        if self.RemapLUT is not None:
            out['RemapLUT'] = self.RemapLUT.tolist()
        return out


class RemapChoiceType(Serializable):
    """
    The remap choice type.
    """

    _fields = ('ColorDisplayRemap', 'MonochromeDisplayRemap')
    _required = ()
    # Descriptor
    ColorDisplayRemap = _SerializableDescriptor(
        'ColorDisplayRemap', ColorDisplayRemapType, _required, strict=DEFAULT_STRICT,
        docstring='Information for proper color display of the '
                  'data.')  # type: Union[None, ColorDisplayRemapType]
    MonochromeDisplayRemap = _SerializableDescriptor(
        'MonochromeDisplayRemap', MonochromeDisplayRemapType, _required, strict=DEFAULT_STRICT,
        docstring='Information for proper monochrome display of the '
                  'data.')  # type: Union[None, MonochromeDisplayRemapType]

    def __init__(self, ColorDisplayRemap=None, MonochromeDisplayRemap=None, **kwargs):
        """

        Parameters
        ----------
        ColorDisplayRemap : None|ColorDisplayRemapType|numpy.ndarray|list|type
        MonochromeDisplayRemap : None|MonochromeDisplayRemapType
        kwargs
        """

        if '_xml_ns' in kwargs:
            self._xml_ns = kwargs['_xml_ns']
        self.ColorDisplayRemap = ColorDisplayRemap
        self.MonochromeDisplayRemap = MonochromeDisplayRemap
        super(RemapChoiceType, self).__init__(**kwargs)


class MonitorCompensationAppliedType(Serializable):
    """

    """
    _fields = ('Gamma', 'XMin')
    _required = ('Gamma', 'XMin')
    _numeric_format = {key: '0.16G' for key in _fields}
    # Descriptor
    Gamma = _FloatDescriptor(
        'Gamma', _required, strict=DEFAULT_STRICT,
        docstring='Gamma value for monitor compensation pre-applied to the image.')  # type: float
    XMin = _FloatDescriptor(
        'XMin', _required, strict=DEFAULT_STRICT,
        docstring='Xmin value for monitor compensation pre-applied to the image.')  # type: float

    def __init__(self, Gamma=None, XMin=None, **kwargs):
        """

        Parameters
        ----------
        Gamma : float
        XMin : float
        kwargs
        """

        if '_xml_ns' in kwargs:
            self._xml_ns = kwargs['_xml_ns']
        self.Gamma = Gamma
        self.XMin = XMin
        super(MonitorCompensationAppliedType, self).__init__(**kwargs)


class DRAHistogramOverridesType(Serializable):
    """
    Dynamic range adjustment overide parameters.
    """
    _fields = ('ClipMin', 'ClipMax')
    _required = ('ClipMin', 'ClipMax')
    # Descriptor
    ClipMin = _IntegerDescriptor(
        'ClipMin', _required, strict=DEFAULT_STRICT,
        docstring='Suggested override for the lower end-point of the display histogram in the '
                  'ELT DRA application. Referred to as Pmin in SIPS documentation.')  # type: int
    ClipMax = _IntegerDescriptor(
        'ClipMax', _required, strict=DEFAULT_STRICT,
        docstring='Suggested override for the upper end-point of the display histogram in the '
                  'ELT DRA application. Referred to as Pmax in SIPS documentation.')  # type: int

    def __init__(self, ClipMin=None, ClipMax=None, **kwargs):
        """

        Parameters
        ----------
        ClipMin : int
        ClipMax : int
        kwargs
        """

        if '_xml_ns' in kwargs:
            self._xml_ns = kwargs['_xml_ns']
        self.ClipMin = ClipMin
        self.ClipMax = ClipMax
        super(DRAHistogramOverridesType, self).__init__(**kwargs)


class ProductDisplayType(Serializable):
    """

    """
    _fields = (
        'PixelType', 'RemapInformation', 'MagnificationMethod', 'DecimationMethod',
        'DRAHistogramOverrides', 'MonitorCompensationApplied', 'DisplayExtension')
    _required = (
        'PixelType', )
    _collections_tags = {
        'DisplayExtensions': {'array': False, 'child_tag': 'DisplayExtension'}}
    # Descriptors
    PixelType = _StringEnumDescriptor(
        'PixelType', ('MONO8I', 'MONO8LU', 'MONO16I', 'RGBL8U', 'RGB24I'), _required, strict=DEFAULT_STRICT,
        docstring='Enumeration of the pixel type. Definition in '
                  'Design and Exploitation document.')  # type: str
    RemapInformation = _SerializableDescriptor(
        'RemapInformation', RemapChoiceType, _required, strict=DEFAULT_STRICT,
        docstring='Information regarding the encoding of the pixel data. '
                  'Used for 8-bit pixel types.')  # type: Union[None, RemapChoiceType]
    MagnificationMethod = _StringEnumDescriptor(
        'MagnificationMethod', ('NEAREST_NEIGHBOR', 'BILINEAR', 'LAGRANGE'), _required, strict=DEFAULT_STRICT,
        docstring='Recommended ELT magnification method for this data.')  # type: Union[None, str]
    DecimationMethod = _StringEnumDescriptor(
        'DecimationMethod', ('NEAREST_NEIGHBOR', 'BILINEAR', 'BRIGHTEST_PIXEL', 'LAGRANGE'),
        _required, strict=DEFAULT_STRICT,
        docstring='Recommended ELT decimation method for this data. Also used as default for '
                  'reduced resolution dataset generation (if applicable).')  # type: Union[None, str]
    DRAHistogramOverrides = _SerializableDescriptor(
        'DRAHistogramOverrides', DRAHistogramOverridesType, _required, strict=DEFAULT_STRICT,
        docstring='Recommended ELT DRA overrides.')  # type: Union[None, DRAHistogramOverridesType]
    MonitorCompensationApplied = _SerializableDescriptor(
        'MonitorCompensationApplied', MonitorCompensationAppliedType, _required, strict=DEFAULT_STRICT,
        docstring='Describes monitor compensation that may have been applied to the product '
                  'during processing.')  # type: Union[None, MonitorCompensationAppliedType]
    DisplayExtensions = _ParametersDescriptor(
        'DisplayExtensions', _collections_tags, required=_required, strict=DEFAULT_STRICT,
        docstring='Optional extensible parameters used to support profile-specific needs related to '
                  'product display. Predefined filter types.')  # type: ParametersCollection

    def __init__(self, PixelType=None, RemapInformation=None, MagnificationMethod=None, DecimationMethod=None,
                 DRAHistogramOverrides=None, MonitorCompensationApplied=None, DisplayExtensions=None, **kwargs):
        """

        Parameters
        ----------
        PixelType : PixelTypeType
        RemapInformation : None|RemapChoiceType
        MagnificationMethod : None|str
        DecimationMethod : None|str
        DRAHistogramOverrides : None|DRAHistogramOverridesType
        MonitorCompensationApplied : None|MonitorCompensationAppliedType
        DisplayExtensions : None|ParametersCollection|dict
        kwargs
        """

        if '_xml_ns' in kwargs:
            self._xml_ns = kwargs['_xml_ns']
        self.PixelType = PixelType
        self.RemapInformation = RemapInformation
        self.MagnificationMethod = MagnificationMethod
        self.DecimationMethod = DecimationMethod
        self.DRAHistogramOverrides = DRAHistogramOverrides
        self.MonitorCompensationApplied = MonitorCompensationApplied
        self.DisplayExtensions = DisplayExtensions
        super(ProductDisplayType, self).__init__(**kwargs)
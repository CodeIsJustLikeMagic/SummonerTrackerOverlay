import wx
from collections import OrderedDict
def __init__(self, parent, log):
    self.log = log
    wx.Panel.__init__(self, parent, wx.ID_ANY, style=wx.CLIP_CHILDREN)

    ## self.SetDoubleBuffered(True)

    self.background = wx.Brush(self.GetBackgroundColour())
    self.Bind(wx.EVT_PAINT, self.OnPaint)
    self.Bind(wx.EVT_SIZE, self.OnSize)

    # --Rubberband Overlay
    self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
    self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
    self.Bind(wx.EVT_MOTION, self.OnMouseMove)
    self.startPos = None
    self.endPos = None
    self.overlay = wx.Overlay()

    self.cropbitmap = wx.Bitmap('bitmaps/cropshot24x20.png')
    self.honeyBitmap = wx.Bitmap('bitmaps/honeycomb300.png')

    self.wxPenStylesDict = OrderedDict([
        ('Solid', wx.PENSTYLE_SOLID),
        ('Dot', wx.PENSTYLE_DOT),
        ('Long Dash', wx.PENSTYLE_LONG_DASH),
        ('Short Dash', wx.PENSTYLE_SHORT_DASH),
        ('Dot Dash', wx.PENSTYLE_DOT_DASH),
        ('User Dash', wx.PENSTYLE_USER_DASH),
        ('Transparent', wx.PENSTYLE_TRANSPARENT),
        # ('Stipple'             , wx.PENSTYLE_STIPPLE),
        ('BDiagonal Hatch', wx.PENSTYLE_BDIAGONAL_HATCH),
        ('CrossDiag Hatch', wx.PENSTYLE_CROSSDIAG_HATCH),
        ('FDiagonal Hatch', wx.PENSTYLE_FDIAGONAL_HATCH),
        ('Cross Hatch', wx.PENSTYLE_CROSS_HATCH),
        ('Horizontal Hatch', wx.PENSTYLE_HORIZONTAL_HATCH),
        ('Vertical Hatch', wx.PENSTYLE_VERTICAL_HATCH),
    ])

    list = []
    for key, value in self.wxPenStylesDict.items():
        list.append(key)
    self.penstylesCombo = wx.ComboBox(self, -1, choices=list,
                                      size=(150, -1),
                                      style=wx.CB_READONLY)
    self.penstylesCombo.SetSelection(0)
    self.penstylesCombo.SetToolTip('Pen Style')

    self.overlayPenWidth = wx.SpinCtrl(self, -1, value='',
                                       size=(75, -1),
                                       style=wx.SP_ARROW_KEYS,
                                       min=1, max=24, initial=1)
    self.overlayPenWidth.SetToolTip('Pen Width')

    from wx.lib.colourselect import ColourSelect
    self.overlayPenColor = ColourSelect(self, -1, colour=wx.BLUE)
    self.overlayPenColor.SetToolTip('Pen Color')

    sizer = wx.BoxSizer(wx.HORIZONTAL)
    sizer.Add(self.penstylesCombo, 0, wx.ALL, 5)
    sizer.Add(self.overlayPenWidth, 0, wx.ALL, 5)
    sizer.Add(self.overlayPenColor, 0, wx.ALL, 5)
    box = wx.BoxSizer(wx.VERTICAL)
    box.Add(sizer, 0)
    box.Add((1, 1), 1)

    self.SetSizer(box)

    self.OnSize()
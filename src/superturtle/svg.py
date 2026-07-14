import math
import re
from collections import defaultdict
from dataclasses import dataclass

try:
    import tkinter as tk
except ImportError as e:
    raise ImportError(
        "superturtle's SVG export requires tkinter. "
        "On macOS with Homebrew Python, install it with: "
        "brew install python-tk@X.Y  (replace X.Y with your Python version)"
    ) from e

from turtle import RawTurtle, TurtleScreen, TurtleGraphicsError


class _DummyWindow:
    def call(self, *args, **kwargs):
        pass


@dataclass
class _CanvasItem:
    method: str
    coords: tuple
    attribs: dict
    z_order: int
    deleted: bool = False


class SVGCanvas:
    """Fake Tk canvas that records drawing commands for SVG export."""

    def __init__(self, width: int, height: int):
        self._opts = {'width': int(round(width)), 'height': int(round(height)), 'bg': 'white'}
        self._items: list[_CanvasItem] = []

    # --- option accessors (TurtleScreenBase reads width/height via cget) ---

    def cget(self, key):
        val = self._opts.get(key, '')
        # Tkinter returns scrollregion as a space-separated string
        if key == 'scrollregion' and isinstance(val, (tuple, list)):
            return ' '.join(str(v) for v in val)
        return val

    def __getitem__(self, key):
        return self.cget(key)

    def config(self, **kwargs):
        self._opts.update(kwargs)

    configure = config

    # --- dimensions ---

    def winfo_width(self) -> int:
        return self._opts['width']

    def winfo_height(self) -> int:
        return self._opts['height']

    @staticmethod
    def winfo_toplevel():
        return _DummyWindow()

    # --- item creation ---

    def create_line(self, *coords, **opts):
        return self._add('line', coords, opts)

    def create_polygon(self, coords, **opts):
        # turtle.py passes coords as a single flat sequence
        return self._add('polygon', tuple(coords), opts)

    def create_text(self, x, y, **opts):
        return self._add('text', (x, y), opts)

    def create_image(self, *args, **opts):
        return self._add('image', args, opts)

    def _add(self, method, coords, attribs):
        item_id = len(self._items)
        self._items.append(_CanvasItem(method, coords, dict(attribs), item_id))
        return item_id

    # --- item management ---

    def coords(self, item_id, *new_coords):
        if new_coords:
            self._items[item_id].coords = new_coords
        else:
            return list(self._items[item_id].coords)

    def itemconfigure(self, item_id, **kwargs):
        self._items[item_id].attribs.update(kwargs)

    itemconfig = itemconfigure

    def itemcget(self, item_id, key):
        return self._items[item_id].attribs.get(key, '')

    def tag_raise(self, item_id):
        if self._items:
            self._items[item_id].z_order = max(i.z_order for i in self._items) + 1

    def delete(self, target):
        if target == 'all':
            for item in self._items:
                item.deleted = True
        elif isinstance(target, int):
            self._items[target].deleted = True

    def find_all(self):
        return range(len(self._items))

    def bbox(self, item_id):
        coords = self._items[item_id].coords
        if coords:
            return coords[0], coords[1], coords[0], coords[1]
        return 0, 0, 0, 0

    def type(self, item_id):
        return self._items[item_id].method

    # --- no-ops (event binding, display refresh) ---

    def update(self): pass
    def after(self, *args, **kwargs): pass
    def focus_force(self): pass
    def bind(self, *args, **kwargs): pass
    def unbind(self, *args, **kwargs): pass
    def tag_bind(self, *args, **kwargs): pass
    def tag_unbind(self, *args, **kwargs): pass


class SVGScreen(TurtleScreen):
    """TurtleScreen backed by SVGCanvas instead of a real Tk window."""

    def __init__(self, canvas: SVGCanvas):
        # Create a hidden Tk root before super().__init__ so that:
        #   - _blankimage() can return a real PhotoImage (satisfies Python 3.14's
        #     isinstance assertion in Shape.__init__ without any monkey-patching)
        #   - _colorstr() can resolve color names via winfo_rgb
        self._tk_root = tk.Tk()
        self._tk_root.withdraw()
        super().__init__(canvas)

    def _blankimage(self):
        return tk.PhotoImage(width=1, height=1, master=self._tk_root)

    def _colorstr(self, color):
        if len(color) == 1:
            color = color[0]
        if isinstance(color, str):
            if re.match(r'^#[0-9A-Fa-f]{6}$', color):
                return color.lower()
            try:
                r16, g16, b16 = self._tk_root.winfo_rgb(color)
                return '#%02x%02x%02x' % (r16 >> 8, g16 >> 8, b16 >> 8)
            except tk.TclError:
                raise TurtleGraphicsError(f'bad color string: {color!r}')
        try:
            r, g, b = color
        except (TypeError, ValueError):
            raise TurtleGraphicsError(f'bad color arguments: {color!r}')
        colormode = self._colormode
        r, g, b = [round(255.0 * x / colormode) for x in (r, g, b)]
        if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
            raise TurtleGraphicsError(f'bad color sequence: {color!r}')
        return '#%02x%02x%02x' % (r, g, b)

    def _iscolorstring(self, color):
        try:
            self._tk_root.winfo_rgb(color)
            return True
        except tk.TclError:
            return False

    def _color(self, colorstr):
        # Colors are stored as hex strings; return as-is
        return colorstr

    # --- Tk stubs ---

    def title(self, title): pass
    def setup(self, *args, **kwargs): pass
    def textinput(self, title, prompt): return None
    def numinput(self, title, prompt, default=None, minval=None, maxval=None): return None
    def mainloop(self): pass
    def done(self): pass
    def bye(self): pass
    def exitonclick(self): pass


class SVGTurtle(RawTurtle):
    """RawTurtle that draws to an SVGCanvas instead of a real Tk window."""

    def __init__(self, width: int, height: int):
        canvas = SVGCanvas(width, height)
        screen = SVGScreen(canvas)
        super().__init__(screen)
        self.speed(0)
        self._svg_fill_items_start = None
        self._svg_fill_prev_line_item = None
        self._svg_fill_line_same = False

    def _drawturtle(self):
        pass

    def pen(self, pen=None, **pendict):
        if not (pen or pendict):
            return super().pen()
        p = dict(pen) if isinstance(pen, dict) else {}
        p.update(pendict)
        p['speed'] = 0
        return super().pen(p)

    def circle(self, radius, extent=None, steps=None):
        """Draw a circle or arc, emitting a true SVG circle/arc when steps is None.

        When steps is explicitly given, the polygon-approximation behavior of the
        standard turtle is preserved (useful for drawing regular polygons).
        """
        if steps is None:
            was_filling = self.filling()
            was_drawing = self._drawing
            pos_before = self.pos()       # turtle coords (x, y)
            heading_before = self.heading()
            pen_color = self._pencolor
            pen_size = self._pensize

            # Lift the pen so super().circle() advances position and _fillpath
            # without writing polygon-approximation coords into any line item.
            if was_drawing:
                self.penup()

            super().circle(radius, extent, steps)

            if was_drawing:
                self.pendown()

            # When inside a fill region the polygon's outline already traces the
            # boundary, so we omit the separate arc stroke item.
            if was_drawing and not was_filling:
                k = self._degreesPerAU   # angular-unit → degrees conversion
                canvas = self.getscreen().cv
                canvas._items.append(_CanvasItem(
                    method='arc',
                    coords=(
                        float(pos_before[0]),
                        float(pos_before[1]),
                        heading_before * k,                                        # degrees
                        radius,
                        (extent if extent is not None else self._fullcircle) * k,  # degrees
                    ),
                    attribs={'fill': pen_color, 'width': pen_size},
                    z_order=len(canvas._items),
                ))
        else:
            super().circle(radius, extent, steps)

    def begin_fill(self):
        """Begin a fill region; records the canvas state so end_fill can clean up."""
        canvas = self.getscreen().cv
        self._svg_fill_items_start = len(canvas._items)
        # Save the current line item BEFORE begin_fill so we can detect whether
        # _newLine (called inside begin_fill) reused it or replaced it.
        # _newLine only creates a new item when len(currentLine) > 1; if the
        # turtle hasn't drawn anything yet it reuses the existing item and that
        # item will silently accumulate fill-region coordinates.
        self._svg_fill_prev_line_item = self.currentLineItem
        super().begin_fill()
        # True when _newLine kept the same item (no pre-fill drawing existed).
        self._svg_fill_line_same = (self.currentLineItem == self._svg_fill_prev_line_item)

    def end_fill(self):
        """Close the fill region.

        Suppresses the line items drawn inside the fill (their edges are already
        captured by the fill polygon) and adds the current pen color as the
        polygon's outline stroke so downstream tools can distinguish the boundary.
        """
        fill_item_id = self._fillitem
        pen_color = self._pencolor
        pen_size = self._pensize
        fill_items_start = self._svg_fill_items_start if self._svg_fill_items_start is not None else 0
        prev_line_item = getattr(self, '_svg_fill_prev_line_item', None)
        line_same = getattr(self, '_svg_fill_line_same', False)

        super().end_fill()

        canvas = self.getscreen().cv
        # Suppress line items created during the fill region. The fill polygon
        # already captures the boundary, so separate stroke items are redundant.
        for i in range(fill_items_start, len(canvas._items)):
            if canvas._items[i].method == 'line':
                canvas._items[i].deleted = True

        # When _newLine didn't create a fresh item at begin_fill time, the
        # original currentLineItem was reused for fill content — delete it too.
        if line_same and prev_line_item is not None:
            canvas._items[prev_line_item].deleted = True

        # Give the fill polygon a visible outline using the current pen.
        if fill_item_id is not None:
            canvas.itemconfigure(fill_item_id, outline=pen_color, width=pen_size)

        self._svg_fill_items_start = None
        self._svg_fill_prev_line_item = None
        self._svg_fill_line_same = False

    def save_as(self, filename: str, group_colors: bool = True):
        canvas = self.getscreen().cv
        _write_svg(canvas, canvas.winfo_width(), canvas.winfo_height(),
                   filename, group_colors=group_colors)


def _arc_svg_parts(coords, xoff: float, yoff: float) -> tuple[str, str]:
    """Return (svg_tag, geometry_attrs) for an arc canvas item.

    coords is (start_x, start_y, heading_deg, radius, extent_deg) in turtle
    coordinate space (y-up, origin at canvas centre).  xoff/yoff shift to SVG
    viewport coordinates (y-down, origin at top-left).
    """
    start_x, start_y, heading_deg, radius, extent_deg = coords
    r = abs(radius)
    h_rad = math.radians(heading_deg)

    # Centre of the circle in turtle coords.
    # The centre is `radius` units to the LEFT of the turtle's heading:
    #   left direction = (-sin h, cos h)  →  centre = pos + radius * (-sin h, cos h)
    cx = start_x - radius * math.sin(h_rad)
    cy = start_y + radius * math.cos(h_rad)

    if abs(extent_deg) >= 360:
        # Full circle: SVG <circle> is exact and avoids the degenerate-arc problem.
        cx_svg = cx + xoff
        cy_svg = -cy + yoff
        return 'circle', f'cx="{cx_svg:.3f}" cy="{cy_svg:.3f}" r="{r:.3f}"'

    # Partial arc: SVG <path> with elliptical-arc command.
    sx = start_x + xoff
    sy = -start_y + yoff

    # Angle from centre to start point, then sweep in the correct direction.
    theta_start = math.atan2(start_y - cy, start_x - cx)
    arc_dir = 1 if radius > 0 else -1   # positive radius → CCW in turtle (y-up)
    theta_end = theta_start + math.radians(extent_deg) * arc_dir

    ex_svg = (cx + r * math.cos(theta_end)) + xoff
    ey_svg = -(cy + r * math.sin(theta_end)) + yoff

    large_arc = 1 if abs(extent_deg) > 180 else 0
    # CCW in turtle (y-up)  →  CW in SVG (y-down)  →  sweep-flag = 1
    sweep = 1 if radius * extent_deg > 0 else 0

    d = (f'M {sx:.3f},{sy:.3f}'
         f' A {r:.3f},{r:.3f} 0 {large_arc} {sweep}'
         f' {ex_svg:.3f},{ey_svg:.3f}')
    return 'path', f'd="{d}"'


def _write_svg(canvas: SVGCanvas, width: int, height: int, filename: str,
               group_colors: bool = True):
    """Write canvas contents to an SVG file.

    TurtleScreenBase sets scrollregion to (-w//2, -h//2, w//2, h//2), so
    canvas coordinates are (turtle_x, -turtle_y). The SVG offset is therefore
    simply (width/2, height/2).
    """
    xoff = width / 2
    yoff = height / 2

    def point_str(flat_coords):
        pairs = []
        it = iter(flat_coords)
        for x in it:
            y = next(it)
            pairs.append(f'{x + xoff:.3f},{y + yoff:.3f}')
        return ' '.join(pairs)

    # Emit visible, non-deleted items: lines and arcs (stroke items) plus
    # polygons whose fill attribute has been set (fill regions).
    drawable = [
        item for item in sorted(canvas._items, key=lambda i: i.z_order)
        if not item.deleted
        and item.method in ('line', 'polygon', 'arc')
        and item.attribs.get('fill', '') != ''
    ]

    clip = 'clip-path="url(#border)"'
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg"'
        f' viewBox="0 0 {width} {height}"'
        f' width="{width}" height="{height}">',
        '  <defs>',
        '    <clipPath id="border">',
        f'      <rect width="{width}" height="{height}"/>',
        '    </clipPath>',
        '  </defs>',
    ]

    if group_colors:
        strokes_by_color: dict[str, list[_CanvasItem]] = defaultdict(list)
        fill_items: list[_CanvasItem] = []

        for item in drawable:
            if item.method in ('line', 'arc'):
                strokes_by_color[item.attribs.get('fill', 'black')].append(item)
            else:
                fill_items.append(item)

        for color, group in strokes_by_color.items():
            out.append(
                f'  <g stroke="{color}" fill="none"'
                f' stroke-linecap="round" {clip}>'
            )
            for item in group:
                sw = item.attribs.get('width', 1)
                if item.method == 'arc':
                    tag, geom = _arc_svg_parts(item.coords, xoff, yoff)
                    out.append(f'    <{tag} {geom} stroke-width="{sw}"/>')
                else:
                    out.append(
                        f'    <polyline points="{point_str(item.coords)}"'
                        f' stroke-width="{sw}"/>'
                    )
            out.append('  </g>')

        for item in fill_items:
            fill = item.attribs.get('fill', 'none')
            stroke = item.attribs.get('outline', '') or 'none'
            sw = item.attribs.get('width', 0)
            out.append(
                f'  <polygon points="{point_str(item.coords)}"'
                f' fill="{fill}" stroke="{stroke}" stroke-width="{sw}"'
                f' fill-rule="evenodd" {clip}/>'
            )
    else:
        for item in drawable:
            if item.method == 'arc':
                color = item.attribs.get('fill', 'black')
                sw = item.attribs.get('width', 1)
                tag, geom = _arc_svg_parts(item.coords, xoff, yoff)
                out.append(
                    f'  <{tag} {geom} fill="none"'
                    f' stroke="{color}" stroke-width="{sw}"'
                    f' stroke-linecap="round" {clip}/>'
                )
            elif item.method == 'line':
                pts = point_str(item.coords)
                color = item.attribs.get('fill', 'black')
                sw = item.attribs.get('width', 1)
                out.append(
                    f'  <polyline points="{pts}"'
                    f' stroke="{color}" stroke-width="{sw}"'
                    f' fill="none" stroke-linecap="round" {clip}/>'
                )
            else:
                pts = point_str(item.coords)
                fill = item.attribs.get('fill', 'none')
                stroke = item.attribs.get('outline', '') or 'none'
                sw = item.attribs.get('width', 0)
                out.append(
                    f'  <polygon points="{pts}"'
                    f' fill="{fill}" stroke="{stroke}" stroke-width="{sw}"'
                    f' fill-rule="evenodd" {clip}/>'
                )

    out.append('</svg>')
    with open(filename, 'w') as f:
        f.write('\n'.join(out) + '\n')

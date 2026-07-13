import re
from collections import defaultdict
from dataclasses import dataclass, field

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

    def _drawturtle(self):
        pass

    def pen(self, pen=None, **pendict):
        if not (pen or pendict):
            return super().pen()
        p = dict(pen) if isinstance(pen, dict) else {}
        p.update(pendict)
        p['speed'] = 0
        return super().pen(p)

    def save_as(self, filename: str, group_colors: bool = True):
        canvas = self.getscreen().cv
        _write_svg(canvas, canvas.winfo_width(), canvas.winfo_height(),
                   filename, group_colors=group_colors)


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

    # Only emit visible, non-deleted line/polygon items.
    # Items with fill='' are invisible placeholders (turtle cursor, undrawn lines).
    drawable = [
        item for item in sorted(canvas._items, key=lambda i: i.z_order)
        if not item.deleted
        and item.method in ('line', 'polygon')
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
        lines_by_color: dict[str, list[_CanvasItem]] = defaultdict(list)
        fill_items: list[_CanvasItem] = []

        for item in drawable:
            if item.method == 'line':
                lines_by_color[item.attribs.get('fill', 'black')].append(item)
            else:
                fill_items.append(item)

        for color, group in lines_by_color.items():
            out.append(
                f'  <g stroke="{color}" fill="none"'
                f' stroke-linecap="round" {clip}>'
            )
            for item in group:
                sw = item.attribs.get('width', 1)
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
            pts = point_str(item.coords)
            if item.method == 'line':
                color = item.attribs.get('fill', 'black')
                sw = item.attribs.get('width', 1)
                out.append(
                    f'  <polyline points="{pts}"'
                    f' stroke="{color}" stroke-width="{sw}"'
                    f' fill="none" stroke-linecap="round" {clip}/>'
                )
            else:
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

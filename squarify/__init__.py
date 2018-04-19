# Squarified Treemap Layout
# Implements algorithm from Bruls, Huizing, van Wijk, "Squarified Treemaps"
#   (but not using their pseudocode)

import typing

class Area(typing.NamedTuple):
	"""
	A type that represents an area, compatible with e.g. pygame screensizes, shutil termsizes etc.

	The magnitude of an Area is easily found from its absolute value:
	>>> abs(Area(16, 9))
	144

	To flip an area so that its height and width swap values, simply take the negative
	>>> -Area(16, 9)
	Area(width=9, height=16)

	You can add or subtract dimensions from an Area, and combining two areas in this way does NOT
	add/subtract the area of one to the other (somewhat confusingly). This would difficult to do in
	a sensible way since areas *must* be integers, but have no forced aspect ratio. Consider trying
	to add a 2x2 square to a 1x3 rectangle. The resulting width and height cannot maintain the
	aspect ratio of either initial area while retaining integral values.
	>>> Area(1,1) + (1,1)
	Area(width=2, height=2)
	>>> (5, 7) - Area(2, 2)
	Area(width=3, height=5)


	This type interacts with numeric types in the following ways:

	Multiplying by integers scales the area's size (rounds width/height to integers)
	>>> Area(16, 9) * 2
	Area(width=22, height=12)

	Multiplying by a float, on the other hand, returns the scalar area of the Area scaled up by the
	float amount
	>>> Area(16, 9) * 2.0
	288.0

	If you want the second behaviour with ints (or also floats), use the matrix multiplication
	operator
	>>> Area(16, 9) @ 2
	288
	>>> 2.0 @ Area(16, 9)
	288.0

	True division always returns a scalar for supported argument types
	>>> Area(32, 18) / 2
	288.0
	>>> 288.0 / Area(32, 18)
	0.5

	Floor division of an Area will scale it, while floor division by an Area yields a scalar
	>>> Area(32, 18) // 2
	Area(width=22, height=12)
	>>> 288.0 // Area(16, 9)
	2.0
	"""
	width: int
	height: int

	def __str__(self) -> str:
		"""
		Implements `str(self)`
		"""
		return "%dx%d" % self

	def __bool__(self) -> bool:
		"""
		Implements `bool(self)`
		"""
		return all(self)

	def __add__(self, other: object) -> object:
		"""
		Implements `self + other`
		"""
		if isinstance(other, tuple) and len(other) == 2 and all(isinstance(a, int) for a in other):
			return type(self)(other[0] + self.width, other[1] + self.height)
		return NotImplemented

	def __radd__(self, other: object) -> object:
		"""
		Implements `other + self`
		"""
		if isinstance(other, tuple) and len(other) == 2 and all(isinstance(a, int) for a in other):
			return type(self)(other[0] + self.width, other[1] + self.height)
		return NotImplemented

	def __sub__(self, other: object) -> object:
		"""
		Implements `self - other`
		"""
		if isinstance(other, tuple) and len(other) == 2 and all(isinstance(a, int) for a in other):
			return type(self)(self.width - other[0],  self.height - other[1])
		return NotImplemented

	def __rsub__(self, other: object) -> object:
		"""
		Implements `other + self`
		"""
		if isinstance(other, tuple) and len(other) == 2 and all(isinstance(a, int) for a in other):
			return type(self)(other[0] - self.width, other[1] - self.height)
		return NotImplemented

	def __mul__(self, other: object) -> object:
		"""
		Implements `self * other`
		"""
		if isinstance(other, int):
			toMult = other**0.5
			return type(self)(int(self.width * toMult), int(self.height * toMult))
		if isinstance(other, float):
			return other * self.width * self.height
		return NotImplemented

	def __rmul__(self, other: object) -> object:
		"""
		Implements `other * self`
		"""
		return self * other

	def __truediv__(self, other: object) -> object:
		"""
		Implements `self / other`
		"""
		if isinstance(other, int) or isinstance(other, float):
			return (self.width * self.height) / other
		return NotImplemented

	def __rtruediv__(self, other: object) -> object:
		"""
		Implements `other / self`
		"""
		if isinstance(other, int) or isinstance(other, float):
			return other / (self.width * self.height)
		return NotImplemented

	def __floordiv__(self, other: object) -> object:
		"""
		Implements `self // other`
		"""
		if isinstance(other, int) or isinstance(other, float):
			toDiv = other**0.5
			return type(self)(int(self.width // toDiv), int(self.height // toDiv))
		return NotImplemented

	def __rfloordiv__(self, other: object) -> object:
		"""
		Implements `other // self`
		"""
		if isinstance(other, int) or isinstance(other, float):
			return other // (self.width * self.height)
		return NotImplemented

	def __matmul__(self, other: object) -> object:
		"""
		Implements `self @ other`
		"""
		if isinstance(other, int) or isinstance(other, float):
			return other * self.width * self.height

		return NotImplemented

	def __rmatmul__(self, other: object) -> object:
		"""
		Implements `other @ self`
		"""

		return self @ other

	def __abs__(self) -> int:
		"""
		Returns the total area encompassed
		"""
		return self.width * self.height

	def __neg__(self) -> 'Area':
		"""
		Returns an Area that results from "flipping"  `self` 

		i.e. one that has a width equal to `self`'s height, and a height equal to `self`'s width
		"""
		return type(self)(*reversed(self))

class Point(typing.NamedTuple):
	"""
	A class that represents a point in 2D space.

	Note that a Point can ONLY exist at integer (x, y) values.

	Points can be added or subtracted together:
	>>> Point(0,1) + Point(1,0)
	Point(x=1, y=1)
	>>> Point(1, 0) - Point(1, 0)
	Point(x=0, y=0)

	For convenience, you can also add any iterable that looks like a point in >= 2D space to a Point.
	Note that higher dimensions are ignored when this object is the LEFT operand, but if a Point is
	the RIGHT operand of such an operation, it will be added to the first components of the iterable
	as though it were a higher-dimensional Point with 0 values for all dimensions above 2.
	>>> p = Point(1, 1)
	>>> p + (1, 0)
	Point(x=2, y=1)
	>>> [5, 5, 7] - Point(1,1)
	[4, 4, 7]

	Note that you should be careful with this, because the operators when a Point is on the left work
	by casting the right operand's first two indicies to `int`s. So for example, this can be used
	to do the following:
	>>> Point(0,0) + "11"
	Point(x=1, y=1)

	which could maybe seem useful in some case, but note that it's impossible to add two-digit decimal
	values to the Point in this way.
	>>> Point(0,0) + "10, 11"
	Point(x=1, y=0)
	"""

	x: int
	y: int

	def __str__(self) -> str:
		"""
		Implements `str(self)`
		"""
		return "(%d, %d)" % self

	def __add__(self, other):
		"""
		Implements `self + other`
		"""
		try:
			toAdd = int(other[0]), int(other[1])
			return type(self)(self.x+toAdd[0], self.y+toAdd[1])
		except (IndexError, TypeError, ValueError):
			# This will hit if other is not indexable,
			# it doesn't have enough parts to seem like a point
			# its parts are not castable to int,
			# or its parts are not addable to our parts
			pass
		return NotImplemented

	def __radd__(self, other):
		"""
		Implements `other + self`
		"""
		try:
			return type(other)((other[0]+self.x, other[1]+self.y, *other[2:]))
		except (IndexError, TypeError, ValueError):
			pass
		return NotImplemented


	def __sub__(self, other):
		"""
		Implements `self - other`
		"""
		try:
			toSub = int(other[0]), int(other[1])
			return type(self)(self.x-toSub[0], self.y-toSub[1])
		except (IndexError, TypeError, ValueError):
			# This will hit if other is not indexable,
			# it doesn't have enough parts to seem like a point
			# its parts are not castable to int,
			# or its parts are not subtractable from our parts
			pass
		return NotImplemented

	def __rsub__(self, other):
		"""
		Implements `other - self`
		"""
		try:
			return type(other)((other[0]-self.x, other[1]-self.y, *other[2:]))
		except (IndexError, TypeError, ValueError):
			pass
		return NotImplemented

class Rect(typing.NamedTuple):
	"""
	A class that represents a rectangle.

	A rectangle has a Point that marks its top-left corner, and a contained Area.
	Rectangles are drawn in traditional computer graphics style, with the origin being the
	top left corner of a surface. That is, the x-axis points right, and the y-axis points down.
	So don't be surprised if the bottom-left corner of a `Rect` has a higher `y` value that its
	top-left corner.
	"""
	topleft: Point
	area: Area

	@property
	def topright(self) -> Point:
		"""
		Gives the rectangle's top-right corner as a Point
		"""
		return self.topleft + Point(self.area.width, 0)

	@property
	def bottomleft(self) -> Point:
		"""
		Gives the rectangles bottom-left corner as a Point
		"""
		return self.topleft + Point(0, self.area.height)

	@property
	def bottomright(self) -> Point:
		"""
		Gives the rectangle's bottom-right corner as a Point
		"""
		return self.topleft + Point(*self.area)

	@property
	def width(self) -> int:
		"""
		Gives the rectangle's width.
		"""
		return self.area.width

	@property
	def height(self) -> int:
		"""
		Gives the rectangle's height
		"""
		return self.area.height

def normalize_sizes(sizes: typing.List[float], areaOrDX: typing.Union[Area, int], dy: int=None) -> typing.List[float]:
	"""
	Normalizes the `sizes` with respect to an area of size `dx`x`dy`

	>>> normalize_sizes([50, 10, 1], (1920, 1080))
	[1699448.1311475409, 339876.47540983604, 33993.44262295082]
	"""
	area = Area(areaOrDX, dy) if dy else Area(*areaOrDX)

	totalSize = sum(sizes)
	return [size * area / totalSize for size in sizes]

def pad_rectangle(rect):
	if rect['dx'] > 2:
		rect['x'] += 1
		rect['dx'] -= 2
	if rect['dy'] > 2:
		rect['y'] += 1
		rect['dy'] -= 2

def layoutrow(sizes: typing.List[float], pt: Point, area: Area) -> typing.List[Rect]:
	"""
	Lays out a row
	"""
	# generate rects for each size in sizes
	# dx >= dy
	# they will fill up height dy, and width will be determined by their area
	# sizes should be pre-normalized wrt dx * dy (i.e., they should be same units)
	width = sum(sizes) / area.height
	rects = []
	for size in sizes:
		adjust = (0, int(size/width))
		rects.append(Rect(pt, Area(area.width, 0) + adjust))
		pt +=  adjust
	return rects

def layoutcol(sizes: typing.List[float], pt: Point, area: Area) -> typing.List[Rect]:
	# generate rects for each size in sizes
	# dx < dy
	# they will fill up width dx, and height will be determined by their area
	# sizes should be pre-normalized wrt dx * dy (i.e., they should be same units)
	height = sum(sizes) / area.width
	rects = []
	for size in sizes:
		adjust = (int(size/height), 0)
		rects.append(Rect(pt, Area(0, area.height)+adjust))
		pt += adjust
	return rects

def layout(sizes: typing.List[float], pt: Point, area: Area) -> typing.List[Rect]:
	return layoutrow(sizes, pt, area) if area.width >= area.height else layoutcol(sizes, pt, area)

def leftoverrow(sizes: typing.List[float], pt: Point, area: Area) -> Rect:
	# compute remaining area when dx >= dy
	width = int(sum(sizes) / area.height)
	leftoverPT = pt + (width, 0)
	leftoverArea = area - (width, 0)
	return Rect(leftoverPT, leftoverArea)

def leftovercol(sizes: typing.List[float], pt: Point, area: Area) -> Rect:
	# compute remaining area when dx >= dy
	height = int(sum(sizes) / area.width)
	leftoverPT = pt + (0, height)
	leftoverArea = area - (0, height) 
	return Rect(leftoverPT, leftoverArea)

def leftover(sizes: typing.List[float], pt: Point, area: Area) -> Rect:
	return leftoverrow(sizes, pt, area) if area.width >= area.height else leftovercol(sizes, pt, area)

def worstRatio(sizes: typing.List[float], pt: Point, area: Area) -> float:
	return max([max(rect.width / rect.height, rect.height / rect.width) for rect in layout(sizes, pt, area)])

def squarify(sizes: typing.List[float],
             PTorX: typing.Union[Point, int],
             areaOrY: typing.Union[Area, int],
             areaOrDX: typing.Union[Area, int] = None,
             dy: int = None) -> typing.List[Rect]:
	"""
	Returns a list of squarified `Rect`s with sizes `sizes` that fit in the rectangle `area`
	with top-left corner at `pt`.

	>>> squarify([1699448.1311475409, 339876.47540983604, 33993.44262295082], (0,0), (1920, 1080))
	[Rect(topleft=Point(x=0, y=0), area=Area(width=1920, height=1080)), Rect(topleft=Point(x=1573, y=0), area=Area(width=347, height=1080)), Rect(topleft=Point(x=1573, y=979), area=Area(width=347, height=101))]
	"""

	if not areaOrDX:
		pt = Point(*PTorX)
		area = Area(*areaOrY)
	elif not dy:
		pt = Point(PTorX, areaOrY)
		area = Area(*areaOrDX)
	else:
		pt = Point(PTorX, areaOrY)
		area = Area(areaOrDX, dy)


	# sizes should be pre-normalized wrt dx * dy (i.e., they should be same units)
	# or dx * dy == sum(sizes)
	# sizes should be sorted biggest to smallest
	
	if not sizes:
		return []
	
	if len(sizes) == 1:
		return layout(sizes, pt, area)
	
	# figure out where 'split' should be
	for i in range(1, len(sizes)):
		if worstRatio(sizes[:i], pt, area) < worstRatio(sizes[:(i+1)], pt, area):
			break
	current = sizes[:i]
	remaining = sizes[i:]
	
	leftoverPT, leftoverArea = leftover(current, pt, area)
	return layout(current, pt, area) + squarify(remaining, leftoverPT, leftoverArea)

def padded_squarify(sizes, x, y, dx=None, dy=None):
	return [pad_rectangle(rect) for rect in squarify(sizes, x, y, dx, dy)]

def plot(sizes, norm_x=100, norm_y=100,
		 color=None, label=None, value=None,
		 ax=None, **kwargs):

	"""
	Plotting with Matplotlib.

	Parameters
	----------
	sizes: input for squarify
	norm_x, norm_y: x and y values for normalization
	color: color string or list-like (see Matplotlib documentation for details)
	label: list-like used as label text
	value: list-like used as value text (in most cases identical with sizes argument)
	ax: Matplotlib Axes instance
	kwargs: dict, keyword arguments passed to matplotlib.Axes.bar

	Returns
	-------
	axes: Matplotlib Axes
	"""
	
	import matplotlib.pyplot as plt

	if ax is None:
		ax = plt.gca()

	if color is None:
		import matplotlib.cm
		import random
		cmap = matplotlib.cm.get_cmap()
		color = [cmap(random.random()) for i in range(len(sizes))]

	normed = normalize_sizes(sizes, norm_x, norm_y)
	rects = squarify(normed, 0, 0, norm_x, norm_y)
	
	x = [rect['x'] for rect in rects]
	y = [rect['y'] for rect in rects]
	dx = [rect['dx'] for rect in rects]
	dy = [rect['dy'] for rect in rects]

	ax.bar(x, dy, width=dx, bottom=y, color=color,
	   label=label, align='edge', **kwargs)

	if not value is None:
		va = 'center' if label is None else 'top'
			
		for v, r in zip(value, rects):
			x, y, dx, dy = r['x'], r['y'], r['dx'], r['dy']
			ax.text(x + dx / 2, y + dy / 2, v, va=va, ha='center')

	if not label is None:
		va = 'center' if value is None else 'bottom'
		for l, r in zip(label, rects):
			x, y, dx, dy = r['x'], r['y'], r['dx'], r['dy']
			ax.text(x + dx / 2, y + dy / 2, l, va=va, ha='center')

	ax.set_xlim(0, norm_x)
	ax.set_ylim(0, norm_y)
	return ax 
	

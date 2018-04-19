# Squarified Treemap Layout
# Implements algorithm from Bruls, Huizing, van Wijk, "Squarified Treemaps"
#   (but not using their pseudocode)

import typing

class Area(typing.NamedTuple):
	"""
	A type that represents an area, compatible with e.g. pygame screensizes, shutil termsizes etc.

	This type interacts with numeric types in the following ways:

	Multiplying by integers scales the area's size
	>>> Area(16, 9) * 2
	Area(width=32, height=18)

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
	144.0
	>>> 288.0 / Area(32, 18)
	1.0

	Floor division of an Area will scale it, while floor division by an Area yields a scalar
	>>> Area(32, 18) // 2
	Area(width=16, height=9)
	>>> 288.0 // Area(16, 9)
	2
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

	def __mul__(self, other: object) -> object:
		"""
		Implements `self * other`
		"""
		if isinstance(other, int):
			return type(self)(self.width * other, self.height * other)
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
			return self.width * self.height / other
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
			return type(self)(self.width // other, self.height // other)
		return NotImplemented

	def __rfloordiv__(self, other: object) -> object:
		"""
		Implements `other // self`
		"""
		if isinstance(other, int) or isinstance(other, float):
			return self.width * self.height // other
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


def normalize_sizes(sizes: typing.List[float], area: Area) -> typing.List[float]:
	"""
	Normalizes the `sizes` with respect to an area of size `dx`x`dy`
	"""
	total_size = sum(sizes)
	return [size * area / total_size for size in sizes]

def pad_rectangle(rect):
	if rect['dx'] > 2:
		rect['x'] += 1
		rect['dx'] -= 2
	if rect['dy'] > 2:
		rect['y'] += 1
		rect['dy'] -= 2

def layoutrow(sizes, x, y, dx, dy):
	# generate rects for each size in sizes
	# dx >= dy
	# they will fill up height dy, and width will be determined by their area
	# sizes should be pre-normalized wrt dx * dy (i.e., they should be same units)
	covered_area = sum(sizes)
	width = covered_area / dy
	rects = []
	for size in sizes:
		rects.append({'x': x, 'y': y, 'dx': width, 'dy': size / width})
		y += size / width
	return rects

def layoutcol(sizes, x, y, dx, dy):
	# generate rects for each size in sizes
	# dx < dy
	# they will fill up width dx, and height will be determined by their area
	# sizes should be pre-normalized wrt dx * dy (i.e., they should be same units)
	covered_area = sum(sizes)
	height = covered_area / dx
	rects = []
	for size in sizes:
		rects.append({'x': x, 'y': y, 'dx': size / height, 'dy': height})
		x += size / height
	return rects

def layout(sizes, x, y, dx, dy):
	return layoutrow(sizes, x, y, dx, dy) if dx >= dy else layoutcol(sizes, x, y, dx, dy)

def leftoverrow(sizes, x, y, dx, dy):
	# compute remaining area when dx >= dy
	covered_area = sum(sizes)
	width = covered_area / dy
	leftover_x = x + width
	leftover_y = y
	leftover_dx = dx - width
	leftover_dy = dy
	return (leftover_x, leftover_y, leftover_dx, leftover_dy)

def leftovercol(sizes, x, y, dx, dy):
	# compute remaining area when dx >= dy
	covered_area = sum(sizes)
	height = covered_area / dx
	leftover_x = x
	leftover_y = y + height
	leftover_dx = dx
	leftover_dy = dy - height
	return (leftover_x, leftover_y, leftover_dx, leftover_dy)

def leftover(sizes, x, y, dx, dy):
	return leftoverrow(sizes, x, y, dx, dy) if dx >= dy else leftovercol(sizes, x, y, dx, dy)

def worst_ratio(sizes, x, y, dx, dy):
	return max([max(rect['dx'] / rect['dy'], rect['dy'] / rect['dx']) for rect in layout(sizes, x, y, dx, dy)])

def squarify(sizes: typing.List[float], x: int, y: int, dx: int, dy: int) -> \
											  typing.List[typing.Tuple[float, float, float, float]]:
	"""
	Returns a list of squarified `size`s that fit in the rectangle of size `dx`x`dy`
	with top-left corner at (`x`, `y`)
	"""

	# sizes should be pre-normalized wrt dx * dy (i.e., they should be same units)
	# or dx * dy == sum(sizes)
	# sizes should be sorted biggest to smallest
	
	if not sizes:
		return []
	
	if len(sizes) == 1:
		return layout(sizes, x, y, dx, dy)
	
	# figure out where 'split' should be
	i = 1
	while i < len(sizes) and worst_ratio(sizes[:i], x, y, dx, dy) >= worst_ratio(sizes[:(i+1)], x, y, dx, dy):
		i += 1
	current = sizes[:i]
	remaining = sizes[i:]
	
	(leftover_x, leftover_y, leftover_dx, leftover_dy) = leftover(current, x, y, dx, dy)
	return layout(current, x, y, dx, dy) + \
			squarify(remaining, leftover_x, leftover_y, leftover_dx, leftover_dy)

def padded_squarify(sizes, x, y, dx, dy):
	rects = squarify(sizes, x, y, dx, dy)
	for rect in rects:
		pad_rectangle(rect)
	return rects

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
	

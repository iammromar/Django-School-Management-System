import random

def generate_colors(n):
	colors = list()
	for i in range(n):
		while True:
			color = "#"+"%06x" % random.randint(0, 0xFFFFFF)
			if not color in colors:
				colors.append(color)
				break
	return colors
try:
	import Image, ImageFilter
except ImportError:
	from PIL import Image, ImageFilter
import random
import string
import argparse

black_pixel = (0, 0, 0, 255)
white_pixel = (255, 255, 255, 255)

# Generates names for output files
def id_generator(size=5, chars=string.ascii_lowercase + string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

def intensity(pixel):
	return pixel[0] + pixel[1] + pixel[2]

# Sorts a given row of pixels
def sort_interval(interval):
	if interval == []:
		return []
	else:
		return(sorted(interval, key = intensity))

# Generates random widths for intervals. Used by int_random()
def random_width(clength):
	x = random.random()
	# width = int(200*(1-(1-(x-1)**2)**0.5))
	width = int(clength*(1-x))
	# width = int(50/(x+0.1))
	return(width)

# Functions starting with int return intervals according to which to sort
def int_edges(pixels, args):
	img = Image.open(args.image)
	img = img.rotate(args.angle, expand = True)
	edges = img.filter(ImageFilter.FIND_EDGES)
	edges = edges.convert('RGBA')
	edge_data = edges.load()

	filter_pixels = []
	edge_pixels = []
	intervals = []

	print("Defining edges...")
	for y in range(img.size[1]):
		filter_pixels.append([])
		for x in range(img.size[0]):
			filter_pixels[y].append(edge_data[x, y])

	print("Thresholding...")
	for y in range(len(pixels)):
		edge_pixels.append([])
		for x in range(len(pixels[0])):
			if filter_pixels[y][x][0] + filter_pixels[y][x][1] + filter_pixels[y][x][2] < args.threshold:
				edge_pixels[y].append(white_pixel)
			else:
				edge_pixels[y].append(black_pixel)

	print("Cleaning up edges...")
	for y in range(len(pixels)-1,1,-1):
		for x in range(len(pixels[0])-1,1,-1):
			if edge_pixels[y][x] == black_pixel and edge_pixels[y][x-1] == black_pixel:
				edge_pixels[y][x] = white_pixel

	print("Defining intervals...")
	for y in range(len(pixels)):
		intervals.append([])
		for x in range(len(pixels[0])):
			if edge_pixels[y][x] == black_pixel:
				intervals[y].append(x)
		intervals[y].append(len(pixels[0]))
	return(intervals)

def int_threshold(pixels, args):
	intervals = []

	print("Defining intervals...")
	for y in range(len(pixels)):
		intervals.append([])
		for x in range(len(pixels[0])):
			if intensity(pixels[y][x]) < args.threshold or intensity(pixels[y][x]) > args.upper_threshold:
				intervals[y].append(x)
		intervals[y].append(len(pixels[0]))
	return(intervals)

def int_random(pixels, args):
	intervals = []

	print("Defining intervals...")
	for y in range(len(pixels)):
		intervals.append([])
		x = 0
		while True:
			width = random_width(args.clength)
			x += width
			if x > len(pixels[0]):
				intervals[y].append(len(pixels[0]))
				break
			else:
				intervals[y].append(x)
	return(intervals)

def int_waves(pixels, args):
	intervals = []

	print("Defining intervals...")
	for y in range(len(pixels)):
		intervals.append([])
		x = 0
		while True:
			width = args.clength + random.randint(0,10)
			x += width
			if x > len(pixels[0]):
				intervals[y].append(len(pixels[0]))
				break
			else:
				intervals[y].append(x)
	return(intervals)

def int_file(pixels, args):
	intervals = []
	file_pixels = []

	img = Image.open(args.int_file)
	img = img.convert('RGBA')
	data = img.load()
	for y in range(img.size[1]):
		file_pixels.append([])
		for x in range(img.size[0]):
			file_pixels[y].append(data[x, y])

	print("Cleaning up edges...")
	for y in range(len(pixels)-1,1,-1):
		for x in range(len(pixels[0])-1,1,-1):
			if file_pixels[y][x] == black_pixel and file_pixels[y][x-1] == black_pixel:
				file_pixels[y][x] = white_pixel

	print("Defining intervals...")
	for y in range(len(pixels)):
		intervals.append([])
		for x in range(len(pixels[0])):
			if file_pixels[y][x] == black_pixel:
				intervals[y].append(x)
		intervals[y].append(len(pixels[0]))

	return intervals

def int_file_edges(pixels, args):
	img = Image.open(args.int_file)
	img = img.rotate(args.angle, expand = True)
	img = img.resize((len(pixels[0]), len(pixels)), Image.ANTIALIAS)
	edges = img.filter(ImageFilter.FIND_EDGES)
	edges = edges.convert('RGBA')
	edge_data = edges.load()

	filter_pixels = []
	edge_pixels = []
	intervals = []

	print("Defining edges...")
	for y in range(img.size[1]):
		filter_pixels.append([])
		for x in range(img.size[0]):
			filter_pixels[y].append(edge_data[x, y])

	print("Thresholding...")
	for y in range(len(pixels)):
		edge_pixels.append([])
		for x in range(len(pixels[0])):
			if filter_pixels[y][x][0] + filter_pixels[y][x][1] + filter_pixels[y][x][2] < args.threshold:
				edge_pixels[y].append(white_pixel)
			else:
				edge_pixels[y].append(black_pixel)

	print("Cleaning up edges...")
	for y in range(len(pixels)-1,1,-1):
		for x in range(len(pixels[0])-1,1,-1):
			if edge_pixels[y][x] == black_pixel and edge_pixels[y][x-1] == black_pixel:
				edge_pixels[y][x] = white_pixel

	print("Defining intervals...")
	for y in range(len(pixels)):
		intervals.append([])
		for x in range(len(pixels[0])):
			if edge_pixels[y][x] == black_pixel:
				intervals[y].append(x)
		intervals[y].append(len(pixels[0]))
	return(intervals)

def int_none(pixels, args):
	intervals = []
	for y in range(len(pixels)):
		intervals.append([len(pixels[y])])
	return(intervals)

# Sorts the image
def sort_image(pixels, intervals, args):
	print("Sorting intervals...")
	# Hold sorted pixels
	sorted_pixels=[]
	for y in range(len(pixels)):
		row=[]
		xMin = 0
		for xMax in intervals[y]:
			interval = []
			for x in range(xMin, xMax):
				interval.append(pixels[y][x])
			if random.randint(0,100) >= args.randomness:
				row = row + sort_interval(interval)
			else:
				row = row + interval
			xMin = xMax
		row.append(pixels[y][0]) # wat
		sorted_pixels.append(row)
	return(sorted_pixels)

def main():
	p = argparse.ArgumentParser(description = "pixel mangle an image")
	p.add_argument("image", help = "input image file")
	p.add_argument("-o", "--output", help = "output image file, defaults to a randomly generated string")
	p.add_argument("-i", "--int_function", help = "random, edges, waves, file, none", default = "random")
	p.add_argument("-f", "--int_file", help = "image for intervals", default = "in.png")
	p.add_argument("-t", "--threshold", type = int, help = "between 0 and 255*3", default = 100)
	p.add_argument("-u", "--upper_threshold", type = int, help = "between 0 and 255*3", default = 400)
	p.add_argument("-c", "--clength", type = int, help = "characteristic length", default = 50)
	p.add_argument("-a", "--angle", type = float, help = "rotate the image by an angle before sorting", default = 0)
	p.add_argument("-r", "--randomness", type = float, help = "what % of intervals are NOT sorted", default = 0)
	args = p.parse_args()

	print("Randomness =", args.randomness, "%")
	print("Threshold =", args.threshold)
	print("Characteristic length = ", args.clength)

	# Get function to define intervals from command line arguments
	try:	
		int_function = {
			"random": int_random,
			"threshold": int_threshold,
			"edges": int_edges,
			"waves": int_waves,
			"file": int_file,
			"file-edges": int_file_edges,
			"none": int_none}[args.int_function]
	except KeyError:
		print("[WARNING] Invalid interval function specified, defaulting to 'random'. Try one of [random, edges, waves, file, none]")
		int_function = int_random

	# If given an output image name, use that. Else generate a random one
	if args.output:
		outputImage = args.output
	else:
		outputImage = id_generator()+".png"

	print("Opening image...")
	img = Image.open(args.image)
	img.convert('RGBA')
	img = img.rotate(args.angle, expand = True)

	print("Getting data...")
	data = img.load()
	new = Image.new('RGBA', img.size)

	pixels = []

	print("Getting pixels...")
	for y in range(img.size[1]):
		pixels.append([])
		for x in range(img.size[0]):
			pixels[y].append(data[x, y])

	intervals = int_function(pixels, args)
	sorted_pixels = sort_image(pixels, intervals, args)

	print("Placing pixels...")
	for y in range(img.size[1]):
		for x in range(img.size[0]):
			new.putpixel((x, y), sorted_pixels[y][x])

	new = new.rotate(-args.angle)
	print("Saving image...")
	new.save(outputImage)
	print("Done!", outputImage)


if __name__ == "__main__":
	main()
from sys import argv
from re import compile

class Pol():

	sign = None
	num = 0
	x = False
	power = 0

	def __init__(self, m, sign = None, num = 0.0, x = False, power = 0):
		self.sign = sign
		self.num = num
		self.x = x
		self.power = power
		if m != None:
			if len(m.group(1)) > 0:
				self.sign = m.group(1)
				if self.sign == '=':
					raise
			if m.group(2) == None:
				self.num = 1.0
			else:
				self.num = float(m.group(2))
			if m.group(3) != None:
				self.x = True
				if m.group(4) != None:
					self.power = int(m.group(4))
				else:
					self.power = 1
		if self.num < 0.0:
			self.sign = "+" if self.sign == "-" else "-"
			self.num = -self.num
		if self.x and self.power == 0:
			self.x = False

	def getNum(self):
		if self.sign == "-":
			return -self.num
		return self.num

	def toString(self):
		s = ""
		if self.sign != None:
			s += self.sign
			s += " "
		if self.x and (self.num == 1 or self.num == -1) and self.power != 0:
			if self.power == 1:
				s += "X"
			else:
				s += "X^%d" % (self.power)
		elif self.x and self.num != 0 and self.power != 0:
			if self.power == 1:
				s += "%sX" % str(self.num)
			else:
				s += "%sX^%d" % (str(self.num), self.power)
		else:
			s += str(self.num)
		return s


reg_pol = compile('([-+=]?)\s*([0-9\.]+)?(\s*\*?\s*[xX](?:\s*\^\s*([0-9]+))?)?\s*')
reg_space = compile('\s+')


class Cmp():

	left = []
	right = []

	def __init__(self):
		self.left = []
		self.right = []

	def parse(self, eq):
		pos = 0
		left = True
		while pos < len(eq):
			if eq[pos:pos + 1] == "=" and left and len(self.left) > 0:
				left = False
				pos += 1
			m = reg_space.match(eq, pos)
			if m != None:
				pos += len(m.group(0))
				continue
			m = reg_pol.match(eq, pos)
			if m == None or len(m.group(0)) <= 0:
				print("Unexpected syntax: '%s'" % (eq[pos:pos + 5]))
				return False
			try:
				p = Pol(m)
				if p.sign == None:
					if left and len(self.left) > 0:
						p.sign = "+"
					elif not left and len(self.right) > 0:
						p.sign = "+"
			except:
				print("Invalid syntax: '%s'" % (eq[pos:pos + 5]))
				return False
			if left:
				self.left.append(p)
			else:
				self.right.append(p)
			pos += len(m.group(0))
		if len(self.left) == 0:
			if len(self.right) == 0:
				print("Bad argument")
				return False
			self.left.append(Pol(None))
		if len(self.right) == 0:
			self.right.append(Pol(None))
		print("Equation: " + self.toString() + "")
		return True

	def reduce(self):
		tmp = {}
		for p in self.left:
			if not p.power in tmp:
				tmp[p.power] = 0.0
			tmp[p.power] += p.num if p.sign != "-" else -p.num
		for p in self.right:
			if not p.power in tmp:
				tmp[p.power] = 0.0
			tmp[p.power] -= p.num if p.sign != "-" else -p.num
		self.left = []
		for power in sorted(tmp):
			if tmp[power] != 0:
				self.left.append(Pol(None, "+" if len(self.left) > 0 else None, tmp[power], True, power))
		self.right = [Pol(None)]
		if len(self.left) == 0:
			self.left.append(Pol(None))
		print("Reduced form: " + self.toString() + "")
		return True

	def resolve(self):
		degree = 0
		for p in self.left:
			if p.power > degree:
				degree = p.power
		print("Polynomial degree: %d" % degree)
		if degree == 0:
			a = self.left[0].getNum()
			if a == 0:
				print("\033[32mEvery real are solution\033[39m")
			else:
				print("No solution")
			return False
		elif degree == 1:
			if len(self.left) > 1:
				b = self.left[0].getNum()
				a = self.left[1].getNum()
			else:
				b = 0
				a = self.left[0].getNum()
			print("\033[94ma = " + str(a) + "\033[39m")
			print("\033[94mb = " + str(b) + "\033[39m")
			print("The solution is:")
			print("\033[94m-b / a = \033[32m" + str(-b / a) + "\033[39m")
		elif degree == 2:
			if len(self.left) > 2:
				c = self.left[0].getNum()
				b = self.left[1].getNum()
				a = self.left[2].getNum()
			elif len(self.left) > 1:
				c = 0
				b = self.left[0].getNum()
				a = self.left[1].getNum()
			else:
				c = 0
				b = 0
				a = self.left[0].getNum()
			print("\033[94ma = " + str(a) + "\033[39m")
			print("\033[94mb = " + str(b) + "\033[39m")
			print("\033[94mc = " + str(c) + "\033[39m")
			d = b ** 2 - (4 * a * c)
			print("\033[94md = " + str(d) + "\033[39m")
			if d > 0:
				print("Discriminant is strictly positive, the two solutions are:")
				print("\033[94m(-b - (d ** 0.5)) / (2 * a) = \033[32m" + str((-b - (d ** 0.5)) / (2 * a)) + "\033[39m")
				print("\033[94m(-b + (d ** 0.5)) / (2 * a) = \033[32m" + str((-b + (d ** 0.5)) / (2 * a)) + "\033[39m")
			else:
				if d == 0:
					print("Discriminant is 0, the solution is:")
					print("\033[94m-b / (2 * a) = \033[32m" + str(-b / (2 * a)))
				else:
					print("Discriminant is strictly negative, the two solutions are:")
					print("\033[94m(-b - (d ** 0.5)) / (2 * a) = \033[32m" + str((-b - (abs(d) ** 0.5)) / (2 * a)) + "i\033[39m")
					print("\033[94m(-b + (d ** 0.5)) / (2 * a) = \033[32m" + str((-b + (abs(d) ** 0.5)) / (2 * a)) + "i\033[39m")
		else:
			print("\033[31mThe polynomial degree is strictly greater than 2, I can't solve.\033[39m")
			return False
		return True

	def toString(self):
		s = ""
		for p in self.left:
			s += p.toString()
			s += " "
		s += "="
		for p in self.right:
			s += " "
			s += p.toString()
		return s


if len(argv) <= 1:
	print("Not enough argument")
else:
	c = Cmp()
	if not c.parse(argv[1]):
		exit(1)
	if not c.reduce():
		exit(1)
	if not c.resolve():
		exit(1)


MAXN = 10


fs = [1] * MAXN
for i in range(1, MAXN):
	fs[i] = fs[i - 1] * i

def CNK(n, k):
	return fs[n] / fs[k] / fs[n - k]

def EGK(n, k, p):
	res = 0
	for i in range(k, n + 1):
		res += CNK(n, i) * p**i * (1 - p)**(n - i)

	return round(res, 3)


for j in range(MAXN):
	if j == 0:
		print('k\\n', end='\t')
	else:
		print(j, end='\t')
print()

for i in range(1, MAXN):
	for j in range(MAXN):
		if j == 0:
			print('c', end='\t')
		else:
			print('%.3f' % (EGK(j, i, 1/6)), end='\t')
	print()
	for j in range(MAXN):
		if j == 0:
			print(i, end='\t')
		else:
			print('%.3f' % (EGK(j, i, 1/3)), end='\t')
	print()
	for j in range(MAXN):
		if j == 0:
			print('b', end='\t')
		else:
			print('%.3f' % (EGK(j, i, 0.5)), end='\t')
	print('\n')

import numpy as np
import numpy.linalg as linalg


x = np.array([
    [58667.1018910160, 52641.1482015879],
    [59314.08378057551, 52641.1482015879],
    [58667.101891016,  54258.7020170489],
    [59314.0837805755, 54258.7020170489],
])

xp = np.array([
    [97575.2, 36805.3],
    [97575.2, 36707.9],
    [97158.2, 36805.3],
    [97158.2, 36707.9],
])


print('x = {}'.format(x))
print('xp = {}'.format(xp))

X = np.kron(np.eye(2), np.concatenate((x, np.ones((x.shape[0], 1))), axis=1))
b = np.concatenate((xp[:, 0], xp[:, 1])).reshape((2*x.shape[0], 1))

print('X = {}'.format(X))
print('b = {}'.format(b))

a,residuals,rank,s = linalg.lstsq(X, b)

print('a = {}'.format(a))
print('residuals = {}'.format(residuals))

A = np.array([
    [a[0,0], a[1,0], a[2,0]],
    [a[3,0], a[4,0], a[5,0]],
    [0, 0, 1],
])

# A is now the affine transformation matrix that maps from x to xp
print('A = {}'.format(A))

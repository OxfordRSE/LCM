import numpy as np
import numpy.linalg as linalg


x = np.array([
    [7172.65, 1668.36],
    [7361.75, 33101.97],
    [35524.50, 19594.92],
    [80045.19, 34312.90],
    [80301.21, 849.74],
])

xp = np.array([
    [109764.1, 25495.6],
    [94014.2, 25571.1],
    [100832.4, 39688.6],
    [93454.2, 62110.4],
    [110222.6, 62199.8],
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

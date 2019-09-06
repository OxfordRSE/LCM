import numpy as np
import numpy.linalg as linalg

x = np.array([
    [6907.52105990312, 6145.133917411616],
    [7197.657134796724, 6145.133917411616],
    [7197.657134796724, 6461.148600206306],
    [6907.52105990312, 6461.148600206306],
])

xp = np.array([
    [105464.7, 37220.8],
    [106107.2, 37220.8],
    [106107.2, 37807.3],
    [105464.7, 37807.3],
])

x = np.array([
    [0.0,0.0],
    [169319.0,0.0],
    [169319.0, 76903.0],
    [0.0,76903.0],
])

xp = np.array([
    [147499.2,62498.9],
    [56243.8,62498.9],
    [56240.6,13267.5],
    [147498.5,13267.3],
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

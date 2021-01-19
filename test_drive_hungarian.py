from hungarian.hungarian import Hungarian

# matrix = [[2 for i in range(4)] for j in range(3)]
# [j][i] row, column
# matrix[0][0] = 1
# matrix[1][1] = 1
# matrix[2][3] = 1

matrix = [[2 for i in range(3)] for j in range(4)]
# [j][i] row, column
matrix[0][0] = 1
matrix[1][1] = 1
matrix[3][2] = 1

print(matrix)

hung = Hungarian(matrix)
hung.calculate()

# print(Hungarian.padMatrix(matrix)) I've been lied to, padMatrix doesn't exist
# but by testing we know that the behaviour will be what we want

print(hung.get_results())

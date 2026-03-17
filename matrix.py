import numpy as np


def solve_matrix_equation_6x6(A, b):
    if A.shape != (6, 6) or b.shape != (6, 1):
        raise ValueError("Матрица R должна быть 6x6, а вектор E - 6x1 (вертикальный).")

    print("Промежуточные вычисления")

    det_A = np.linalg.det(A)
    print(f"Определитель матрицы R (det(R)): {det_A:.2f}")

    if np.isclose(det_A, 0):
        print("\nОшибка: Матрица R вырождена, det(A) ≈ 0.")
        print("Решение через обратную матрицу невозможно.")
        return None

    A_inv = np.linalg.inv(A)
    print("\nОбратная матрица R_inv (A^-1):")
    print(A_inv)

    x = np.dot(A_inv, b)
    print("\n Решение I = R_inv * E:")

    return x


def calculate_power_balance(I_vector, R_dict, E_dict):
    # Расчет баланса мощностей

    print("Расчет Баланса Мощностей")

    pow_R_losses = 0.0
    for i in range(len(I_vector)):
        R_key = f'R{i + 1}'
        R_val = R_dict.get(R_key, 0.0)
        pow_R_losses += R_val * (I_vector[i] ** 2)

    pow_E_sources = 0.0
    for i in range(len(I_vector)):
        E_key = f'E{i + 1}'
        E_val = E_dict.get(E_key, 0.0)
        pow_E_sources += E_val * I_vector[i]
    difference = pow_R_losses - pow_E_sources

    print(f"LHS: {pow_R_losses:} Вт")
    print(f"RHS: {pow_E_sources:} Вт")
    print(f"Разница (LHS - RHS): {difference:} Вт")

    if np.isclose(difference, 0, atol=1e-5):
        print("Баланс мощностей ВЫПОЛНЕН.")
    else:
        print("Баланс мощностей НЕ ВЫПОЛНЕН.")


def solve_mkt_3x3(R_dict, E_dict):
    print("Расчет Методом Контурных Токов")

    R1, R2, R3 = R_dict['R1'], R_dict['R2'], R_dict['R3']
    R4, R5, R6 = R_dict['R4'], R_dict['R5'], R_dict['R6']
    E3, E6 = E_dict['E3'], E_dict['E6']

    A_mkt = np.array([
        [(R1 + R2 + R4), -R2, -R4],
        [-R2, (R2 + R3 + R5), -R5],
        [-R4, -R5, (R4 + R5 + R6)]
    ])

    b_mkt = np.array([0, -E3, -E6]).reshape((3, 1))
    print("Матрица A (МКТ):")
    print(A_mkt)
    print("\nВектор b (МКТ):")
    print(b_mkt)

    try:
        Ik_solution = np.linalg.solve(A_mkt, b_mkt)
        print("\nРешение Ik (Контурные токи Ik1, Ik2, Ik3):")
        print(np.round(Ik_solution, decimals=4))
    except np.linalg.LinAlgError:
        print("\nОшибка: Матрица МКТ вырождена")
        return

    Ik1, Ik2, Ik3 = Ik_solution.flatten()
    I_branches = np.zeros(6)

    I_branches[0] = Ik1
    I_branches[1] = Ik2 - Ik1
    I_branches[2] = -Ik2
    I_branches[3] = -Ik1 + Ik3
    I_branches[4] = -Ik2 + Ik3
    I_branches[5] = -Ik3

    print("\nПересчет в Токи ветвей (I1-I6):")
    print(np.round(I_branches.reshape((6, 1)), decimals=4))

    print("\n Проверка баланса мощностей")

    pow_R_losses = sum(R_dict[f'R{i + 1}'] * (I_branches[i] ** 2) for i in range(6))
    pow_E_sources = sum(E_dict[f'E{i + 1}'] * I_branches[i] for i in range(6))  # пассивная конвенция
    difference = pow_R_losses - pow_E_sources

    print(f"LHS (R·I²): {pow_R_losses:} Вт")
    print(f"RHS (E·I): {pow_E_sources:} Вт")
    print(f"Разница (LHS - RHS): {difference:.6e} Вт")

    if np.isclose(difference, 0, atol=1e-5):
        print("Баланс мощностей ВЫПОЛНЕН.")
    else:
        print("Баланс мощностей НЕ ВЫПОЛНЕН.")

    return I_branches


A = np.array([
    [-1, 0, 0, -1, 0, -1],
    [1, 1, 1, 0, 0, 0],
    [0, 0, -1, 0, 1, 1],
    [0, 79, -91, 0, -40, 0],
    [0, 0, 0, 3, 40, -67],
    [71, -79, 0, -3, 0, 0]
])

b = np.array([0, 0, 0, -25, -28, 0]).reshape((6, 1))

CIRCUIT_R = {
    'R1': 43.0, 'R2': 32.0, 'R3': 82.0,
    'R4': 6.0, 'R5': 44.0, 'R6': 55.0
}
CIRCUIT_E = {
    'E1': 0.0, 'E2': 0.0, 'E3': 0.0,
    'E4': 2.0, 'E5': 0.0, 'E6': 9.0
}


def matrix_3x3_mup(R_dict, E_dict):
    R = R_dict
    E = E_dict

    r1, r2, r3, r4, r5, r6 = R.values()
    e1, e2, e3, e4, e5, e6 = E.values()

    g = {f'g{i + 1}': 1.0 / val for i, val in enumerate(R.values())}
    g1, g2, g3, g4, g5, g6 = g.values()
    G_matrix = ([
        [g1 + g4 + g6, -g1, -g6],
        [-g1, g1 + g2 + g3, -g3],
        [-g6, -g3, g3 + g5 + g6]
    ])
    J_source_vector = np.array([
        - (e1 * g1) - (e4 * g4) - (e6 * g6),
        (e1 * g1) + (e2 * g2) + (e3 * g3),
        (e5 * g5) - (e3 * g3) + e6 * g6
    ]).reshape((3, 1))

    print(" Матрица G:")
    print(G_matrix)
    print("\n Вектор J:")
    print(J_source_vector)

    try:
        Phi_solution = np.linalg.solve(G_matrix, J_source_vector)
        print("\nПотенциалы (Phi_A, Phi_B, Phi_C):")
        print(np.round(Phi_solution, decimals=4))
    except np.linalg.LinAlgError:
        print("\nОшибка: Матрица вырождена")
        return None

    phi_A, phi_B, phi_C = Phi_solution.flatten()
    phi_D = 0.0
    I_branches = np.zeros(6)
    I_branches[0] = (phi_A - phi_B + e1) / r1
    I_branches[1] = (phi_D - phi_B + e2) / r2
    I_branches[2] = (phi_C - phi_B + e3) / r3
    I_branches[3] = (phi_A - phi_D + e4) / r4
    I_branches[4] = (phi_D - phi_C + e5) / r5
    I_branches[5] = (phi_A - phi_C + e6) / r6
    print("\n Пересчет в Токи ветвей (I1-I6):")
    print(np.round(I_branches.reshape((6, 1)), decimals=4))
    calculate_power_balance(I_branches, R_dict, E_dict)

    return I_branches


print("Матрица коэффициентов R:")
print(A)
print("\nВектор правой части E:")
print(b)
solution_x = solve_matrix_equation_6x6(A, b)
print("\nРешение токов I:", solution_x)
calculate_power_balance(solution_x, CIRCUIT_R, CIRCUIT_E)

solve_mkt_3x3(CIRCUIT_R, CIRCUIT_E)
matrix_3x3_mup(CIRCUIT_R, CIRCUIT_E)

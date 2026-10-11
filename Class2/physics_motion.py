import numpy as np
import matplotlib.pyplot as plt


def uniform_motion(v0, t):
    s = v0 * t
    return s


def uniform_accelerated_motion(v0, a, t):
    s = v0 * t + 0.5 * a * t**2
    return s


def motion_with_air_resistance(v0, k, m, t):
    def velocity(t):
        return (v0 - m * 9.8 / k) * np.exp(-k * t / m) + m * 9.8 / k

    def displacement(t):
        return m / k * (v0 - m * 9.8 / k) * (1 - np.exp(-k * t / m)) + m * 9.8 / k * t

    return displacement(t), velocity(t)


def plot_displacement_time():
    t = np.linspace(0, 10, 200)

    plt.figure(figsize=(12, 8))

    plt.subplot(2, 2, 1)
    v0_uniform = 5.0
    s_uniform = uniform_motion(v0_uniform, t)
    plt.plot(t, s_uniform, 'b-', linewidth=2)
    plt.xlabel('Time (s)')
    plt.ylabel('Displacement (m)')
    plt.title('Uniform Linear Motion (v = constant)')
    plt.grid(True)

    plt.subplot(2, 2, 2)
    v0_accel = 2.0
    a_accel = 3.0
    s_accel = uniform_accelerated_motion(v0_accel, a_accel, t)
    plt.plot(t, s_accel, 'r-', linewidth=2)
    plt.xlabel('Time (s)')
    plt.ylabel('Displacement (m)')
    plt.title('Uniformly Accelerated Motion (a = constant)')
    plt.grid(True)

    plt.subplot(2, 2, 3)
    v0_air = 20.0
    k = 0.5
    m = 2.0
    s_air, v_air = motion_with_air_resistance(v0_air, k, m, t)
    plt.plot(t, s_air, 'g-', linewidth=2)
    plt.xlabel('Time (s)')
    plt.ylabel('Displacement (m)')
    plt.title('Motion with Air Resistance')
    plt.grid(True)

    plt.subplot(2, 2, 4)
    plt.plot(t, s_uniform, 'b-', linewidth=2, label='Uniform (v=5m/s)')
    plt.plot(t, s_accel, 'r-', linewidth=2, label='Accelerated (a=3m/s²)')
    plt.plot(t, s_air, 'g-', linewidth=2, label='Air Resistance')
    plt.xlabel('Time (s)')
    plt.ylabel('Displacement (m)')
    plt.title('Comparison of Three Motion Types')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    print("=" * 50)
    print("Physics Motion Analysis - Function Demonstration")
    print("=" * 50)

    print("\n1. Uniform Linear Motion:")
    print("   Relationship: s = v * t")
    print("   (Velocity constant, acceleration = 0)")
    print(f"   When v = 5 m/s, t = 10 s => s = {uniform_motion(5.0, 10):.2f} m")

    print("\n2. Uniformly Accelerated Motion:")
    print("   Relationship: s = v0*t + (1/2)*a*t²")
    print("   (Acceleration constant)")
    print(f"   When v0 = 2 m/s, a = 3 m/s², t = 10 s => s = {uniform_accelerated_motion(2.0, 3.0, 10):.2f} m")

    print("\n3. Motion with Air Resistance:")
    print("   Relationship: dv/dt = g - (k/m)*v")
    print("   (Terminal velocity reached when dv/dt = 0)")
    v_terminal = 9.8 * 2.0 / 0.5
    print(f"   Terminal velocity = m*g/k = {v_terminal:.2f} m/s")

    print("\n" + "=" * 50)
    print("Generating displacement-time plots...")
    print("=" * 50)

    plot_displacement_time()

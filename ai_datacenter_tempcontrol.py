import matplotlib.pyplot as plt
import numpy as np


class DataCenterThermalAgent:

    def __init__(self, target_temp=65.0, critical_temp=85.0):
        self.target_temp = target_temp
        self.critical_temp = critical_temp
        self.energy_consumed = 0.0
        self.action_history = []

    def evaluate_utility_and_act(self, cpu_temp, workload, ambient_temp):
        """Goal-Based / Utility-Based Agent Logic.

        Balances the trade-off between thermal safety (U_thermal) and energy
        conservation (U_energy).
        """
        # Default safety defaults
        cooling_power = 0.0  # Percentage (0 to 100%)
        throttle_workload = False
        action_label = "Optimal Rest"

        # Situation 1: Critical Emergency (Temperature approaching meltdown)
        if cpu_temp >= self.critical_temp:
            cooling_power = 100.0
            throttle_workload = True
            action_label = "EMERGENCY: Max Cooling + Workload Throttle"

        # Situation 2: Above target temperature (Active management needed)
        elif cpu_temp > self.target_temp:
            # Calculate deviation from target
            deviation = cpu_temp - self.target_temp

            # Utility scaling: If ambient temp or workload is high, ramp up faster
            if ambient_temp > 32 or workload > 80:
                cooling_power = min(100.0, deviation * 4.5)
                action_label = "Proactive High Cooling"
            else:
                cooling_power = min(100.0, deviation * 2.5)
                action_label = "Standard Precision Cooling"

        # Situation 3: Safe Zone
        else:
            if ambient_temp > 30:
                cooling_power = 15.0  # Baseline circulation for external heat
                action_label = "Ambient Mitigation"
            else:
                cooling_power = 5.0  # Idle eco-mode
                action_label = "Eco-Idle"

        # Track metrics
        self.energy_consumed += cooling_power * 0.1  # Simplified power consumption formula
        self.action_history.append(cooling_power)

        return action_label, cooling_power, throttle_workload


if __name__ == "__main__":

    agent = DataCenterThermalAgent(target_temp=60.0, critical_temp=80.0)

    # Initialize Agent
    agent = DataCenterThermalAgent(target_temp=60.0, critical_temp=80.0)

    # Time configuration (24 hours simulated in 15-minute intervals = 96 steps)
    intervals = np.arange(1, 97)
    hours_axis = intervals * 0.25

    # 1. Environment Generation: Diurnal Outside Temperature
    ambient_temps = 22 + 12 * np.sin((hours_axis - 8) * np.pi / 12) + np.random.normal(0, 0.5, 96)

    # 2. Environment Generation: Mid-day User Traffic Spike (Workload %)
    workloads = 20 + 65 * np.exp(-((hours_axis - 14) ** 2) / 12) + np.random.normal(0, 2, 96)
    workloads = np.clip(workloads, 5, 100)

    # Initial State
    cpu_temperature = 50.0

    # History logs for plotting
    history_cpu_temp = []
    history_workload = []
    history_cooling_power = []
    history_ambient = []

    print(f"{'Hour':<6} | {'CPU Temp (°C)':<14} | {'Workload (%)':<13} | {'Cooling Action Taken':<40}")
    print("-" * 83)

    # Simulation Loop
    for idx, t in enumerate(hours_axis):
        amb = ambient_temps[idx]
        work = workloads[idx]

        # Environmental Step: Compute heat generation
        # Heat added depends directly on workload intensity and outside ambient heat leak
        heat_generated = (work * 0.45) + (amb * 0.15)
        cpu_temperature += heat_generated

        # Agent Step: Intervene based on current perception
        action, cooling_output, throttled = agent.evaluate_utility_and_act(
            cpu_temperature, work, amb
        )

        # Apply Agent Action adjustments to the environment
        if throttled:
            work = work * 0.5  # Forced mitigation drop

        # Cooling application reducing temperature
        cooling_effect = cooling_output * 0.35
        cpu_temperature = max(20.0, cpu_temperature - cooling_effect)

        # Log updates to terminal for specific key hours (Every 2 hours)
        if idx % 8 == 0:
            print(
                f"{t:<6.2f} | {cpu_temperature:<14.1f} | {work:<13.1f} | {action:<40}"
            )

        # Save history
        history_cpu_temp.append(cpu_temperature)
        history_workload.append(work)
        history_cooling_power.append(cooling_output)
        history_ambient.append(amb)

    print("-" * 83)
    print(f"Simulation Complete. Total Agent HVAC Energy Consumed: {agent.energy_consumed:.2f} kWh")

    # --- Visualization Processing ---
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 8), sharex=True)

    # Top Plot: System States
    ax1.plot(hours_axis, history_cpu_temp, "r-", label="CPU Core Temp (°C)", linewidth=2.5)
    ax1.plot(hours_axis, history_workload, "k--", label="Server Workload Max (%)", alpha=0.5)
    ax1.plot(hours_axis, history_ambient, "orange", linestyle=":", label="Outside Ambient (°C)", alpha=0.7)
    ax1.axhline(80, color="darkred", linestyle="-.", alpha=0.7, label="Critical Ceiling (80°C)")
    ax1.axhline(60, color="green", linestyle="--", alpha=0.5, label="Target Safe Ceiling (60°C)")

    ax1.set_ylabel("Thermal & Load Metrics")
    ax1.set_title("AI Agent Data Center Thermal & Workload Management Matrix")
    ax1.legend(loc="upper left", frameon=True)
    ax1.grid(True, alpha=0.25)

    # Bottom Plot: Actuator Responses
    ax2.fill_between(hours_axis, history_cooling_power, color="teal", alpha=0.3, label="Cooling Output Intensity")
    ax2.plot(hours_axis, history_cooling_power, color="teal", linewidth=1.5)
    ax2.set_xlabel("Time Horizon (24-Hour Timeline)")
    ax2.set_ylabel("HVAC Pump & Fan Output (%)")
    ax2.set_xlim(1, 24)
    ax2.set_xticks(np.arange(1, 25))
    ax2.legend(loc="upper right")
    ax2.grid(True, alpha=0.25)

    plt.tight_layout()
    plt.savefig("datacenter_thermal_simulation.png", dpi=300)
    print("Analytics visual graph plotted and saved successfully as 'datacenter_thermal_simulation.png'.")
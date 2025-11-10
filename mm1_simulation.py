import simpy
import random
import statistics

RANDOM_SEED = 42
MU = 2.0  # service rate (kunder per minut), medelservicetid = 0.5 min
SIM_TIME = 480  # minuter, t.ex. 8 timmar
LAMBDA_VALUES = [0.5, 1.0, 1.5, 1.8]  # ankomsttakter (kunder per minut)


def customer(env, name, server, mu, waiting_times, busy_time_tracker):
    arrival_time = env.now
    with server.request() as req:
        yield req
        service_start = env.now
        waiting_times.append(service_start - arrival_time)

        service_time = random.expovariate(mu)
        busy_start = env.now
        yield env.timeout(service_time)
        busy_end = env.now
        busy_time_tracker[0] += (busy_end - busy_start)


def arrival_process(env, lam, server, mu, waiting_times, busy_time_tracker):
    i = 0
    while True:
        interarrival = random.expovariate(lam)
        yield env.timeout(interarrival)
        i += 1
        env.process(customer(env, f"Cust{i}", server, mu, waiting_times, busy_time_tracker))


def run_simulation(lam, mu, sim_time):
    random.seed(RANDOM_SEED)
    env = simpy.Environment()
    server = simpy.Resource(env, capacity=1)

    waiting_times = []
    busy_time_tracker = [0.0]

    env.process(arrival_process(env, lam, server, mu, waiting_times, busy_time_tracker))
    env.run(until=sim_time)

    avg_wait = statistics.mean(waiting_times) if waiting_times else 0.0
    utilization = busy_time_tracker[0] / sim_time
    return avg_wait, utilization


def main():
    print("λ (cust/min)\tAvg wait (min)\tUtilization")
    for lam in LAMBDA_VALUES:
        avg_wait, util = run_simulation(lam, MU, SIM_TIME)
        print(f"{lam:.2f}\t\t{avg_wait:.3f}\t\t{util:.3f}")


if __name__ == "__main__":
    main()

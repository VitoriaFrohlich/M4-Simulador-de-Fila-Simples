import heapq
from dataclasses import dataclass


class RandomGenerator:
    def __init__(
        self,
        seed=123456789,
        a=1664525,
        c=1013904223,
        m=2**32,
        limit=100000
    ):
        self.previous = seed
        self.a = a
        self.c = c
        self.m = m
        self.limit = limit
        self.used = 0

    def next_random(self):
        """Retorna um número pseudoaleatório entre 0 e 1."""
        if self.used >= self.limit:
            raise RuntimeError("Limite de números aleatórios atingido.")

        self.previous = (
            self.a * self.previous + self.c
        ) % self.m

        self.used += 1

        return self.previous / self.m


@dataclass(order=True)
class Event:
    time: float
    sequence: int
    event_type: str
    server: int = -1



def simulate(
    servers,
    capacity=5,
    random_limit=100000,
    seed=123456789
):
    rng = RandomGenerator(
        seed=seed,
        limit=random_limit
    )

    event_queue = []
    sequence = 0

    heapq.heappush(
        event_queue,
        Event(3.0, sequence, "ARRIVAL")
    )
    sequence += 1

    busy = [False] * servers
    queue_size = 0
    number_in_system = 0

    accumulated_time = [0.0] * (capacity + 1)

    current_time = 0.0

    losses = 0
    arrivals = 0
    departures = 0

    while event_queue and rng.used < random_limit:

        event = heapq.heappop(event_queue)

        delta = event.time - current_time

        if number_in_system <= capacity:
            accumulated_time[number_in_system] += delta

        current_time = event.time

        if event.event_type == "ARRIVAL":

            arrivals += 1

            if number_in_system < capacity:

                number_in_system += 1

                free_server = None

                for i in range(servers):
                    if not busy[i]:
                        free_server = i
                        break

                if free_server is not None:

                    busy[free_server] = True
                    random_number = rng.next_random()
                    service_time = (
                        4.0 + random_number * (5.0 - 4.0)
                    )

                    heapq.heappush(
                        event_queue,
                        Event(
                            current_time + service_time,
                            sequence,
                            "DEPARTURE",
                            free_server
                        )
                    )

                    sequence += 1
                else:
                    queue_size += 1

            else:
                losses += 1

            if rng.used < random_limit:

                random_number = rng.next_random()

                interarrival_time = (
                    3.0 + random_number * (5.0 - 3.0)
                )

                heapq.heappush(
                    event_queue,
                    Event(
                        current_time + interarrival_time,
                        sequence,
                        "ARRIVAL"
                    )
                )

                sequence += 1

        elif event.event_type == "DEPARTURE":

            departures += 1

            server = event.server

            busy[server] = False
            number_in_system -= 1

            if queue_size > 0:

                queue_size -= 1

                busy[server] = True

                random_number = rng.next_random()

                service_time = (
                    4.0 + random_number * (5.0 - 4.0)
                )

                heapq.heappush(
                    event_queue,
                    Event(
                        current_time + service_time,
                        sequence,
                        "DEPARTURE",
                        server
                    )
                )

                sequence += 1

    global_time = sum(accumulated_time)
    probabilities = []

    for accumulated in accumulated_time:
        if global_time > 0:
            probabilities.append(
                accumulated / global_time
            )
        else:
            probabilities.append(0.0)

    return {
        "servers": servers,
        "capacity": capacity,
        "randoms_used": rng.used,
        "global_time": global_time,
        "accumulated_time": accumulated_time,
        "probabilities": probabilities,
        "losses": losses,
        "arrivals": arrivals,
        "departures": departures
    }

def print_results(result):

    print("=" * 65)
    print(
        f"G/G/{result['servers']}/{result['capacity']}"
    )
    print("=" * 65)

    print(
        f"Números aleatórios utilizados: "
        f"{result['randoms_used']}"
    )

    print(
        f"Tempo global da simulação: "
        f"{result['global_time']:.6f}"
    )

    print(
        f"Clientes perdidos: "
        f"{result['losses']}"
    )

    print(
        f"Chegadas processadas: "
        f"{result['arrivals']}"
    )

    print(
        f"Saídas processadas: "
        f"{result['departures']}"
    )

    print()
    print(
        f"{'Estado':>8}"
        f"{'Tempo acumulado':>22}"
        f"{'Probabilidade':>20}"
    )

    print("-" * 52)

    for state, time, probability in zip(
        range(result["capacity"] + 1),
        result["accumulated_time"],
        result["probabilities"]
    ):
        print(
            f"{state:>8}"
            f"{time:>22.6f}"
            f"{probability:>20.8f}"
        )

    print()

if __name__ == "__main__":

    result_gg15 = simulate(
        servers=1,
        capacity=5,
        random_limit=100000,
        seed=123456789
    )

    result_gg25 = simulate(
        servers=2,
        capacity=5,
        random_limit=100000,
        seed=123456789
    )

    print_results(result_gg15)
    print_results(result_gg25)
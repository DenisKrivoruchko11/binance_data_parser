import asyncio
import collections
import json
import ssl

import scipy as sp
from matplotlib import pyplot as plt
from websockets.asyncio import client as ws_client


URL = "wss://fstream.binance.com/ws/btcusdt@bookTicker"
CONNECTIONS_COUNT = 5
CONNECTION_TIME = 60

SSL = ssl._create_unverified_context()
CONN_WAITING_TIME = 1


async def get_connection_messages(connect: ws_client.connect) -> list[tuple[int, int, int]]:
    messages = []
    
    start = None
    async with connect as connection:
        # waiting for all connections to open
        await asyncio.sleep(CONN_WAITING_TIME)

        async for raw_message in connection:
            parsed_message = json.loads(raw_message)
            if start is None:
                start = parsed_message['E']
            if (parsed_message['E'] - start) > (CONNECTION_TIME * 1000):
                break
            messages.append((parsed_message['u'], parsed_message['T'], parsed_message['E']))

    return messages


def _get_filtered_messages(connections_messages):
    first_messages = [messages[0] for messages in connections_messages]
    start_update_id = max(first_messages, key=lambda message: message[0])[0]
    start_indexes = [0 for _ in connections_messages]

    for conn_number, messages in enumerate(connections_messages):
        for index, (update_id, _, _) in enumerate(messages):
            next_update_id = messages[index + 1][0]
            if update_id == start_update_id and next_update_id != start_update_id:
                start_indexes[conn_number] = index
                break

    return [
        messages[index:] for messages, index in zip(connections_messages, start_indexes)
    ]


def _build_plots(connections_delays: list[list[int]]):
    for i, delays in enumerate(connections_delays, start=1):
        delays_to_count = collections.defaultdict(int)
        for delay in delays:
            delays_to_count[delay] += 1
        plt.plot(delays_to_count.keys(), delays_to_count.values(), label=f'Connection {i}')

    plt.xlabel('delay time, ms')
    plt.ylabel('messages count')
    plt.legend()
    plt.grid()
    plt.show()


def _get_fast_updates_by_connection(connections_messages: list[list[tuple[int, int]]]):
    events_to_updates = collections.defaultdict(lambda: [None for _ in range(CONNECTIONS_COUNT)])
    for conn_number, messages in enumerate(connections_messages):
        for update_id, event_time in messages:
            events_to_updates[event_time][conn_number] = update_id

    fast_updates = [0 for _ in connections_messages]
    visited = set()
    for _, update_ids in sorted(events_to_updates.items(), key=lambda event: event[0]):
        for conn_number, update_id in enumerate(update_ids):
            if update_id is None or update_id in visited:
                continue
            visited.add(update_id)
            if sum([1 for upd_id in update_ids if upd_id == update_id]) == 1:
                fast_updates[conn_number] += 1 

    print(f'differtent update_ids count: {len(visited)}')
    for conn_number, count in enumerate(fast_updates, start=1):
        print(f'fast updates for connection {conn_number}: {count}')


def handle_connections_data(connections_messages):
    filtered_messages = _get_filtered_messages(connections_messages)
    delays = [
        [event_time - trade_time for _, trade_time, event_time in messages] 
        for messages in filtered_messages
    ]
    _get_fast_updates_by_connection(
        [
            [(update_id, event_time) for update_id, _, event_time in messages] 
            for messages in filtered_messages
        ],
    )
    _calculate_stats_metrics(delays)
    _build_plots(delays)


def _calculate_stats_metrics(connections_delays):
    alpha = 0.05

    f_statistic, p_value_mean = sp.stats.f_oneway(*connections_delays)
    print(f'ANOVA test for means: F-statistic = {f_statistic}, p-value = {p_value_mean}')
    print('means differ' if p_value_mean < alpha else 'means do not differ')

    w_statistic, p_value_stdev = sp.stats.levene(*connections_delays)
    print(f'Levene test for variances: W-statistic = {w_statistic}, p-value = {p_value_stdev}')
    print('standard deviations differ' if p_value_mean < alpha else 'standard deviations do not differ')


async def main():
    connections = [
        ws_client.connect(URL, ssl=SSL, close_timeout=1) for _ in range(CONNECTIONS_COUNT)
    ]
    connections_messages = await asyncio.gather(
        *[get_connection_messages(conn) for conn in connections],
    )
    handle_connections_data(connections_messages)


if __name__ == '__main__':
    asyncio.run(main())

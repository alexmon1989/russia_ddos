import threading
import sys
import time
from datetime import datetime
from context import Context
from common import green_txt, red_txt, blue_txt, convert_size, print_logo, get_first_ip_part
from constants import DEFAULT_CURRENT_IP_VALUE
import services

_ctx = Context()
lock = threading.Lock()


def show_info(_ctx: Context):
    """Prints attack info to console."""
    print_logo()

    my_ip_masked = get_first_ip_part(_ctx.current_ip) if _ctx.current_ip != DEFAULT_CURRENT_IP_VALUE \
        else DEFAULT_CURRENT_IP_VALUE
    is_random_packet_len = _ctx.attack_method in ('tcp', 'udp') and _ctx.random_packet_len

    if _ctx.current_ip:
        if _ctx.current_ip == _ctx.start_ip:
            your_ip = blue_txt(my_ip_masked)
        else:
            your_ip = red_txt(f'IP was changed, check VPN (current IP: {my_ip_masked})')
    else:
        your_ip = red_txt('Can\'t get your IP. Check internet connection.')

    target_host = blue_txt(f'{_ctx.original_host}:{_ctx.port}')
    load_method = blue_txt(f'{str(_ctx.attack_method).upper()}')
    thread_pool = blue_txt(f'{_ctx.threads}')
    available_cpu = blue_txt(f'{_ctx.cpu_count}')
    rnd_packet_len = blue_txt('YES' if is_random_packet_len else 'NO')
    max_rnd_packet_len = blue_txt(_ctx.max_random_packet_len if is_random_packet_len else 'NOT REQUIRED')

    print('------------------------------------------------------')
    print(f'Start time:                 {_ctx.start_time.strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'Your IP:                    {your_ip}')
    print(f'Host:                       {target_host}')
    print(f'Load Method:                {load_method}')
    print(f'Threads:                    {thread_pool}')
    print(f'vCPU count:                 {available_cpu}')
    print(f'Random Packet Length:       {rnd_packet_len}')
    print(f'Max Random Packet Length:   {max_rnd_packet_len}')
    print('------------------------------------------------------')

    sys.stdout.flush()


def show_statistics(_ctx: Context):
    """Prints statistics to console."""
    if not _ctx.show_statistics:
        _ctx.show_statistics = True

        lock.acquire()
        if not _ctx.getting_ip_in_progress:
            t = threading.Thread(target=services.update_current_ip, args=[_ctx])
            t.start()
        lock.release()

        if _ctx.attack_method == 'tcp':
            services.check_successful_tcp_attack(_ctx)
        else:
            services.check_successful_connections(_ctx)
        # cpu_load = get_cpu_load()

        print("\033c")
        show_info(_ctx)

        connections_success = green_txt(_ctx.connections_success)
        connections_failed = red_txt(_ctx.connections_failed)

        curr_time = datetime.now() - _ctx.start_time

        print(f'Duration:                   {str(curr_time).split(".", 2)[0]}')
        # print(f'CPU Load Average:           {cpu_load}')
        if _ctx.attack_method == 'http':
            print(f'Requests sent:              {_ctx.packets_sent}')
            if len(_ctx.http_codes_counter.keys()):
                print(f'HTTP codes distribution:    {build_http_codes_distribution(_ctx.http_codes_counter)}')
        elif _ctx.attack_method == 'tcp':
            size_sent = convert_size(_ctx.packets_sent)
            if _ctx.packets_sent == 0:
                size_sent = red_txt(size_sent)
            else:
                size_sent = blue_txt(size_sent)

            print(f'Total Packets Sent Size:    {size_sent}')
        else:  # udp
            print(f'Packets Sent:               {_ctx.packets_sent}')
        print(f'Connection Success:         {connections_success}')
        print(f'Connection Failed:          {connections_failed}')
        print('------------------------------------------------------')

        if _ctx.errors:
            print('\n\n')
        for error in _ctx.errors:
            print(red_txt(error))
            print('\007')

        sys.stdout.flush()
        time.sleep(3)
        _ctx.show_statistics = False


def build_http_codes_distribution(http_codes_counter):
    codes_distribution = []
    total = sum(http_codes_counter.values())
    for code in http_codes_counter.keys():
        count = http_codes_counter[code]
        percent = round(count * 100 / total)
        codes_distribution.append(f'{code}: {count} ({percent}%)')
    return ', '.join(codes_distribution)

import os
import ipaddress

import psutil

from backend.db import db


def is_local_address(ip_address: str) -> bool:
    """
    Check whether an IP address is local/internal.
    """

    try:
        ip = ipaddress.ip_address(ip_address)

        return (
            ip.is_loopback
            or ip.is_private
            or ip.is_link_local
        )

    except ValueError:
        return False


def get_process_name(pid):
    """
    Safely get a process name from its PID.
    """

    if pid is None:
        return "unknown"

    try:
        process = psutil.Process(pid)

        return process.name()

    except (
        psutil.NoSuchProcess,
        psutil.AccessDenied
    ):
        return "unknown"


def get_external_connections(allowed_pids=None):
    """
    Scan active established network connections.

    If allowed_pids is provided, only connections belonging
    to those processes are checked.
    """

    external_connections = []

    try:
        connections = psutil.net_connections(
            kind="inet"
        )

        for connection in connections:

            # Ignore sockets without a remote endpoint.
            if not connection.raddr:
                continue

            # Filter by Workbench process tree if requested.
            if (
                allowed_pids is not None
                and connection.pid not in allowed_pids
            ):
                continue

            # Only inspect active connections.
            if (
                connection.status
                != psutil.CONN_ESTABLISHED
            ):
                continue

            remote_ip = connection.raddr.ip
            remote_port = connection.raddr.port

            # Ignore localhost/private/internal traffic.
            if is_local_address(remote_ip):
                continue

            external_connections.append({
                "pid": connection.pid,
                "process_name": get_process_name(
                    connection.pid
                ),
                "remote_ip": remote_ip,
                "remote_port": remote_port,
                "status": connection.status
            })

    except psutil.AccessDenied as error:

        external_connections.append({
            "error": "Access denied while scanning network connections",
            "details": str(error)
        })

    except Exception as error:

        external_connections.append({
            "error": "Network scan failed",
            "details": str(error)
        })

    return external_connections


def check_system_airgap_status() -> dict:
    """
    Check the entire operating system for public,
    external network connections.
    """

    connections = get_external_connections()

    real_connections = [
        connection
        for connection in connections
        if "remote_ip" in connection
    ]

    airgapped = len(real_connections) == 0

    return {
        "airgapped": airgapped,
        "active_external_sockets": real_connections,
        "external_socket_count": len(real_connections),
        "status": (
            "SYSTEM_SECURE_AIR_GAPPED"
            if airgapped
            else "SYSTEM_EXTERNAL_TRAFFIC_DETECTED"
        )
    }


def get_workbench_process_tree():
    """
    Get the current Workbench Python process and all
    child processes.

    This allows monitoring the Workbench specifically,
    instead of incorrectly reporting unrelated browser,
    VS Code, Windows, or system traffic.
    """

    current_process = psutil.Process(
        os.getpid()
    )

    processes = [current_process]

    try:

        children = current_process.children(
            recursive=True
        )

        processes.extend(children)

    except (
        psutil.NoSuchProcess,
        psutil.AccessDenied
    ):
        pass

    process_data = []

    for process in processes:

        try:

            process_data.append({
                "pid": process.pid,
                "name": process.name()
            })

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied
        ):
            pass

    return process_data


def check_workbench_airgap_status() -> dict:
    """
    Check external network traffic only for the current
    Sovereign AI Workbench process and child processes.
    """

    process_tree = get_workbench_process_tree()

    workbench_pids = {
        process["pid"]
        for process in process_tree
    }

    connections = get_external_connections(
        allowed_pids=workbench_pids
    )

    real_connections = [
        connection
        for connection in connections
        if "remote_ip" in connection
    ]

    airgapped = len(real_connections) == 0

    return {
        "airgapped": airgapped,
        "active_external_sockets": real_connections,
        "external_socket_count": len(
            real_connections
        ),
        "monitored_processes": process_tree,
        "status": (
            "WORKBENCH_SECURE_LOCAL"
            if airgapped
            else "WORKBENCH_EXTERNAL_TRAFFIC_DETECTED"
        )
    }


def check_airgap_status() -> dict:
    """
    Main Network Sentry function.

    Returns both Workbench-specific and system-wide
    network status.

    The top-level 'airgapped' value represents the
    Sovereign AI Workbench process.
    """

    workbench_status = (
        check_workbench_airgap_status()
    )

    system_status = (
        check_system_airgap_status()
    )

    return {
        "airgapped": workbench_status[
            "airgapped"
        ],
        "active_external_sockets": (
            workbench_status[
                "active_external_sockets"
            ]
        ),
        "external_socket_count": (
            workbench_status[
                "external_socket_count"
            ]
        ),
        "status": workbench_status["status"],
        "workbench": workbench_status,
        "system": system_status
    }


def log_sentry_telemetry() -> dict:
    """
    Run the Network Sentry and store telemetry
    using the central DatabaseManager.

    No SQLite schema logic exists here anymore.
    Database management is handled by backend/db.py.
    """

    result = check_airgap_status()

    workbench_status = result["workbench"]

    system_status = result["system"]

    telemetry = {
        "workbench_external_sockets": (
            workbench_status[
                "active_external_sockets"
            ]
        ),
        "system_external_sockets": (
            system_status[
                "active_external_sockets"
            ]
        ),
        "monitored_processes": (
            workbench_status[
                "monitored_processes"
            ]
        )
    }

    log_id = db.save_network_log(
        workbench_airgapped=(
            workbench_status["airgapped"]
        ),
        system_airgapped=(
            system_status["airgapped"]
        ),
        workbench_status=(
            workbench_status["status"]
        ),
        system_status=(
            system_status["status"]
        ),
        workbench_external_count=(
            workbench_status[
                "external_socket_count"
            ]
        ),
        system_external_count=(
            system_status[
                "external_socket_count"
            ]
        ),
        details=telemetry
    )

    result["database_log_id"] = log_id

    return result


if __name__ == "__main__":

    print("\n")

    print("#" * 60)
    print("SOVEREIGN AI WORKBENCH")
    print("PHASE 4 - NETWORK SENTRY")
    print("#" * 60)

    result = log_sentry_telemetry()

    workbench = result["workbench"]

    system = result["system"]

    print("\nWORKBENCH STATUS")

    print("-" * 60)

    print(
        "Status:",
        workbench["status"]
    )

    print(
        "Air-Gapped:",
        workbench["airgapped"]
    )

    print(
        "External Connections:",
        workbench["external_socket_count"]
    )

    print("\nMonitored Processes:")

    for process in workbench[
        "monitored_processes"
    ]:

        print(
            f"PID {process['pid']} -> "
            f"{process['name']}"
        )

    print("\nSYSTEM STATUS")

    print("-" * 60)

    print(
        "Status:",
        system["status"]
    )

    print(
        "Air-Gapped:",
        system["airgapped"]
    )

    print(
        "External Connections:",
        system["external_socket_count"]
    )

    print("\nFINAL WORKBENCH SECURITY RESULT")

    print("-" * 60)

    print(
        result["status"]
    )

    print(
        "\nSQLite Network Log ID:",
        result["database_log_id"]
    )
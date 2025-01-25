from math import ceil
from collections import deque

from src.users.schemas import UserRead, CompanyRead


def similarity_check(current_row: str, users_data, companies_data) -> dict[str, dict | None]:
    """
    Algorithm for checking differences between a company name or username and the current string
    """
    users, companies = dict(), dict()
    users_weights, companies_weights = dict(), dict()
    users_answer, companies_answer = dict(), dict()
    users_sorted, companies_sorted = deque(), deque()

    for n in users_data:
        users[n[2]] = n
    for key in users:
        row = key.lower().replace(' ', '')
        table = [[0 for _ in range(len(row) + 1)] for _ in range(len(current_row) + 1)]

        for s in range(1, len(current_row) + 1):
            for c in range(1, len(row) + 1):
                if row[c - 1] == current_row[s - 1]:
                    table[s][c] = table[s - 1][c - 1] + 1
                else:
                    table[s][c] = max(table[s - 1][c], table[s][c - 1])
        users_weights[key] = table[-1][-1]

    un = len(users) if len(users) <= 10 else ceil(len(users) * 0.25) # How much need return
    for i in users_weights:
        if users_sorted:
            if users_weights[users_sorted[0]] < users_weights[i]:
                users_sorted.appendleft(i)
            else:
                users_sorted.append(i)
        else:
            users_sorted.append(i)
    for key in list(users_sorted)[0:un]:
        users_answer[key] = UserRead(
            id=users[key][0],
            email=users[key][1],
            username=users[key][2],
            first_name=users[key][4],
            last_name=users[key][5],
            role_id=users[key][7],
            company_id=users[key][8],
            is_verified=users[key][11],
            register_at=users[key][-1],
        )

    if companies_data:
        for n in companies_data:
            companies[n[2]] = n
        for key in companies:
            row = key.lower().replace(' ', '')
            table = [[0 for _ in range(len(row) + 1)] for _ in range(len(current_row) + 1)]

            for s in range(1, len(current_row) + 1):
                for c in range(1, len(row) + 1):
                    if row[c - 1] == current_row[s - 1]:
                        table[s][c] = table[s - 1][c - 1] + 1
                    else:
                        table[s][c] = max(table[s - 1][c], table[s][c - 1])
            companies_weights[key] = table[-1][-1]

        cn = len(companies) if len(companies) <= 10 else ceil(len(companies) * 0.25) # How much need return
        for i in companies_weights:
            if companies_sorted:
                if companies_weights[companies_sorted[0]] < companies_weights[i]:
                    companies_sorted.appendleft(i)
                else:
                    companies_sorted.append(i)
            else:
                companies_sorted.append(i)
        for key in list(companies_sorted)[:cn]:
            companies_answer[key] = CompanyRead(
            id = companies[key][0],
            email = companies[key][1],
            name = companies[key][2],
            description = companies[key][3],
            address = companies[key][4],
            contacts = companies[key][5],
            register_at = companies[key][7],
        )
    else:
        companies_answer = None

    return {
        "users": users_answer,
        "companies": companies_answer,
    }

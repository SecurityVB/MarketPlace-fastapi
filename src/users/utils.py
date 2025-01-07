from math import ceil


def similarity_check(current_row: str, user_data, companies_data) -> list[dict | None]:
    """
    Algorithm for checking differences between a company name or username and the current string
    """
    users, companies = {}, {}
    users_weights, companies_weights = {}, {}

    for n in user_data:
        users[n[2]] = n
    for u in users:
        key = u
        row = key.lower().replace(' ', '')
        table = [[0 for _ in range(len(row) + 1)] for _ in range(len(current_row) + 1)]

        for s in range(1, len(current_row) + 1):
            for c in range(1, len(row) + 1):
                if row[c - 1] == current_row[s - 1]:
                    table[s][c] = table[s - 1][c - 1] + 1
                else:
                    table[s][c] = max(table[s - 1][c], table[s][c - 1])
        users_weights[key] = table[-1][-1]

    un = ceil(len(users) * 0.25)  # How much need return
    sorted_users = sorted(users.keys(), key=lambda tag: users_weights[tag], reverse=True)
    users_answer = {tag: users[tag] for tag in sorted_users[:un]}

    if companies:
        for n in companies_data:
            companies[n[2]] = n
        for c in companies:
            key = c[1]
            row = key.lower().replace(' ', '')
            table = [[0 for _ in range(len(row) + 1)] for _ in range(len(current_row) + 1)]

            for s in range(1, len(current_row) + 1):
                for c in range(1, len(row) + 1):
                    if row[c - 1] == current_row[s - 1]:
                        table[s][c] = table[s - 1][c - 1] + 1
                    else:
                        table[s][c] = max(table[s - 1][c], table[s][c - 1])
            companies_weights[key] = table[-1][-1]

        cn = ceil(len(companies) * 0.25) # How much need return
        sorted_companies = sorted(companies.keys(), key=lambda tag: companies_weights[tag], reverse=True)
        companies_answer = {tag: companies[tag] for tag in sorted_companies[:cn]}
    else:
        companies_answer = None
    return [users_answer, companies_answer]

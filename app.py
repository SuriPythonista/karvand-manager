####============== Mansoureh Hamedi =================####

import json
import os

STORAGE_FOLDER = "data"
MEMBERS_PATH = os.path.join(STORAGE_FOLDER, "karvands.json")
SUMMARY_PATH = os.path.join(STORAGE_FOLDER, "report.json")

INITIAL_CONTENT = {
    "bootcamp": {"title": "Karvand Python", "year": 2026},
    "karvands": [],
}


# ======================== file handling ========================

def dump_to_file(target, payload):
    with open(target, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=4)


def fresh_content():
    """Return a new copy of the starting structure."""
    return json.loads(json.dumps(INITIAL_CONTENT))


def ensure_storage():
    os.makedirs(STORAGE_FOLDER, exist_ok=True)
    if not os.path.exists(MEMBERS_PATH):
        dump_to_file(MEMBERS_PATH, fresh_content())


def read_store():
    """Load the data file; rebuild it if it is empty or broken."""
    try:
        with open(MEMBERS_PATH, "r", encoding="utf-8") as fh:
            store = json.load(fh)
        if not isinstance(store, dict) or not isinstance(store.get("karvands"), list):
            raise ValueError("unexpected structure")
        return store
    except (json.JSONDecodeError, ValueError):
        print("Data file was empty or damaged. It has been rebuilt with the initial structure.")
        store = fresh_content()
        dump_to_file(MEMBERS_PATH, store)
        return store

if __name__ == "__main__":
    ensure_storage()
    store = read_store()
    print("Storage is ready:", MEMBERS_PATH)

# def persist(store):
#     dump_to_file(MEMBERS_PATH, store)


# # ======================== user input ========================

# def prompt_number(message, low=None, high=None):
#     """Repeat the prompt until a whole number within [low, high] is typed."""
#     while True:
#         try:
#             number = int(input(message))
#         except ValueError:
#             print("Please enter a valid number.")
#             continue

#         too_low = low is not None and number < low
#         too_high = high is not None and number > high
#         if too_low or too_high:
#             print(f"Value must be between {low} and {high}.")
#             continue

#         return number


# def collect_abilities():
#     abilities = []
#     while True:
#         title = input("Enter skill name (or 'done' to finish): ").strip()
#         if title.lower() == "done":
#             return abilities
#         if not title:
#             continue

#         rank = input("Enter skill level: ").strip()
#         points = prompt_number("Enter skill score (0-100): ", 0, 100)
#         abilities.append({"name": title, "level": rank, "score": points})


# # ======================== lookup & output ========================

# def locate_member(store, member_id):
#     for member in store["karvands"]:
#         if member["id"] == member_id:
#             return member
#     return None


# def generate_id(store):
#     return max((m["id"] for m in store["karvands"]), default=0) + 1


# def ability_line(ability):
#     return f"- {ability['name']} | Level: {ability['level']} | Score: {ability['score']}"


# def display_member(member, only=None):
#     """Show a member's details; `only` limits which skills are listed."""
#     listed = member["skills"] if only is None else only
#     edu = member["education"]

#     print("\n--------------------")
#     print("ID:", member["id"])
#     print("Name:", member["full_name"])
#     print("Email:", member["email"])
#     print("City:", member["city"])
#     print("Education:", edu["degree"], "-", edu["field"])
#     print("Skills:")
#     for ability in listed:
#         print(ability_line(ability))


# # ======================== menu operations ========================

# def register_member(store):
#     print("\n--- Add Karvand ---")

#     record = {
#         "id": generate_id(store),
#         "full_name": input("Enter full name: ").strip(),
#         "email": input("Enter email: ").strip(),
#         "city": input("Enter city: ").strip(),
#         "education": {
#             "degree": input("Enter education degree: ").strip(),
#             "field": input("Enter education field: ").strip(),
#         },
#         "skills": collect_abilities(),
#     }

#     store["karvands"].append(record)
#     persist(store)
#     print("Karvand added successfully.")


# def list_members(store):
#     print("\n--- All Karvands ---")

#     if not store["karvands"]:
#         print("No karvands have been registered.")
#         return

#     for member in store["karvands"]:
#         display_member(member)


# def lookup_by_id(store):
#     print("\n--- Search Karvand by ID ---")

#     member = locate_member(store, prompt_number("Enter Karvand ID: "))
#     if member is None:
#         print("Karvand with this ID was not found.")
#     else:
#         display_member(member)


# def lookup_by_ability(store):
#     print("\n--- Search Karvand by Skill ---")

#     query = input("Enter skill name: ").strip().lower()
#     any_hit = False

#     for member in store["karvands"]:
#         hits = [a for a in member["skills"] if a["name"].lower() == query]
#         if hits:
#             display_member(member, hits)
#             any_hit = True

#     if not any_hit:
#         print("No karvand found with this skill.")


# def update_member(store):
#     print("\n--- Edit Karvand ---")

#     member = locate_member(store, prompt_number("Enter Karvand ID: "))
#     if member is None:
#         print("Karvand with this ID was not found.")
#         return

#     print("\nLeave input empty to keep the current value.")

#     editable = [
#         (member, "email", "Email"),
#         (member, "city", "City"),
#         (member["education"], "degree", "Degree"),
#         (member["education"], "field", "Field"),
#     ]
#     for holder, attr, caption in editable:
#         answer = input(f"{caption} [{holder[attr]}]: ").strip()
#         if answer:
#             holder[attr] = answer

#     persist(store)
#     print("Karvand updated successfully.")


# def remove_member(store):
#     print("\n--- Delete Karvand ---")

#     member = locate_member(store, prompt_number("Enter Karvand ID: "))
#     if member is None:
#         print("Karvand with this ID was not found.")
#         return

#     store["karvands"].remove(member)
#     persist(store)
#     print("Karvand deleted successfully.")


# def build_summary(store):
#     members = store["karvands"]
#     every_ability = [a for m in members for a in m["skills"]]
#     point_list = [a["score"] for a in every_ability]

#     mean_score = round(sum(point_list) / len(point_list), 2) if point_list else 0

#     summary = {
#         "total_karvands": len(members),
#         "total_skills": len(every_ability),
#         "average_skill_score": mean_score,
#         "cities": list(dict.fromkeys(m["city"] for m in members)),
#         "unique_skills": list(dict.fromkeys(a["name"] for a in every_ability)),
#     }

#     print("\n--- General Report ---")
#     print("Total Karvands:", summary["total_karvands"])
#     print("Total Skills:", summary["total_skills"])
#     print("Average Skill Score:", summary["average_skill_score"])
#     print("Cities:", summary["cities"])
#     print("Unique Skills:", summary["unique_skills"])

#     dump_to_file(SUMMARY_PATH, summary)
#     print("Report saved successfully.")


# # ======================== entry point ========================

# ACTIONS = {
#     "1": ("Add Karvand", register_member),
#     "2": ("Show All Karvands", list_members),
#     "3": ("Search by ID", lookup_by_id),
#     "4": ("Search by Skill", lookup_by_ability),
#     "5": ("Edit Karvand", update_member),
#     "6": ("Delete Karvand", remove_member),
#     "7": ("General Report", build_summary),
# }
# QUIT_KEY = "8"


# def run():
#     ensure_storage()
#     store = read_store()

#     while True:
#         print("\n===== Karvand Manager =====")
#         for key, (caption, _) in ACTIONS.items():
#             print(f"{key}. {caption}")
#         print(f"{QUIT_KEY}. Exit")

#         selection = input("Enter your choice: ").strip()

#         if selection == QUIT_KEY:
#             print("Goodbye!")
#             break

#         action = ACTIONS.get(selection)
#         if action:
#             action[1](store)
#         else:
#             print("Invalid choice.")


# if __name__ == "__main__":
#     run()
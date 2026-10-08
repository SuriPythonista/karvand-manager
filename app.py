####============== Mansoureh Hamedi =================####

"""
Karvand Manager:
An app for keeping a list of bootcamp members ("karvands") in a JSON file.
Each karvand has an id, name, email, city, education and a list of skills.
The menu lets you add, list, search, edit and delete karvands, and build a summary report.

Data is stored in "data/karvands.json" and the report is written to "data/report.json".

Sections:
    1. File handling
    2. Adding karvands
    3. Showing karvands
    4. Editing a karvand
    5. Searching by id
    6. Searching by skill
    7. Removing by id
    8. App menu
"""


import json
import os

STORAGE_FOLDER = "data"
MEMBERS_PATH = os.path.join(STORAGE_FOLDER, "karvands.json")
SUMMARY_PATH = os.path.join(STORAGE_FOLDER, "report.json")

INITIAL_CONTENT = {
    "bootcamp": {"title": "Karvand Python", "year": 2026},
    "karvands": [],
}


# ======================== 1. file handling ========================

def dump_to_file(target, payload):
    """
    Write (payload) to the file at (target) as a JSON.
    Args:
        target: Path of the file to write.
        payload: python object convertible to JSON (usually a dict).
    """
    with open(target, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=4)


def fresh_content():
    """
    Returns a new copy of INITIAL_CONTENT:
    changing the returned structure (for example appending to its karvands list)
    never changes the INITIAL_CONTENT template.
    """
    return json.loads(json.dumps(INITIAL_CONTENT))


def ensure_storage():
    """
    Make sure the data folder and the members file exist:

    Creates STORAGE_FOLDER (data) if it is missing (no error if it is already there).
    If MEMBERS_PATH (karvands.json) does not exist yet, it is created with the
    starting structure from fresh_content(). An existing file is left untouched.
    """
    os.makedirs(STORAGE_FOLDER, exist_ok=True)
    if not os.path.exists(MEMBERS_PATH):
        dump_to_file(MEMBERS_PATH, fresh_content())


def read_store():
    """
    Loads the members data from MEMBERS_PATH.

    The file must contain a JSON object with a "karvands" key holding a list.
    If the file is empty, is not valid JSON, or has a different
    structure, a message is printed and the file is rebuilt with the
    starting structure, so the program can keep running.

    Returns:
        dict: The loaded or freshly rebuilt data store.
    """
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


def persist(store):
    """
    Save the whole data store back to MEMBERS_PATH.
    Called after every change (add, edit, delete) so the file always matches what is in memory.

    Args:
        store: The data store dict returned by read_store().
    """
    dump_to_file(MEMBERS_PATH, store)


# ======================== 2. adding karvands ========================

def prompt_number(message, low=None, high=None):
    """
    Keeps asking while the input is not an integer or is outside the
    allowed range (low and high).
    Also used by the edit, search and remove sections to read an id.

    Args:
        message: Text shown to the user.
        low: Smallest allowed value, or None.
        high: Largest allowed value, or None.

    Returns:
        int: The number the user entered.
    """
    while True:
        try:
            number = int(input(message))
        except ValueError:
            print("Please enter a valid number.")
            continue

        too_low = low is not None and number < low
        too_high = high is not None and number > high
        if too_low or too_high:
            print(f"Value must be between {low} and {high}.")
            continue

        return number


def generate_id(store):
    """
    Return the next free id: the highest existing id plus one.

    Returns 1 when there are no karvands yet. Ids of deleted karvands
    are reused only if they were the highest.
    """
    return max((m["id"] for m in store["karvands"]), default=0) + 1


def collect_skills():
    """
    Ask the user for skills one by one until they type 'done'.

    For each skill it asks for a name, a level and a score from 0 to 100.
    An empty name is ignored and asked again.

    Returns:
        list[dict]: Skills as {"name", "level", "score"} dicts.
    """
    skills = []

    while True:
        title = input("Enter skill name (or 'done' to finish): ").strip()
        if title.lower() == "done":
            return skills
        if not title:
            continue

        rank = input("Enter skill level: ").strip()
        points = prompt_number("Enter skill score (0-100): ", 0, 100)
        skills.append({"name": title, "level": rank, "score": points})


def register_member(store):
    """Menu 1: ask for a new karvand's details, add it and save.

    The id is assigned automatically with ``generate_id``.
    """
    print("\n--- Add Karvand ---")

    record = {
        "id": generate_id(store),
        "full_name": input("Enter full name: ").strip(),
        "email": input("Enter email: ").strip(),
        "city": input("Enter city: ").strip(),
        "education": {
            "degree": input("Enter education degree: ").strip(),
            "field": input("Enter education field: ").strip(),
        },
        "skills": collect_skills(),
    }

    store["karvands"].append(record)
    persist(store)
    print("Karvand added successfully.")


# ======================== 3. showing karvands ========================

def skill_line(skill):
    """
    Format one skill as a single line for display.

    Example: ``- Python | Level: Advanced | Score: 90``
    """
    return f"- {skill['name']} | Level: {skill['level']} | Score: {skill['score']}"


def display_member(member, skills=None):
    """
    Print a karvand's details.

    display_member(member)          -> prints all of the karvand's skills
    display_member(member, hits)    -> prints only the skills in hits
    """
    if skills is None:
        skills = member["skills"]

    print("\n--------------------")
    print("ID:", member["id"])
    print("Name:", member["full_name"])
    print("Email:", member["email"])
    print("City:", member["city"])
    print("Education:", member["education"]["degree"], "-", member["education"]["field"])
    print("Skills:")
    for skill in skills:
        print(skill_line(skill))


def list_members(store):
    """Menu 2: print every karvand, or a message if there are none."""
    print("\n--- All Karvands ---")

    if not store["karvands"]:
        print("No karvands have been registered.")
        return

    for member in store["karvands"]:
        display_member(member)


# ======================== 4. editing a karvand ========================

def locate_member(store, member_id):
    """
    Find a karvand by id.
    Shared by the edit, search-by-id and remove sections.

    Args:
        store: The data store.
        member_id: The id to look for.

    Returns:
        dict | None: The matching karvand, or None if there is none.
    """
    for member in store["karvands"]:
        if member["id"] == member_id:
            return member
    return None


def ask_new_value(caption, current):
    """
    Show the current value and ask for a new one.
    If the user just presses Enter, the current value is kept.
    """
    answer = input(f"{caption} [{current}]: ").strip()
    if answer:
        return answer
    return current


def update_member(store):
    """
    Menu 5: edit a karvand's email, city, degree and field, then save.
    Pressing Enter without typing keeps the current value.
    """
    print("\n--- Edit Karvand ---")

    member = locate_member(store, prompt_number("Enter Karvand ID: "))
    if member is None:
        print("Karvand with this ID was not found.")
        return

    print("\nLeave input empty to keep the current value.")

    member["email"] = ask_new_value("Email", member["email"])
    member["city"] = ask_new_value("City", member["city"])
    member["education"]["degree"] = ask_new_value("Degree", member["education"]["degree"])
    member["education"]["field"] = ask_new_value("Field", member["education"]["field"])

    persist(store)
    print("Karvand updated successfully.")


# ======================== 5. searching by id ========================

def lookup_by_id(store):
    """Menu 3: ask for an id and print that karvand, if found."""
    print("\n--- Search Karvand by ID ---")

    member = locate_member(store, prompt_number("Enter Karvand ID: "))
    if member is None:
        print("Karvand with this ID was not found.")
    else:
        display_member(member)
 

# ======================== 6. searching by skill ========================

def lookup_by_skill(store):
    """Menu 4: find karvands who have a given skill.

    The match is exact but case-insensitive. Each matching karvand is
    shown with only the matching skill(s).
    """
    print("\n--- Search Karvand by Skill ---")

    query = input("Enter skill name: ").strip().lower()
    any_hit = False

    for member in store["karvands"]:
        hits = [a for a in member["skills"] if a["name"].lower() == query]
        if hits:
            display_member(member, hits)
            any_hit = True

    if not any_hit:
        print("No karvand found with this skill.")


# ======================== 7. removing by id ========================

def remove_member(store):
    """
    delete a karvand by id and update the JSON file.

    No confirmation is asked. persist() writes the updated list back
    to MEMBERS_PATH straight after the removal.
    """
    print("\n--- Delete Karvand ---")

    member = locate_member(store, prompt_number("Enter Karvand ID: "))
    if member is None:
        print("Karvand with this ID was not found.")
        return

    store["karvands"].remove(member)
    persist(store)
    print("Karvand deleted successfully.")


# ======================== 8. summary report ========================

def build_summary(store):
    """
    print a general report and save it to SUMMARY_PATH.

    The report contains the number of karvands, the total number of
    skills, the average skill score, and the cities and unique skill names.
    """
    members = store["karvands"]
    # Put the skills of all karvands into one list.
    every_skill = []
    for member in members:
        every_skill.extend(member["skills"])
    point_list = [a["score"] for a in every_skill]

    mean_score = round(sum(point_list) / len(point_list), 2) if point_list else 0

    # Each city only once, in the order it first appears.
    cities = []
    for member in members:
        if member["city"] not in cities:
            cities.append(member["city"])

    # Each skill name only once, in the order it first appears.
    unique_skills = []
    for skill in every_skill:
        if skill["name"] not in unique_skills:
            unique_skills.append(skill["name"])

    summary = {
        "total_karvands": len(members),
        "total_skills": len(every_skill),
        "average_skill_score": mean_score,
        "cities": cities,
        "unique_skills": unique_skills,
    }

    print("\n--- General Report ---")
    print("Total Karvands:", summary["total_karvands"])
    print("Total Skills:", summary["total_skills"])
    print("Average Skill Score:", summary["average_skill_score"])
    print("Cities:", summary["cities"])
    print("Unique Skills:", summary["unique_skills"])

    dump_to_file(SUMMARY_PATH, summary)
    print("Report saved successfully.")

# ======================== 8. app menu ========================
# Menu choices: 
# key : (message shown in the menu, function to call).
ACTIONS = {
    "1": ("Add Karvand", register_member),
    "2": ("Show All Karvands", list_members),
    "3": ("Search by ID", lookup_by_id),
    "4": ("Search by Skill", lookup_by_skill),
    "5": ("Edit Karvand", update_member),
    "6": ("Delete Karvand", remove_member),
    "7": ("General Report", build_summary),
}
EXIT_KEY = "8"


def run():
    """
    Start the program: prepare storage, then show the menu in a loop.

    Each choice calls the matching function with the data store. 
    The loop ends when the user picks EXIT_KEY.
    """
    ensure_storage()
    store = read_store()

    while True:
        print("\n===== Karvand Manager =====")
        for key, (caption, _) in ACTIONS.items():
            print(f"{key}. {caption}")
        print(f"{EXIT_KEY}. Exit")

        selection = input("Enter your choice: ").strip()

        if selection == EXIT_KEY:
            print("Goodbye!")
            break

        action = ACTIONS.get(selection)
        if action:
            action[1](store)
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    run()

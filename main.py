from database import (initialize_database, create_policy, get_all_policies, get_policies_by_category, get_policy_by_id, update_policy, delete_policy)

ALLOWED_CATEGORIES = [
    "Motor",
    "Health",
    "Life",
    "Travel",
    "Home",
    "Other"
]

def get_positive_number(prompt):
    while True:
        try:
            value = float(input(prompt))
            
            if value <= 0:
                print("Error: Enter a number greater than zero.")
                continue
            
            return value
        except ValueError:
            print("Error: Please enter a valid number.")
            
def create_policy_flow():
    print("\n--- Create New Policy ---")
    
    name = input("Enter policy name: ").strip()
    
    if not name:
        print("Error: Policy name cannot be empty.")
        return
    
    print("Allowed categories:", ", ".join(ALLOWED_CATEGORIES))
    category = input("Enter category:  ").strip().title()
    
    if category not in ALLOWED_CATEGORIES:
        print("Error: Invalid category.")
        return 
    
    min_premium = get_positive_number("Enter minimum premium: ")
    max_premium = get_positive_number("Enter maximum premium: ")
    
    if min_premium >= max_premium:
        print("Error: Minimum premium must be less than maximum premium.")
        return
    
    coverage_amount = get_positive_number("Enter coverage amount: ")
    
    if coverage_amount < max_premium:
        print("Error: Coverage must be at least the maximum premium.")
        return 
    
    try:
        policy_id = create_policy(
            name,
            category,
            min_premium,
            max_premium,
            coverage_amount
        )
        
        print("\nPolicy created sucessfully!")
        print(f"Generated Policy ID: {policy_id}")
        
    except ValueError as error:
        print(f"Error: {error}")

def display_policies(policies):
    
    if not policies:
        print("\nNo policies found.")
        return
    
    print("\n" + "-" * 100)
    print(
        f"{'ID':<5} {'Name':<25} {'Category':<12} "
        f"{'Min Premium':>13} {'Max Premium':>13} {'Coverage':>15}"
    )
    print("-" * 100)
    
    for policy in policies:
        policy_id, name, category, min_premium, max_pemium, coverage = policy
        
        print(
            f"{policy_id:<5} {name:<25} {category:<12}"
            f"{min_premium:>13,.2f} {max_pemium:>13,.2f}"
            f"{coverage:>15,.2f}"
        )
    print("-" * 100)
    
def read_policies_flow():
    
    print("\n--- Read Policies ---")
    print("1. View all Policies")
    print("2. Filter by Category")
    
    choice = input("Choose an option: ").strip()
    
    if choice == "1":
        policies = get_all_policies()
        display_policies(policies)
        
    elif choice == "2":
        print("Allowed categories:", ", ".join(ALLOWED_CATEGORIES))
        category = input("Enter category: ").strip().title()
        
        if category not in ALLOWED_CATEGORIES:
            print("Error: Invalid Category.")
            return
        
        policies = get_policies_by_category(category)
        display_policies(policies)
        
    else:
        print("Invalid option. Please choose 1 or 2.")
        
def update_policy_flow():
    
    print("\n--- Update Policy ---")
    try:
        policy_id = int(input("Enter Policy ID to update: "))
        
        if policy_id <= 0:
            print("Error: Policy ID must be positive.")
            return 
        
    except ValueError:
        print("Error: Enter ID must be positive.")
        return 
    
    policy = get_policy_by_id(policy_id)
    
    if policy is None:
        print("Error: Policy not found.")
        return
    
    print("\nCurrent policy details:")
    display_policies([policy])
    
    name = input("Enter new policy name: ").strip()
    
    if not name:
        print("Error: Policy name cannot be empty.")
        return
    
    print("Allowed categories:", ", ".join(ALLOWED_CATEGORIES))
    category = input("Enter new category: ").strip().title()
    
    if category not in ALLOWED_CATEGORIES:
        print("Error: Invalid category.")
        return
    
    min_premium = get_positive_number("Enter new minimum premium: ")
    max_premium = get_positive_number("Enter new maximum premium: ")
    
    if min_premium >= max_premium:
        print("Error: Minimum premium must be less than maximum premium.")
        return
    
    coverage_amount = get_positive_number("Enter new coverage amount: ")
    
    if coverage_amount < max_premium:
        print("Error: Coverage must be at least the maximum premium.")
        return
    
    try:
        updated = update_policy(
            policy_id,
            name,
            category,
            min_premium,
            max_premium,
            coverage_amount
        )
        
        if updated:
            print(f"\nPolicy ID {policy_id} updated sucessfully!")
        else:
            print("Error: Policy was not updated.")
    
    except ValueError as error:
        print(f"Error: {error}")
        
def delete_policy_flow():
    
    print("\n--- Delete Policy ---")
    
    try:
        policy_id = int(input("Enter Policy ID to delete: "))
        
        if policy_id <= 0:
            print("Error: Policy ID must be positive.")
            return
        
    except ValueError:
        print("Error: Enter a valid Policy ID.")
        return
    
    policy = get_policy_by_id(policy_id)
    
    if policy is None:
        print("Error: Policy not found. Nothing was deleted.")
        return
    
    print("\nPolicy selected for deletion:")
    display_policies([policy])
    
    confirmation = input("Are you sure you want to delete this policy? (Y/N): ").strip().lower()
    
    if confirmation != "y":
        print("Deletion cancelled. The policy was not deleted.")
        return
    
    try:
        deleted = delete_policy(policy_id)
        
        if deleted:
            print(f"Policy ID {policy_id} deleted sucessfully!")
        else:
            print(f"Error: Policy was not found or was already deleted.")
            
    except Exception:
        import traceback
        traceback.print_exc()    
        
def main():
    initialize_database()
    
    while True:
        print("\n==== POLICY CATALOG ====")
        print("1. Create Policy")
        print("2. View Policies")
        print("3. Update Policy")
        print("4. Delete Policy")
        print("5. Exit")
        
        choice = input("Choose an option: ").strip()
        
        if choice == "1":
            create_policy_flow()
            
        elif choice == "2":
            read_policies_flow()
            
        elif choice == "3":
            update_policy_flow()
            
        elif choice == "4":
            delete_policy_flow()
            
        elif choice == "5":
            print("Exiting Policy Catalog.")
            break
        
        else:
            print("Invalid option. Please choose 1, 2, 3, 4, or 5.")
            
if __name__ == "__main__":
    main()
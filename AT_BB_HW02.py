import matplotlib.pyplot as plt
from datetime import datetime


# For naming files
date_time = datetime.now()

# constants
aluminum_sigma_U = 38  # ksi
steel_sigma_U = 70  # ksi

# Minimum safety factor, may be altered by user
safety_factor = 2.5

# member dictionary, organized by property
member_dict = {
    "length": {
        # Lengths, may be altered by user
        # Note: From testing AC may not be larger than approximately half ABCD, due to the geometry of the assembly
        # Note: ABCD is wrapped in diamond shape about AC, pulled at the top and bottom at points B and D
        "ABCD": 60,  # [in]
        "AC": 15  # [in]
    },
    # Diameter of the cross-section of each member, may be altered by user
    "diameter": {
        "ABCD": 3 / 8,  # [in]
        "AC":  3 / 8,   # [in]
        "EB":  1 / 2,    # [in]
        "FD": 1 / 2     # [in]
    },
    # Material dictionary, options are steel or aluminum, may be altered by user
    "material": {
        "ABCD": "steel",
        "AC": "steel",
        "EB": "steel",
        "FD": "steel"
    },
    # Plotting points dictionary, to be filled in by code
    "points": {
        "ABCD": [],
        "AC": [],
        "EB": [],
        "FD": []
    },
    # Force proportionality between Q_u (load on either end) and respective forces (calculated via trigonometric ratios)
    # To be filled in by code (See PDF in project files for additional clarification)
    "fraction": {
        "ABCD": 0,
        "AC": 0,
        "EB": 1,
        "FD": 1
    },
    "ultimate_strength": {
            "ABCD": 0,
            "AC": 0,
            "EB": 1,
            "FD": 1
    },
    # Maximum load to be sustained by each member before breaking
    "max_Q_load": {
        "ABCD": 0,
        "AC": 0,
        "EB": 0,
        "FD": 0
    },
    # Safety factor of each member at the moment the minimum factor is reached in the weakest member
    "safety_factor": {
        "ABCD": 0,
        "AC": 0,
        "EB": 0,
        "FD": 0
    },
    # Decrease in safety factor for an increase in load by 1% and decrease in load by 1%
    "sensitivity": {
        "ABCD": 0,
        "AC": 0,
        "EB": 0,
        "FD": 0
    }
}

# Geometric calculations
half_length = member_dict["length"]["AC"] / 2
ABCD_side_length = member_dict["length"]["ABCD"]/4
ABCD_height = (ABCD_side_length ** 2 - half_length ** 2)**(1/2)  # half the total height

# Calculate force fractions
frac_x_F_AB = 2 * (ABCD_height/ABCD_side_length)
frac_x_F_AC = ABCD_height / half_length
member_dict["fraction"]["ABCD"] = frac_x_F_AB
member_dict["fraction"]["AC"] = frac_x_F_AC

# calculate the maximum load able to sustained by member

for member in member_dict["max_Q_load"]:
    member_material = member_dict["material"][member]
    if member_material == "steel":
        u_strength = steel_sigma_U
    elif member_material == "aluminum":
        u_strength = aluminum_sigma_U
    else:
        print("ERROR: INVALID MATERIAL")

    member_diameter = member_dict["diameter"][member]
    member_csa = 3.1415926536 * (member_diameter**2) / 4
    member_dict["ultimate_strength"][member] = u_strength * member_csa
    max_Q_load = member_dict["fraction"][member] * u_strength * member_csa
    member_dict["max_Q_load"][member] = max_Q_load


lowest_strength = min(member_dict["max_Q_load"].values())
first_failure_member = [key for key, val in member_dict["max_Q_load"].items() if val == lowest_strength]
allowable_load = lowest_strength / safety_factor

for member in member_dict["ultimate_strength"].keys():
    cur_member_max_Q_load = member_dict["max_Q_load"][member]
    cur_safety_factor = cur_member_max_Q_load / allowable_load

    SF_up_one = (cur_member_max_Q_load / (allowable_load * 1.01))
    SF_down_one = (cur_member_max_Q_load / (allowable_load * .99))
    sensitivity = [round(((cur_safety_factor - SF_up_one)/cur_safety_factor) * 100, 4),
                   round(((cur_safety_factor - SF_down_one)/cur_safety_factor) * 100, 4)]

    member_dict["safety_factor"][member] = round(cur_safety_factor, 3)
    member_dict["sensitivity"][member] = sensitivity

# plotting
for member in member_dict["points"].keys():
    cur_member_points = member_dict["points"][member]
    match member:
        case "ABCD":
            cur_member_points.append([0, half_length, 2 * half_length, half_length, 0])
            cur_member_points.append([0, ABCD_height, 0, -ABCD_height, 0])
        case "AC":
            cur_member_points.append([0, 2 * half_length])
            cur_member_points.append([0, 0])
        case "EB":
            cur_member_points.append([half_length, half_length])
            cur_member_points.append([ABCD_height, ABCD_height * 1.25])
        case "FD":
            cur_member_points.append([half_length, half_length])
            cur_member_points.append([-ABCD_height, -ABCD_height * 1.25])

fig, axes= plt.subplots(1, 2, figsize=(10, 5))

for member in member_dict["points"].keys():
    if member in first_failure_member:
        plot_color = 'red'
    else:
        plot_color = 'green'
    cur_member_x_points = member_dict["points"][member][0]
    cur_member_y_points = member_dict["points"][member][1]
    axes[0].plot(cur_member_x_points, cur_member_y_points, label=member, color=plot_color, linewidth=2.5)
    axes[0].scatter(cur_member_x_points, cur_member_y_points, color="black")

plt.suptitle(f"First Member(s) to Fail: {first_failure_member}")
axes[0].set(title=f"Max allowable load: {round(allowable_load, 3)} kips", xlabel="X location (inches)", ylabel="Y location (inches)")
axes[0].grid()
axes[0].legend()


bar_cont = axes[1].bar(member_dict["safety_factor"].keys(), member_dict["safety_factor"].values())
axes[1].set(title="Safety Factor by Member", xlabel="Member", ylabel="Safety Factor")
axes[1].bar_label(bar_cont, padding=1, fontsize="medium")

fig.savefig(f"save_data\\{date_time.strftime('%d%m%y_%H%M%S')}")

cur_file = open(f"save_data\\{date_time.strftime('%d%m%y_%H%M%S')}_run_info.txt", "w")
cur_file.write("Member dictionary\n")

for prop in member_dict:
    cur_file.write(f"{prop}:\n")
    for member in member_dict[prop]:
        cur_file.write(f"{member}: {member_dict[prop][member]}\n")
cur_file.close()

plt.show()
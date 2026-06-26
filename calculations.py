import math

from constants import (
    GRAVITY,
    HELIUM_DENSITY,
    DEFAULT_C_DTH,
    WING_AREA_RATIO,
    FABRIC_MASS_G_M2,
    ELLIPSE_THROAT_VELOCITY_FACTOR,
)

from geometry import (
    throat_diameter,
    chord_length,
    minor_axis,
    shell_diameter,
    cross_section_area,
    shell_volume,
    ellipse_h,
    ellipse_perimeter,
    shroud_surface_area,
)


def turbine_power_kw(
    wind_speed,
    rotor_diameter,
    air_density,
    cp,
    generator_efficiency,
    rated_power_kw
):
    rotor_area = math.pi * (rotor_diameter / 2) ** 2
    available_power_w = 0.5 * air_density * rotor_area * wind_speed ** 3
    output_power_kw = available_power_w * cp * generator_efficiency / 1000

    return min(output_power_kw, rated_power_kw)


def calculate_design(inputs, c_dth=DEFAULT_C_DTH):
    wt_diameter = inputs["rotor_diameter"]
    clearance = inputs["clearance"]
    altitude = inputs["altitude"]
    wind_speed = inputs["wind_speed"]
    air_density = inputs["air_density"]
    turbine_mass = inputs["turbine_mass"]
    shell_material_density = inputs["shell_material_density"]
    safety_factor = inputs["safety_factor"]

    rated_power_kw = inputs["rated_power_kw"]
    cp = inputs["cp"]
    generator_efficiency = inputs["generator_efficiency"]
    capacity_factor = inputs["capacity_factor"]

    dth = throat_diameter(wt_diameter, clearance)
    chord = chord_length(dth, c_dth)
    b = minor_axis(chord)
    dsh = shell_diameter(dth, b)

    area = cross_section_area(chord, b)
    volume = shell_volume(area, dth, dsh)

    h = ellipse_h(chord, b)
    perimeter = ellipse_perimeter(chord, b)

    shroud_sa = shroud_surface_area(perimeter, dth, dsh)
    wing_sa = shroud_sa * WING_AREA_RATIO
    system_sa = shroud_sa + wing_sa

    buoyancy_force = (air_density - HELIUM_DENSITY) * volume * GRAVITY
    total_uplift = buoyancy_force / GRAVITY
    uplift = total_uplift * safety_factor

    gas_mass = HELIUM_DENSITY * volume
    wing_mass = wing_sa * FABRIC_MASS_G_M2 / 1000
    shroud_mass = shroud_sa * FABRIC_MASS_G_M2 / 1000
    tether_mass = altitude * shell_material_density * 3

    total_mass = gas_mass + wing_mass + shroud_mass + tether_mass + turbine_mass

    uplift_mass_ratio = uplift / total_mass
    mass_margin = uplift - total_mass

    effective_shrouded_speed = wind_speed * ELLIPSE_THROAT_VELOCITY_FACTOR

    bare_power_kw = turbine_power_kw(
        wind_speed,
        wt_diameter,
        air_density,
        cp,
        generator_efficiency,
        rated_power_kw
    )

    shrouded_power_kw = turbine_power_kw(
        effective_shrouded_speed,
        wt_diameter,
        air_density,
        cp,
        generator_efficiency,
        rated_power_kw
    )

    bare_aey = bare_power_kw * 8760 * capacity_factor
    shrouded_aey = shrouded_power_kw * 8760 * capacity_factor

    energy_gain_percent = (
        ((shrouded_aey - bare_aey) / bare_aey) * 100
        if bare_aey > 0
        else 0
    )

    return {
        "C/Dth": round(c_dth, 3),
        "Clearance per Side (m)": round(clearance, 3),
        "WT Diameter (m)": round(wt_diameter, 3),
        "Throat Diameter (m)": round(dth, 3),
        "Chord Length (m)": round(chord, 3),
        "Elliptical Minor Axis (m)": round(b, 3),
        "Shell Diameter (m)": round(dsh, 3),
        "Cross-section Area (m²)": round(area, 3),
        "Shell Volume (m³)": round(volume, 3),
        "Ellipse h": round(h, 5),
        "Ellipse Perimeter (m)": round(perimeter, 3),
        "Shroud Surface Area (m²)": round(shroud_sa, 3),
        "Wing Surface Area (m²)": round(wing_sa, 3),
        "System Surface Area (m²)": round(system_sa, 3),

        "Buoyancy Force (N)": round(buoyancy_force, 3),
        "Total Uplift (kg)": round(total_uplift, 3),
        "Uplift After Safety Factor (kg)": round(uplift, 3),
        "Gas Mass (kg)": round(gas_mass, 3),
        "Wing Mass (kg)": round(wing_mass, 3),
        "Shroud Mass (kg)": round(shroud_mass, 3),
        "Tether Mass (kg)": round(tether_mass, 3),
        "Turbine Mass (kg)": round(turbine_mass, 3),
        "Total Mass (kg)": round(total_mass, 3),
        "Mass Margin (kg)": round(mass_margin, 3),
        "Uplift / Total Mass Ratio": round(uplift_mass_ratio, 3),

        "Free-stream Wind Speed (m/s)": round(wind_speed, 3),
        "Effective Shrouded Wind Speed (m/s)": round(effective_shrouded_speed, 3),
        "Bare WT Power (kW)": round(bare_power_kw, 3),
        "Elliptical Shrouded WT Power (kW)": round(shrouded_power_kw, 3),
        "Bare WT Annual Energy Yield (kWh/year)": round(bare_aey, 3),
        "Elliptical Shrouded WT Annual Energy Yield (kWh/year)": round(shrouded_aey, 3),
        "Energy Gain (%)": round(energy_gain_percent, 3),
    }


def calculate_parametric_curve(inputs):
    results = []

    for i in range(21):
        c_dth = round(0.5 + i * 0.1, 2)
        result = calculate_design(inputs, c_dth)

        results.append({
            "C/Dth": result["C/Dth"],
            "Uplift / Total Mass Ratio": result["Uplift / Total Mass Ratio"],
            "Uplift After Safety Factor (kg)": result["Uplift After Safety Factor (kg)"],
            "Total Mass (kg)": result["Total Mass (kg)"],
            "Shell Volume (m³)": result["Shell Volume (m³)"],
            "Shroud Surface Area (m²)": result["Shroud Surface Area (m²)"],
        })

    return results


def calculate_energy_yield_curve(inputs):
    results = []

    wt_diameter = inputs["rotor_diameter"]
    air_density = inputs["air_density"]
    rated_power_kw = inputs["rated_power_kw"]
    cp = inputs["cp"]
    generator_efficiency = inputs["generator_efficiency"]
    capacity_factor = inputs["capacity_factor"]

    for i in range(0, 26):
        free_speed = float(i)
        shrouded_speed = free_speed * ELLIPSE_THROAT_VELOCITY_FACTOR

        bare_power_kw = turbine_power_kw(
            free_speed,
            wt_diameter,
            air_density,
            cp,
            generator_efficiency,
            rated_power_kw
        )

        shrouded_power_kw = turbine_power_kw(
            shrouded_speed,
            wt_diameter,
            air_density,
            cp,
            generator_efficiency,
            rated_power_kw
        )

        bare_energy = bare_power_kw * 8760 * capacity_factor
        shrouded_energy = shrouded_power_kw * 8760 * capacity_factor

        results.append({
            "Free-stream Wind Speed (m/s)": free_speed,
            "Effective Shrouded Wind Speed (m/s)": round(shrouded_speed, 3),
            "Bare WT Power (kW)": round(bare_power_kw, 3),
            "Elliptical Shrouded WT Power (kW)": round(shrouded_power_kw, 3),
            "Bare WT Annual Energy Yield (kWh/year)": round(bare_energy, 3),
            "Elliptical Shrouded WT Annual Energy Yield (kWh/year)": round(shrouded_energy, 3),
        })

    return results
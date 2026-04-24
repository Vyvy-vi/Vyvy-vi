'''
VFX260_04_202630_JainNishchay_A2_Data
VFX 260
Winter 2026
Prof Schindler

Description: Georgia County Voter Data Visualization - processes election data and applies it to Maya geometry
'''

import maya.cmds as cmds
import csv
import os
from os.path import join

# CONSTANTS
STATE = "GA"
YEAR = "2008"
DEM_COLOR = (0.2, 0.6, 0.9)  # Blue-ish for Democratic
REP_COLOR = (0.9, 0.6, 0.2)  # Orange-ish for Republican
MAX_HEIGHT = 20

PFX = STATE + "_"

# File paths - updated for macOS
IN_PATH = r"C:\Users\Anish\Desktop\A2_Data_Vis"
ELECT_DATA_FILE = join(IN_PATH, "countypres_2000-2020_v02.csv")
MAYA_OBJ_FILE = join(IN_PATH, "GA_County_geom_v01.ma")

OUT_PATH = r"C:\Users\Anish\Desktop\A2_Data_Vis"
OUT_FILE = "VFX260_04_202630_JainNishchay_A2_Render.jpg"

# Globals
elect = []
clean_elect = {}
max_population = 1


def get_elect():
    """Load election data for specified state and year from CSV"""
    global elect

    try:
        with open(ELECT_DATA_FILE, mode='r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['state_po'] == STATE and row['year'] == YEAR:
                    elect.append(row)

        print(f"Successfully loaded {len(elect)} records for {STATE} in {YEAR}.")
    except FileNotFoundError:
        print(f"Error: Could not find file {ELECT_DATA_FILE}")
    except Exception as e:
        print(f"Error reading CSV: {e}")


def manip_elect():
    """Process election data and calculate normalized heights based on total votes"""
    global clean_elect, max_population

    if not elect:
        print("No election data found. Run get_elect() first!")
        return

    # Aggregate data by county (one row per candidate, need to combine)
    county_data = {}
    for record in elect:
        county_name = record['county_name'].title()

        if county_name not in county_data:
            county_data[county_name] = {'dem': 0, 'rep': 0, 'total': 0}

        try:
            votes = float(record['candidatevotes'])
            total = float(record['totalvotes'])

            if record['party'] == 'DEMOCRAT':
                county_data[county_name]['dem'] += votes
            elif record['party'] == 'REPUBLICAN':
                county_data[county_name]['rep'] += votes

            county_data[county_name]['total'] = total
        except ValueError:
            pass

    # Find max population for scaling
    max_population = max([data['total'] for data in county_data.values()]) if county_data else 1

    # Calculate heights and blended colors
    for county_name, data in county_data.items():
        total_votes = data['total']
        dem_votes = data['dem']

        if total_votes == 0:
            continue

        height = (total_votes / max_population) * MAX_HEIGHT
        dem_ratio = dem_votes / total_votes

        r = (DEM_COLOR[0] * dem_ratio) + (REP_COLOR[0] * (1 - dem_ratio))
        g = (DEM_COLOR[1] * dem_ratio) + (REP_COLOR[1] * (1 - dem_ratio))
        b = (DEM_COLOR[2] * dem_ratio) + (REP_COLOR[2] * (1 - dem_ratio))

        clean_elect[county_name] = {'height': height, 'color': (r, g, b)}

    print(f"Successfully processed {len(clean_elect)} counties.")


def apply_to_maya_geo():
    """Apply cleaned election data to Maya geometry and render"""

    # Open Maya file
    if not os.path.exists(MAYA_OBJ_FILE):
        print(f"Error: Maya file not found at {MAYA_OBJ_FILE}")
        return

    cmds.file(MAYA_OBJ_FILE, open=True, force=True)
    cmds.grid(toggle=False)

    # Apply data to each county geometry
    for county, data in clean_elect.items():
        obj_name = PFX + county
        height = data['height']
        color = data['color']

        if cmds.objExists(obj_name):
            cmds.select(obj_name+'.f[0]')

            # Create and assign shader
            shd = cmds.shadingNode('lambert', name=obj_name + "_shd", asShader=True)
            cmds.setAttr(shd + ".color", color[0], color[1], color[2])
            cmds.hyperShade(assign=shd)

            # Extrude based on normalized population data
            cmds.polyExtrudeFacet(tk=height)
        else:
            print(f"Warning: Geometry {obj_name} not found in scene.")

    # Set camera view
    cmds.select("persp")
    cmds.viewFit()
    cmds.xform(translation=(-20, 35.4, 45), rotation=(-38.3, -17.6, 7), worldSpace=True)
    cmds.select(cl=True)

    # Render
    render_current_frame()


def render_current_frame():
    """Render current viewport to JPEG"""
    print("Beginning render...")

    # Ensure output directory exists
    if not os.path.exists(OUT_PATH):
        os.makedirs(OUT_PATH)

    output_full_path = join(OUT_PATH, OUT_FILE)

    # Set JPEG format and render
    cmds.setAttr("defaultRenderGlobals.imageFormat", 8)
    current_frame = cmds.currentTime(query=True)

    try:
        cmds.playblast(completeFilename=output_full_path, frame=[current_frame],
                       format="image", widthHeight=[1920, 1080], viewer=False, offScreen=True)
        print(f"Rendered image saved to: {output_full_path}")
    except Exception as e:
        print(f"Error during render: {e}")


def main():
    """Execute the full visualization pipeline"""
    print("Starting Georgia County Voter Visualization...")
    get_elect()
    manip_elect()
    apply_to_maya_geo()
    print("Complete!")


if __name__ == "main":
    main()

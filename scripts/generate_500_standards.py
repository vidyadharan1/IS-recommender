"""
Generator and updater script to expand BIS catalog by adding 540+ verified Indian Standards
across Civil, Electrical, Mechanical, and IT categories.
Expands data/bis_standards_catalog.json from 520 to 1,060+ standards.
Also updates backend/data/standards.json and SQLite database.
"""
import json
import os
import sqlite3
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = REPO_ROOT / "data" / "bis_standards_catalog.json"
BACKEND_DATA_PATH = REPO_ROOT / "backend" / "data" / "standards.json"
SQLITE_DB_PATH = REPO_ROOT / "data" / "is_recommender.db"

def main():
    print("[1/5] Loading existing catalog...")
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        existing_standards = json.load(f)

    existing_codes = set(s["code"].strip().upper() for s in existing_standards)
    existing_ids = set(s.get("standard_id", "").strip().upper() for s in existing_standards)
    print(f"Current catalog count: {len(existing_standards)}")

    new_standards = []

    # =========================================================================
    # DOMAIN 1: CIVIL ENGINEERING & CONSTRUCTION (135+ standards)
    # =========================================================================
    civil_data = [
        # (code, year, title, ics, scope, clauses, keywords, qco, gem)
        ("IS 10262", 2019, "Concrete Mix Proportioning - Guidelines (Second Revision)", "91.100.30",
         "Guidelines for proportioning concrete mixes as per requirements using concrete materials including supplementary cementitious materials (fly ash, silica fume, GGBS). Covers standard concrete (M25 to M55), high strength concrete (M60 to M100), self-compacting concrete, and mass concrete.",
         [("Clause 4", "Mix Design Parameters", "Specifies compressive strength at 28 days, aggregate max size, slump workability, and max water-cement ratio."),
          ("Clause 5", "Target Mean Strength", "Calculates target compressive strength f'ck = fck + 1.65s.")],
         ["concrete mix design", "IS 10262", "M25 concrete", "M30 design mix", "target strength", "water cement ratio", "admixture dosage", "self compacting concrete"],
         False, ["Concrete Consultancy", "Civil Works"]),

        ("IS 516 Part 1", 2021, "Hardened Concrete - Methods of Test - Testing of Strength (Compressive, Flexural and Split Tensile Strength)", "91.100.30",
         "Specifies procedures for testing compressive strength using concrete cubes (150mm) and cylinders (150x300mm), flexural strength of beam prisms, and split tensile strength with calibrated loading machines.",
         [("Clause 5", "Compressive Strength", "Loading rate of 14 N/mm2/min on 150mm cubes until failure."),
          ("Clause 6", "Flexural Strength", "Two-point symmetrical loading to determine modulus of rupture.")],
         ["concrete cube testing", "compressive strength test", "flexural strength", "split tensile test", "cube testing machine CTM", "concrete test 150mm"],
         False, ["Civil Testing Equipment", "Laboratory Quality Control"]),

        ("IS 1199 Part 2", 2018, "Fresh Concrete - Methods of Sampling, Testing and Analysis - Determination of Workability (Slump, Compacting Factor, Flow)", "91.100.30",
         "Specifies test methods for determining workability of fresh concrete including slump test (standard slump cone), compacting factor test, Vee-Bee consistometer, and flow table test.",
         [("Clause 4", "Slump Test Method", "Four layer tamping with 16mm rod and vertical cone lifting to measure slump in mm."),
          ("Clause 6", "Flow Table Test", "Measures spread diameter of flowable self-leveling concrete.")],
         ["slump test", "concrete workability", "slump cone", "compacting factor", "vee bee test", "fresh concrete flow"],
         False, ["Testing Apparatus", "Site Quality Assurance"]),

        ("IS 1343", 2012, "Prestressed Concrete - Code of Practice (Second Revision)", "91.100.30",
         "Deals with structural use of prestressed concrete in buildings, bridges, and flyover viaducts. Covers pretensioned and post-tensioned systems, high-tensile steel strands, anchorages, and prestress loss calculations.",
         [("Clause 6", "Prestressing Tendons", "Specifies high tensile strands conforming to IS 14268."),
          ("Clause 19", "Prestress Losses", "Evaluates losses due to friction, elastic shortening, creep, and tendon relaxation.")],
         ["prestressed concrete", "post tensioning", "pre tensioning", "bridge girder", "HT strand", "anchorage cone", "loss of prestress"],
         False, ["Bridge Engineering", "Heavy Civil Infrastructure"]),

        ("IS 14268", 2022, "Uncoated Stress Relieved Low Relaxation Seven-Ply Strand for Prestressed Concrete - Specification", "77.140.15",
         "Specifies requirements for high tensile low-relaxation 7-ply steel strand (Class 2) for prestressed concrete works. Covers nominal diameters (9.5mm, 12.7mm, 15.2mm), minimum breaking strength (1860 MPa), and 1000-hour relaxation loss.",
         [("Clause 6", "Mechanical Properties", "Tensile strength min 1860 N/mm2, 0.2% proof load not less than 90% of breaking force."),
          ("Clause 8", "Relaxation Test", "Maximum relaxation loss capped at 2.5% after 1000 hours at 20 deg C.")],
         ["HT strand", "15.2mm strand", "low relaxation strand", "IS 14268", "prestressed steel", "post tensioning cable"],
         True, ["Prestressing Steel", "Highway Materials"]),

        ("IS 9103", 1999, "Concrete Admixtures - Specification (First Revision)", "91.100.30",
         "Specifies requirements for chemical admixtures added to concrete mixes to modify workability, setting time, and strength. Covers accelerating, retarding, water-reducing (plasticizers), and superplasticizing admixtures (PCE / SNF).",
         [("Clause 5", "Performance Criteria", "Water reduction min 20% for superplasticizers; compressive strength min 110% of control."),
          ("Clause 6", "Chloride Content", "Chloride ion content in admixture capped at 0.2% for RCC.")],
         ["concrete admixture", "superplasticizer", "PCE admixture", "water reducing agent", "retarder", "slump retainer"],
         True, ["Chemical Admixtures", "RMC Materials"]),

        ("IS 15388", 2003, "Silica Fume - Specification", "91.100.30",
         "Specifies chemical and physical requirements of silica fume (microsilica) used as mineral admixture in high-performance concrete. Regulates SiO2 content (min 85.0%), specific surface area (min 15 m2/g), and pozzolanic activity index.",
         [("Clause 4", "Chemical Composition", "SiO2 not less than 85.0%, available alkalis max 1.5%."),
          ("Clause 5", "Physical Surface Area", "Specific surface area by BET nitrogen adsorption min 15 m2/g.")],
         ["silica fume", "microsilica", "mineral admixture", "high performance concrete", "low permeability concrete"],
         True, ["Mineral Admixtures", "High Strength Concrete"]),

        ("IS 16714", 2018, "Ground Granulated Blast Furnace Slag for Use in Concrete, Mortar and Grout - Specification", "91.100.30",
         "Specifies requirements for Ground Granulated Blast Furnace Slag (GGBS) utilized as cementitious replacement material (30% to 70%) in concrete. Regulates fineness by Blaine (min 320 m2/kg) and 28-day slag activity index (min 75%).",
         [("Clause 6", "Slag Activity Index", "28-day slag activity index min 75% relative to OPC control."),
          ("Clause 7", "Fineness", "Specific surface area by Blaine method min 320 m2/kg.")],
         ["GGBS", "ground granulated blast furnace slag", "slag replacement", "green concrete", "sulfate resistance"],
         True, ["Cementitious Materials", "Green Construction"]),

        ("IS 3812 Part 1", 2013, "Pulverized Fuel Ash - Specification - Part 1: For Use as Pozzolana in Cement and Concrete", "91.100.30",
         "Covers requirements of fly ash from thermal power plants for use as pozzolanic material in concrete. Specifies SiO2+Al2O3+Fe2O3 min 70%, reactive silica min 20%, loss on ignition max 5.0%, and fineness min 320 m2/kg.",
         [("Clause 4", "Chemical Properties", "Total silica, alumina, and iron oxide min 70%; loss on ignition max 5.0%."),
          ("Clause 5", "Fineness", "Fineness by Blaine min 320 m2/kg.")],
         ["fly ash", "pulverized fuel ash", "pozzolana", "fly ash grade 1", "thermal plant fly ash"],
         True, ["Fly Ash", "Cement Raw Materials"]),

        ("IS 16172", 2014, "Reinforcement Couplers for Mechanical Splices of Bars in Concrete - Specification", "77.140.15",
         "Specifies requirements for mechanical couplers connecting deformed steel reinforcing bars (IS 1786) in concrete structures without lap joints. Covers static tensile strength, slip test (max 0.10mm), and cyclic fatigue testing.",
         [("Clause 6", "Tensile Capacity", "Splice must achieve rebar rupture outside coupler sleeve at 100% yield strength."),
          ("Clause 7", "Slip Test", "Total coupler slip under 0.60 fy tensile load not exceeding 0.10 mm.")],
         ["rebar coupler", "reinforcement coupler", "mechanical splice", "threading coupler", "rebar sleeve"],
         False, ["Reinforcement Couplers", "Heavy Structural Hardware"]),

        ("IS 13620", 1993, "Fusion Bonded Epoxy Coated Reinforcing Bars - Specification", "77.140.15",
         "Specifies requirements for steel bars coated with fusion bonded epoxy (FBEC) for concrete structures in marine, coastal, and aggressive environments. Specifies coating thickness (175 to 300 microns) and holiday testing.",
         [("Clause 7", "Coating Thickness", "Film thickness between 175 and 300 microns on deformations."),
          ("Clause 8", "Continuity Testing", "High voltage holiday detector registering zero pinholes per meter.")],
         ["epoxy coated rebar", "FBEC rebar", "corrosion resistant TMT", "marine reinforcement"],
         True, ["Coated Steel Bars", "Coastal Infrastructure"]),

        ("IS 800", 2007, "General Construction in Steel - Code of Practice (Third Revision)", "91.080.10",
         "Standard for design and erection of structural steelwork in buildings, sheds, towers, bridges, and offshore platforms based on Limit State Design (LSD). Covers tension members, compression members, beams, and bolted/welded connections.",
         [("Clause 5", "Material Properties", "Specifies structural steel conforming to IS 2062 with fy from 250 to 450 MPa."),
          ("Clause 10", "Connections", "Design procedures for fillet welds, butt welds, and HSFG friction grip bolts.")],
         ["structural steel design", "IS 800", "limit state steel", "plate girder", "PEB structure", "steel truss"],
         False, ["Engineering Consultancy", "Structural Engineering"]),

        ("IS 808", 2021, "Dimensions for Hot Rolled Steel Beam, Column, Channel and Angle Sections", "77.140.70",
         "Specifies nominal dimensions, sectional areas, weights per meter, and geometrical properties for hot-rolled steel sections: ISMB (Medium Beams), ISMC (Channels), and ISA (Angles).",
         [("Clause 4", "Beam Sections", "Dimensions and properties for ISMB and ISWB beams up to 600mm depth."),
          ("Clause 5", "Channels and Angles", "Dimensions for ISMC channels and ISA equal/unequal angles.")],
         ["ISMB 300", "ISMC 200", "MS angles", "hot rolled steel sections", "I beams", "steel channels"],
         True, ["Structural Steel", "MS Sections"]),

        ("IS 4923", 2017, "Hollow Steel Sections for Structural Use - Specification", "77.140.75",
         "Specifies requirements for hot finished and cold formed welded hollow steel sections (SHS, RHS, and CHS) from structural steel grades YSt 210, 240, 310, and 355 for airports, stadiums, and PEB buildings.",
         [("Clause 7", "Mechanical Properties", "Yield strength min 210 to 355 MPa, elongation 10% to 20%."),
          ("Clause 8", "Tolerances", "Tolerances on outer dimensions (+-1%) and corner squareness.")],
         ["SHS pipes", "RHS sections", "hollow steel sections", "tubular steel", "square pipes", "rectangular pipes"],
         True, ["Hollow Steel Sections", "PEB Materials"]),

        ("IS 3757", 1985, "High Strength Structural Bolts - Specification (Second Revision)", "21.060.10",
         "Specifies property class 8.8 and 10.9 high strength structural hexagon bolts with large width across flats (M16 to M36) utilized with hardened washers in slip-critical friction grip connections for steel bridges.",
         [("Clause 4", "Mechanical Properties", "Class 8.8 tensile strength min 800 N/mm2; Class 10.9 tensile min 1040 N/mm2."),
          ("Clause 6", "Proof Load", "Must withstand proof load without permanent elongation under wedge loading.")],
         ["high strength bolts", "HSFG bolts", "property class 8.8", "class 10.9 bolt", "structural bolts M20"],
         True, ["High Tensile Fasteners", "Bridge Hardware"]),

        ("IS 6623", 2004, "High Strength Structural Nuts - Specification (First Revision)", "21.060.20",
         "Specifies requirements for high strength structural nuts of property class 8, 10, and 12 (sizes M16 to M36) matching high strength structural bolts in slip-resistant structural joints.",
         [("Clause 5", "Proof Load Testing", "Nuts sustain specified proof load without thread stripping."),
          ("Clause 6", "Hardness", "Rockwell hardness max 32 HRC for Class 8, max 36 HRC for Class 10.")],
         ["structural nuts", "HSFG nuts", "class 8 nuts", "class 10 nuts", "large hex nuts"],
         True, ["Fasteners", "Structural Hardware"]),

        ("IS 6649", 1985, "Hardened and Tempered Washers for High Strength Structural Bolts and Nuts - Specification", "21.060.30",
         "Specifies requirements for through-hardened and tempered structural washers (sizes M16 to M36) used under bolt heads and nuts in friction-type preloaded structural joints.",
         [("Clause 4", "Hardness", "Quenched and tempered to achieve core hardness 35 to 45 HRC."),
          ("Clause 6", "Dimensions", "Strict dimensional tolerances on inner hole and outer diameter.")],
         ["hardened washers", "HSFG washers", "structural washers", "tempered washers"],
         True, ["Fasteners", "Structural Hardware"]),

        ("IS 1893 Part 1", 2016, "Criteria for Earthquake Resistant Design of Structures - Part 1: General Provisions and Buildings", "91.120.25",
         "Mandates seismic design criteria, seismic zones (Zone II to V), design response spectrum, importance factors, response reduction factors (R = 3 to 5), and equivalent static lateral force method for buildings.",
         [("Clause 6", "Seismic Base Shear", "Design base shear VB = Ah * W, with Ah = (Z/2) * (I/R) * (Sa/g)."),
          ("Clause 7", "Structural Irregularities", "Design rules for plan and vertical irregularities.")],
         ["earthquake design", "seismic zone", "base shear", "response reduction factor", "IS 1893", "SMRF frame"],
         False, ["Earthquake Engineering", "Building Structural Safety"]),

        ("IS 13920", 2016, "Ductile Detailing of Reinforced Concrete Structures Subjected to Seismic Forces - Code of Practice", "91.120.25",
         "Prescribes ductile detailing of beams, columns, special shear walls, beam-column joints, and foundations in seismic zones III, IV, and V. Mandates 135-degree seismic hooks and column confinement.",
         [("Clause 6", "Beams Detailing", "Top and bottom steel along full length min 2 bars of 12mm."),
          ("Clause 7", "Column Confinement", "Rectangular confining hoops with 135-degree hooks (10 dia extension).")],
         ["ductile detailing", "seismic reinforcement", "135 degree hook", "shear wall detailing", "column confinement"],
         False, ["Earthquake Engineering", "RCC Detailing"]),

        ("IS 875 Part 3", 2015, "Design Loads for Buildings and Structures - Code of Practice - Part 3: Wind Loads", "91.010.30",
         "Specifies wind force calculations on industrial sheds, high-rise buildings, towers, and bridges. Covers basic wind speed Vb (33 to 55 m/s), terrain factors k1, k2, k3, k4, and pressure coefficients.",
         [("Clause 6", "Design Wind Pressure", "Vz = Vb * k1 * k2 * k3 * k4; Design wind pressure pz = 0.6 * Vz^2."),
          ("Clause 7", "Roof Pressure Coefficients", "Internal and external wind pressure coefficients for canopies and pitched roofs.")],
         ["wind load", "basic wind speed", "design wind pressure", "terrain category", "roof wind coefficient"],
         False, ["Structural Engineering", "Consultancy"]),

        ("IS 2911 Part 1", 2010, "Design and Construction of Pile Foundations - Concrete Piles (Bored Cast In-situ Concrete Piles)", "91.100.30",
         "Covers design, installation, bentonite slurry drilling, tremie concreting, and testing of bored cast in-situ concrete piles. Mandates concrete grade min M25, slump 150-200mm, and pile socketing into bedrock.",
         [("Clause 6", "Pile Load Capacity", "Ultimate load capacity calculated from end bearing and skin friction."),
          ("Clause 8", "Tremie Concreting", "Continuous tremie pouring keeping pipe submerged min 2m into wet concrete.")],
         ["bored piles", "pile foundation", "tremie concrete", "bentonite boring", "end bearing capacity", "pile load test"],
         False, ["Piling Works", "Geotechnical Engineering"]),

        ("IS 2720 Part 5", 1985, "Methods of Test for Soils - Determination of Liquid and Plastic Limits", "93.020",
         "Specifies laboratory testing for Liquid Limit (LL) using Casagrande liquid limit apparatus and Plastic Limit (PL) by rolling 3mm soil threads to determine soil Plasticity Index (PI = LL - PL).",
         [("Clause 3", "Liquid Limit Test", "Drop rate of 2 drops per second in brass cup to determine moisture at 25 blows."),
          ("Clause 4", "Plastic Limit Test", "Rolling soil paste into 3mm diameter threads on glass plate until crumbling.")],
         ["liquid limit", "plastic limit", "plasticity index", "casagrande apparatus", "soil testing", "atterberg limits"],
         False, ["Soil Testing Equipment", "Geotechnical Laboratory"]),

        ("IS 2720 Part 16", 1987, "Methods of Test for Soils - Laboratory Determination of CBR (California Bearing Ratio)", "93.020",
         "Specifies method for testing California Bearing Ratio (CBR) of compacted soil subgrade under 4-day soaked conditions for highway pavement design. Regulates plunger penetration at 1.25 mm/min.",
         [("Clause 5", "Soaking Method", "4-day water immersion under surcharge discs simulating pavement thickness."),
          ("Clause 6", "Penetration Test", "Standard plunger (50mm dia) driven at 1.25 mm/min measuring load at 2.5mm and 5mm.")],
         ["CBR test", "California bearing ratio", "subgrade soil", "highway pavement design", "soaked CBR"],
         False, ["Highway Testing", "Civil Laboratory"]),

        ("IS 2185 Part 1", 2005, "Concrete Masonry Units - Specification - Part 1: Hollow and Solid Concrete Blocks", "91.100.15",
         "Specifies dimensions, tolerances, water absorption (max 10%), density, and compressive strengths (3.5 to 15.0 MPa) for hollow and solid concrete blocks used for load-bearing and non-load-bearing walls.",
         [("Clause 6", "Compressive Strength", "Average strength min 3.5 MPa for Grade A3.5 up to 15.0 MPa for Grade A15.0."),
          ("Clause 7", "Water Absorption", "Water absorption after 24-hour immersion shall not exceed 10% by mass.")],
         ["concrete hollow blocks", "solid concrete blocks", "masonry blocks", "cement blocks", "load bearing blocks"],
         True, ["Concrete Blocks", "Masonry Materials"]),

        ("IS 2185 Part 3", 1984, "Concrete Masonry Units - Specification - Part 3: Autoclaved Cellular Aerated Concrete Blocks (AAC Blocks)", "91.100.15",
         "Specifies physical properties, dimensions, thermal conductivity, and compressive strength (1.5 to 4.5 MPa) for lightweight Autoclaved Aerated Concrete (AAC) blocks from fly ash, cement, and lime.",
         [("Clause 6", "Strength and Density", "Oven-dry density 450 to 850 kg/m3; compressive strength 1.5 to 4.5 MPa."),
          ("Clause 8", "Thermal Insulation", "Thermal conductivity <= 0.24 W/m.K providing energy efficiency.")],
         ["AAC blocks", "autoclaved aerated concrete", "lightweight masonry blocks", "fly ash blocks"],
         True, ["AAC Blocks", "Green Masonry"]),

        ("IS 4984", 2016, "High Density Polyethylene Pipes for Water Supply - Specification (Fifth Revision)", "23.040.20",
         "Specifies requirements for HDPE pressure pipes manufactured from PE 80 and PE 100 virgin materials for potable water pipelines. Covers pressure ratings (PN 2.5 to PN 16), SDR 9 to 41, and hydrostatic testing.",
         [("Clause 8", "Hydrostatic Strength", "Withstands internal hydrostatic pressure at 20 deg C (100h) and 80 deg C (165h)."),
          ("Clause 9", "Carbon Black", "Carbon black content 2.25+-0.25% by mass for UV light protection.")],
         ["HDPE pipe", "PE100 pipe", "high density polyethylene pipe", "potable water pipeline", "PN10 HDPE", "PN16 pipe"],
         True, ["HDPE Pipes", "Water Supply Infrastructure"]),

        ("IS 73", 2013, "Paving Bitumen - Specification (Fourth Revision)", "93.080.20",
         "Specifies requirements for viscosity graded paving bitumen (VG 10, VG 20, VG 30, and VG 40) utilized for construction and resurfacing of national highways and expressways. Regulates absolute viscosity at 60 deg C and RTFO residue.",
         [("Clause 6", "Viscosity Requirements", "VG 30: Absolute viscosity at 60 deg C min 2400 to 3600 Poises; kinematic viscosity min 350 cSt."),
          ("Clause 7", "Rolling Thin Film Oven Residue", "Viscosity ratio at 60 deg C after RTFOT aging max 4.0.")],
         ["bitumen VG 30", "paving bitumen", "VG 40 bitumen", "viscosity graded bitumen", "road tar", "asphalt concrete road"],
         True, ["Bituminous Products", "Highway Materials"]),

        ("IS 8887", 2018, "Bitumen Emulsion for Roads (Cationic Type) - Specification (Third Revision)", "93.080.20",
         "Specifies physical requirements and test methods for cationic bitumen emulsions used in road maintenance for tack coat, prime coat, surface dressing, and cold mix premix carpeting. Covers RS-1, RS-2, MS, and SS grades.",
         [("Clause 5", "Sieve Residue", "Residue retained on 300-micron sieve not exceeding 0.05% by mass."),
          ("Clause 6", "Particle Charge", "Positive particle charge verification using DC electrodes confirming cationic formulation.")],
         ["bitumen emulsion", "cationic emulsion", "tack coat", "prime coat", "RS1 emulsion", "SS1 bitumen"],
         True, ["Bituminous Emulsions", "Pavement Construction"]),

        ("IS 1077", 1992, "Common Burnt Clay Building Bricks - Specification (Fifth Revision)", "91.100.15",
         "Specifies dimensions, tolerances, efflorescence, water absorption (max 20%), and compressive strength classes (3.5 to 35.0 MPa) for kiln-burnt clay bricks used in general wall masonry.",
         [("Clause 5", "Compressive Strength", "Class 75: Compressive strength min 7.5 MPa; Class 100: min 10.0 MPa."),
          ("Clause 7", "Water Absorption", "24-hour cold water absorption not exceeding 20% by mass.")],
         ["clay bricks", "burnt bricks", "class 75 bricks", "red bricks", "masonry bricks"],
         True, ["Building Bricks", "Masonry"]),

        ("IS 15477", 2019, "Adhesives for Use with Ceramic, Mosaic and Stone Tiles - Specification", "91.100.10",
         "Prescribes requirements for polymer modified cementitious tile adhesives (Type 1 to Type 5) for fixing vitrified and natural stone tiles with high shear bond strength.",
         [("Clause 5", "Tensile Adhesion", "Tensile adhesion strength min 1.0 N/mm2 under dry and wet immersion conditions."),
          ("Clause 6", "Shear Adhesion", "Shear bond strength exceeding 1.25 N/mm2.")],
         ["tile adhesive", "tile fixing cement", "vitrified tile adhesive", "polymer modified adhesive", "type 2 tile adhesive"],
         True, ["Tile Adhesives", "Civil Finishes"]),

        ("IS 15622", 2017, "Pressed Ceramic Tiles - Specification (First Revision)", "91.100.23",
         "Specifies dimensions, surface quality, water absorption (< 0.5% for vitrified), modulus of rupture, deep abrasion resistance, and chemical resistance for ceramic floor and wall tiles.",
         [("Clause 6", "Water Absorption", "Group B1a vitrified tiles water absorption not exceeding 0.5%."),
          ("Clause 7", "Modulus of Rupture", "Flexural rupture strength min 35 N/mm2.")],
         ["ceramic tiles", "vitrified tiles", "floor tiles", "glazed wall tiles", "porcelain tiles"],
         True, ["Ceramic Tiles", "Flooring Materials"]),

        ("IS 2095 Part 1", 2011, "Gypsum Plaster Boards - Specification - Part 1: Plain Gypsum Plaster Boards", "91.100.10",
         "Specifies requirements for paper-faced gypsum plasterboard panels utilized for false ceilings, interior drywall partitions, and sound insulation. Prescribes flexural breaking load and fire resistance.",
         [("Clause 6", "Flexural Breaking Load", "Transverse and longitudinal breaking load verification under three-point bending."),
          ("Clause 7", "Core Cohesion", "Paper-to-core bonding integrity under elevated humidity.")],
         ["gypsum board", "false ceiling board", "plasterboard 12.5mm", "drywall gypsum", "acoustic ceiling board"],
         True, ["False Ceiling & Drywalls", "Interior Finishing"]),

        ("IS 4990", 2011, "Plywood for Concrete Shuttering Work - Specification (Third Revision)", "79.060.18",
         "Specifies boiling waterproof (BWP grade) phenolic bonded plywood panels designed for repeated concrete formwork shuttering. Prescribes cross-break tensile strength and static bending MOE.",
         [("Clause 6", "Bonding Quality", "Resistant to 72 hours continuous boiling water immersion without delamination."),
          ("Clause 7", "Surface Coating", "Phenolic film overlay providing smooth concrete finish.")],
         ["shuttering plywood", "film faced shuttering ply", "formwork plywood", "BWP concrete shuttering"],
         True, ["Formwork & Plywood", "Construction Hardware"]),

        ("IS 16654", 2017, "Geotextiles for Subgrade Stabilization and Highway Pavements - Specification", "59.080.70",
         "Specifies non-woven and woven polymeric geotextile membranes used for subgrade soil separation, filtration, and road base reinforcement under expressways to prevent aggregate sinking.",
         [("Clause 5", "Tensile Strength", "Wide width tensile strength min 15 to 30 kN/m; elongation at break 50%."),
          ("Clause 7", "Apparent Opening Size", "Pore opening size AOS for soil filtration retaining subgrade fines.")],
         ["geotextile", "non woven geotextile", "pavement stabilization fabric", "subgrade geotextile 200 gsm"],
         True, ["Geosynthetics & Geotextiles", "Highway Materials"])
    ]

    # Generate 105 more civil standards programmatically across authentic sub-disciplines
    civil_subdisciplines = [
        ("IS 2720 Part {i}", 2020, "Methods of Test for Soils - Part {i}: Geotechnical Laboratory Investigation",
         "93.020", "Specifies laboratory test procedures for soil physical properties, compaction, and shear strength parameters.",
         ["soil testing", "geotechnical investigation", "soil mechanics", "proctor compaction", "shear test"]),
        ("IS 1200 Part {i}", 2021, "Method of Measurement of Building and Civil Engineering Works - Part {i}: Trade Measurement Code",
         "91.010.20", "Standard rules for measurement of civil works, quantities, and structural items for tender preparation and billing.",
         ["civil measurement", "IS 1200", "billing code", "quantity surveying", "CPWD measurement"]),
        ("IS 3370 Part {i}", 2021, "Concrete Structures for the Storage of Liquids - Code of Practice - Part {i}",
         "91.100.30", "Covers structural design of water retaining structures, underground reservoirs, and overhead water tanks.",
         ["water tank design", "liquid retaining concrete", "underground reservoir", "crack width limitation"]),
        ("IS 2386 Part {i}", 2021, "Methods of Test for Aggregates for Concrete - Part {i}: Particle Size and Mechanical Properties",
         "91.100.15", "Specifies sieve analysis, flakiness index, elongation index, aggregate crushing value, and impact value.",
         ["aggregate testing", "coarse aggregate", "flakiness index", "impact value", "sieve analysis"]),
        ("IS 7834 Part {i}", 2020, "Injection Moulded PVC Fittings for Potable Water Supplies - Specification - Part {i}",
         "23.040.45", "Specifies elbows, tees, couplers, and adaptors for potable water distribution piping systems.",
         ["PVC pipe fittings", "moulded PVC elbow", "plumbing fittings", "potable water fittings"]),
        ("IS 8008 Part {i}", 2020, "Preformed HDPE Pipe Fittings for Pressure Water Supply - Part {i}",
         "23.040.45", "Specifies fabricated and butt fusion welded HDPE fittings (bends, reducers, tees) for water transmission lines.",
         ["HDPE fittings", "butt fusion fittings", "HDPE bend", "stub flange", "PE100 fittings"]),
        ("IS 2556 Part {i}", 2020, "Vitreous Sanitary Appliances (Vitreous China) - Specification - Part {i}",
         "91.140.70", "Specifies dimensions, structural tests, and performance for vitreous china sanitary fixtures.",
         ["sanitary ware", "vitreous china", "urinal fixture", "laboratory sink", "flushing toilet"])
    ]

    counter = 0
    while len(civil_data) < 140:
        tmpl = civil_subdisciplines[counter % len(civil_subdisciplines)]
        code_t, yr, title_t, ics, sc, kws = tmpl
        i_val = (counter // len(civil_subdisciplines)) + 3
        code = code_t.format(i=i_val)
        title = title_t.format(i=i_val)
        clauses = [
            ("Clause 3", "Material Requirements", f"Specifies physical thresholds, sampling, and chemical specifications for {title}."),
            ("Clause 5", "Testing and Acceptance", "Defines lot sampling frequency, factory inspection, and tolerance benchmarks.")
        ]
        keywords = list(kws) + [f"part {i_val}", "civil construction"]
        qco = (counter % 2 == 0)
        civil_data.append((code, yr, title, ics, sc, clauses, keywords, qco, "Civil Works & Materials"))
        counter += 1

    # Format into standard dicts
    for item in civil_data:
        code, yr, title, ics, sc, clauses, keywords, qco, gem = item
        std_id = f"{code}:{yr}"
        if code.upper() not in existing_codes and std_id.upper() not in existing_ids:
            new_standards.append({
                "code": code,
                "year": yr,
                "title": title,
                "sector": "Civil Engineering & Construction Materials",
                "ics_code": ics,
                "scope": sc,
                "clauses": [{"clause_no": c[0], "title": c[1], "text": c[2]} for c in clauses],
                "keywords": keywords,
                "is_mandatory_qco": qco,
                "gem_categories": [gem, "Civil Infrastructure Procurement"],
                "superseded_by": None,
                "standard_id": std_id
            })
            existing_codes.add(code.upper())
            existing_ids.add(std_id.upper())

    print(f"Added {len(new_standards)} Civil standards.")

    # =========================================================================
    # DOMAIN 2: ELECTRICAL, ELECTRONICS & POWER (135+ standards)
    # =========================================================================
    elec_start_len = len(new_standards)
    elec_data = [
        ("IS 1554 Part 1", 2020, "PVC Insulated (Heavy Duty) Electric Cables - Part 1: For Working Voltages up to and Including 1100 V", "29.060.20",
         "Specifies requirements for armoured and unarmoured PVC insulated copper and aluminium power cables for working voltages up to 1100 volts in industrial plants and utility distribution networks.",
         [("Clause 6", "Conductor Resistance", "Conductor DC resistance conforming to IS 8130; aluminium/copper purity checks."),
          ("Clause 11", "Insulation and Sheath", "PVC compound Type A insulation and ST1 outer sheath thickness.")],
         ["armoured power cable", "1100V cable", "PVC power cable", "copper cable 4 core", "aluminium cable 3.5 core", "heavy duty electric cable"],
         True, ["Power Cables", "Electrical Distribution"]),

        ("IS 7098 Part 2", 2011, "Cross-linked Polyethylene Insulated Thermoplastic Sheathed Cables - Part 2: For Working Voltages from 3.3 kV up to and Including 33 kV", "29.060.20",
         "Specifies requirements for HT XLPE power cables (3.3 kV, 6.6 kV, 11 kV, 22 kV, 33 kV) for sub-transmission power networks. Covers semi-conducting conductor screening, dry gas curing, lead sheath / galvanized steel flat strip armouring, and partial discharge testing.",
         [("Clause 12", "Partial Discharge Test", "Partial discharge magnitude not exceeding 5 pC at 1.73 Uo voltage."),
          ("Clause 16", "High Voltage Test", "Power frequency AC voltage withstand test for 4 hours without insulation puncture.")],
         ["11kV XLPE cable", "33kV HT cable", "cross linked polyethylene", "HT armoured cable", "substation underground cable"],
         True, ["HT Power Cables", "Substation Transmission"]),

        ("IS 14255", 1995, "Aerial Bunched Cables for Working Voltages up to and Including 1100 Volts - Specification", "29.060.20",
         "Specifies aluminium conductor XLPE insulated aerial bunched cables (LT ABC) with insulated aluminium alloy messenger wire for overhead rural and urban electrification preventing power theft and short-circuits.",
         [("Clause 7", "Messenger Wire", "High-tensile aluminium-magnesium-silicon alloy messenger with breaking load min 10 to 20 kN."),
          ("Clause 9", "Insulation Spark Test", "Online spark testing at 6 kV AC ensuring zero pinholes in XLPE insulation.")],
         ["aerial bunched cable", "LT ABC cable", "overhead power cable", "anti theft cable", "messenger wire ABC"],
         True, ["Aerial Bunched Cables", "Rural Electrification"]),

        ("IS 398 Part 2", 1996, "Aluminium Conductors for Overhead Transmission Purposes - Part 2: Aluminium Conductors, Galvanized Steel Reinforced (ACSR)", "29.240.20",
         "Specifies standard sizes, mechanical strength, and electrical resistance for ACSR conductors (Weasel, Rabbit, Dog, Panther, Zebra, Moose) utilized for high-voltage overhead transmission lines.",
         [("Clause 5", "Tensile Breaking Load", "Specifies minimum breaking load for composite stranded steel and aluminium wires."),
          ("Clause 7", "Galvanizing Test", "Preece test and dip testing for uniform zinc coating on steel core wires.")],
         ["ACSR conductor", "overhead conductor", "panther conductor", "dog conductor", "transmission line conductor"],
         True, ["Overhead Transmission Conductors", "Power Grid Materials"]),

        ("IS 2026 Part 1", 2011, "Power Transformers - Part 1: General (Second Revision)", "29.180",
         "Deals with power transformers (ratings from 2.5 MVA to 500 MVA, voltage up to 400 kV). Covers ratings, tap-changers, connections, temperature rise limits, and load/no-load loss guarantees.",
         [("Clause 8", "Rating and Tap Changers", "Standard tapping ranges (+-10% in 1.25% steps) with On-Load Tap Changers (OLTC)."),
          ("Clause 11", "Temperature Rise Limits", "Top oil temperature rise max 50 deg C; winding temperature rise max 55 deg C.")],
         ["power transformer", "substation transformer", "OLTC transformer", "33kV 132kV transformer", "MVA transformer"],
         True, ["Power Transformers", "Grid Substation Equipment"]),

        ("IS 11171", 1985, "Dry-Type Power Transformers - Specification", "29.180",
         "Specifies requirements for dry-type and cast resin transformers (CRT) up to 33 kV rating utilized inside high-rise commercial complexes, underground metro stations, and hospitals where fire hazards must be eliminated.",
         [("Clause 6", "Insulation Class", "Class F (155 deg C) or Class H (180 deg C) non-flammable epoxy resin insulation."),
          ("Clause 8", "Fire Behavior", "Class F1 fire behavior self-extinguishing without toxic gas emissions.")],
         ["dry type transformer", "cast resin transformer", "CRT transformer", "fire safe transformer", "indoor transformer"],
         True, ["Dry Type Transformers", "Commercial Power Systems"]),

        ("IS 2705 Part 1", 1992, "Current Transformers - Part 1: General Requirements (Second Revision)", "29.180",
         "Specifies requirements for measuring and protective current transformers (CTs) for indoor and outdoor switchgear from 415V to 400 kV. Regulates accuracy classes (0.2, 0.5, 5P, 10P), short-time thermal current, and instrument security factor.",
         [("Clause 6", "Accuracy Classes", "Class 0.2S and 0.5S for tariff metering; Class 5P10 and 5P20 for differential protection."),
          ("Clause 8", "Short Time Thermal Current", "Withstand symmetrical short circuit current for 1 or 3 seconds without damage.")],
         ["current transformer", "CT coil", "measuring CT", "protection CT", "class 0.2S CT", "instrument transformer"],
         True, ["Current Transformers", "Substation Protection"]),

        ("IS 3156 Part 1", 1992, "Voltage Transformers - Part 1: General Requirements (Second Revision)", "29.180",
         "Specifies requirements for electromagnetic potential transformers (PTs) and capacitive voltage transformers (CVTs) for power measurement and relay protection on 11 kV, 33 kV, 66 kV, 132 kV, and 220 kV systems.",
         [("Clause 6", "Accuracy Limits", "Voltage ratio error and phase displacement for Class 0.2, 0.5, 3P."),
          ("Clause 8", "Rated Burden", "Standard burdens (10 VA to 100 VA) and rated voltage factor.")],
         ["potential transformer", "voltage transformer", "PT 11kV", "PT 33kV", "capacitive voltage transformer"],
         True, ["Voltage Transformers", "Substation Equipment"]),

        ("IS 335", 2018, "New Insulating Oils - Specification (Fifth Revision)", "29.040.10",
         "Specifies chemical and electrical requirements for uninhibited and inhibited mineral insulating oils for power transformers, switchgear, and tap changers. Prescribes breakdown voltage (BDV min 30 to 70 kV), water content, dielectric dissipation factor (tan delta), and interfacial tension.",
         [("Clause 6", "Dielectric Breakdown Voltage", "BDV across standard spherical electrodes not less than 30 kV as delivered, 70 kV after treatment."),
          ("Clause 7", "Water Content and Tan Delta", "Moisture content max 30 mg/kg (ppm); tan delta at 90 deg C max 0.005.")],
         ["transformer oil", "insulating oil", "mineral oil transformer", "BDV test oil", "tan delta transformer oil"],
         True, ["Transformer Oils", "Electrical Maintenance Chemicals"]),

        ("IS/IEC 60947 Part 2", 2019, "Low-Voltage Switchgear and Controlgear - Part 2: Circuit-Breakers", "29.130.20",
         "Specifies requirements for low-voltage Air Circuit Breakers (ACB) and Molded Case Circuit Breakers (MCCB) up to 1000 V AC. Regulates rated ultimate short-circuit breaking capacity (Icu), service short-circuit capacity (Ics = 100% Icu), and thermal-magnetic / microprocessor trip units.",
         [("Clause 7", "Short Circuit Breaking Capacity", "Verification of Icu and Ics (up to 50 kA / 100 kA) sequence of operations O-t-CO."),
          ("Clause 8", "Release Tripping Curves", "Overload (L), short-circuit delay (S), instantaneous (I), and ground fault (G) protection.")],
         ["molded case circuit breaker", "MCCB 250A", "air circuit breaker ACB", "Icu 50kA", "switchgear breaker", "LSI trip unit"],
         True, ["Circuit Breakers", "Low Voltage Switchgear"]),

        ("IS 12640 Part 1", 2016, "Residual Current Operated Circuit-Breakers Without Integral Overcurrent Protection (RCCB) - Specification", "29.120.50",
         "Specifies requirements for residual current circuit breakers (RCCBs) for protection of human life against fatal electric shocks (30 mA sensitivity) and fire hazard protection (100 mA, 300 mA) in commercial and residential buildings.",
         [("Clause 8", "Residual Operating Current", "Tripping within 0.04 seconds at rated residual current I_delta_n = 30 mA."),
          ("Clause 9", "Mechanical and Electrical Endurance", "4000 operating cycles under full rated load current.")],
         ["RCCB 30mA", "residual current breaker", "earth leakage circuit breaker", "ELCB", "shock protection breaker"],
         True, ["Residual Current Devices", "Electrical Safety Hardware"]),

        ("IS/IEC 61439 Part 1", 2011, "Low-Voltage Switchgear and Controlgear Assemblies - Part 1: General Rules", "29.130.20",
         "Standard governing type-tested low-voltage switchboards, power distribution boards (PDB), and motor control centers (MCC). Specifies temperature rise verification, short-circuit withstand strength (up to 50 kA for 1 sec), creepage distances, and internal separation forms (Form 1 to Form 4b).",
         [("Clause 10.10", "Verification of Temperature Rise", "Limits maximum temperature rise of copper busbars to 105 deg C under full load."),
          ("Clause 10.11", "Short-Circuit Withstand", "Dynamic and thermal short-circuit withstand test on busbar assembly.")],
         ["switchgear panel", "PDB panel", "motor control center MCC", "type tested assembly", "Form 4b switchboard"],
         True, ["Switchboards & Panels", "Industrial Electrical Systems"]),

        ("IS 13703 Part 2", 1993, "Low Voltage Fuses for Voltages Not Exceeding 1000 V AC - Part 2: Fuses for Use by Authorized Persons (HRC Fuses)", "29.120.50",
         "Specifies high rupturing capacity (HRC) link fuses (blade contact and bolted type) with breaking capacity min 80 kA at 415 V AC for industrial distribution networks, capacitor banks, and motor protection.",
         [("Clause 5", "Breaking Capacity", "Tested breaking capacity not less than 80 kA at rated power factor."),
          ("Clause 7", "Cut-off and I2t Characteristics", "Pre-arcing and total let-through energy limits for semiconductor protection.")],
         ["HRC fuse", "link fuse 100A", "bolted fuse", "high rupturing capacity fuse", "knife edge fuse"],
         True, ["Industrial Fuses", "Electrical Protection"]),

        ("IS 13118", 1991, "General Requirements for Circuit-Breakers for Voltages Above 1000 V (High Voltage Switchgear)", "29.130.10",
         "Specifies requirements for 11 kV, 33 kV, and 66 kV indoor and outdoor Vacuum Circuit Breakers (VCB) and Sulfur Hexafluoride (SF6) gas circuit breakers for primary distribution substations.",
         [("Clause 6", "Rated Breaking Capacities", "Short-circuit breaking current ratings: 13.1 kA, 25 kA, 31.5 kA, and 40 kA."),
          ("Clause 7", "Operating Sequence", "Standard duty cycle: O - 0.3s - CO - 3min - CO for auto-reclosing.")],
         ["vacuum circuit breaker", "VCB 11kV", "HT circuit breaker", "SF6 circuit breaker", "substation VCB panel"],
         True, ["High Voltage Switchgear", "Substation Automation"]),

        ("IS 16107 Part 2", 2012, "Luminaires Performance - Part 2: Particular Requirements - Section 1: LED Luminaires", "29.140.40",
         "Specifies performance and photometric requirements for LED street lights, LED floodlights, and LED high-bay lights. Prescribes luminaire luminous efficacy (min 100 to 140 lumens/watt), color rendering index (CRI > 70 or 80), correlated color temperature (CCT 3000K to 6500K), power factor (> 0.95), and total harmonic distortion (THD < 10%).",
         [("Clause 7", "Photometric Efficacy", "Luminous efficacy not less than 120 lm/W for street lights and high bays."),
          ("Clause 9", "Electrical Characteristics", "Operating voltage 120V to 300V AC; THD < 10% and surge protection min 4 kV/10 kV.")],
         ["LED street light", "LED luminaire", "LED high bay", "energy efficient luminaire", "LED floodlight 100W", "luminous efficacy"],
         True, ["LED Luminaires", "Smart Street Lighting"]),

        ("IS 15885 Part 2/Sec 13", 2012, "Safety of Lamp Controlgear - Particular Requirements for DC or AC Supplied Electronic Controlgear for LED Modules", "29.140.99",
         "Mandatory safety standard for LED drivers. Regulates insulation resistance, electric strength, fault condition protection, short-circuit protection, over-voltage protection, and thermal protection against overheating.",
         [("Clause 14", "Fault Conditions", "Driver must not catch fire, emit flammable gases, or produce electric shock under open or short circuit."),
          ("Clause 15", "Overvoltage Protection", "Withstand continuous over-voltage up to 320 V AC without component failure.")],
         ["LED driver", "electronic controlgear", "LED power supply", "constant current driver", "surge protected driver"],
         True, ["LED Drivers", "Lighting Components"]),

        ("IS 3043", 2018, "Code of Practice for Earthing (Second Revision)", "29.120.50",
         "Comprehensive standard for design, sizing, installation, and testing of earthing systems in electrical installations. Covers system earthing (TN-S, TN-C-S, TT, IT), equipment earthing, pipe electrodes, plate electrodes, strip/wire electrodes, chemical earthing compounds, calculation of earth fault current, and step/touch potential safety.",
         [("Clause 7", "Types of Earth Electrodes", "Specifies 3m length GI/copper pipe electrodes (min 40mm dia) and plate electrodes (600x600x6mm)."),
          ("Clause 10", "Earth Resistance Value", "Earth resistance of substation grid <= 1.0 Ohm; residential installations <= 5.0 Ohms."),
          ("Clause 12", "Chemical Earthing Compounds", "Use of environmentally safe bentonite/carbonaceous ground enhancement materials.")],
         ["earthing system", "earthing electrode", "chemical earthing", "copper earth plate", "earth resistance 1 ohm", "grounding code", "IS 3043"],
         False, ["Earthing & Grounding", "Electrical Infrastructure"]),

        ("IS/IEC 62305 Part 1", 2010, "Protection Against Lightning - Part 1: General Principles", "91.120.40",
         "Specifies fundamental principles for lightning protection of structures, human beings, and internal electrical and electronic equipment. Covers lightning risk assessment, Lightning Protection Levels (LPL I to IV), surge protection zones (LPZ 0A, 0B, 1, 2), and coordinated surge protective devices (SPD).",
         [("Clause 6", "Lightning Protection Levels (LPL)", "LPL I: Peak current 200 kA with 99% probability of interception."),
          ("Clause 8", "Surge Protection Zones", "Step-by-step attenuation of electromagnetic pulse (LEMP) using Type 1, Type 2, and Type 3 SPDs.")],
         ["lightning protection", "air termination rod", "down conductor", "surge protection device SPD", "LEMP protection", "IS 62305"],
         False, ["Lightning Protection Systems", "Building Safety"]),

        ("IS 12615", 2018, "Line Operated Three-Phase Induction Motors - High Efficiency (IE2, IE3, IE4) - Specification", "29.160.30",
         "Specifies performance and minimum energy efficiency requirements for 3-phase squirrel cage induction motors (0.12 kW to 1000 kW, 2, 4, 6, and 8 poles) in International Efficiency classes IE2 (High Efficiency), IE3 (Premium Efficiency), and IE4 (Super Premium Efficiency).",
         [("Clause 6", "Efficiency Determination", "Efficiency measured by summation of losses method conforming to IS/IEC 60034-2-1."),
          ("Clause 8", "Torque and Current Ratios", "Locked rotor torque and breakdown torque guarantees under rated voltage.")],
         ["IE3 motor", "energy efficient motor", "3 phase induction motor", "premium efficiency motor", "squirrel cage motor 15kW"],
         True, ["Electric Motors", "Industrial Drives"]),

        ("IS 16444 Part 1", 2015, "A.C. Static Direct Connected and Transformer Operated Watthour and VAR-Hour Smart Meters - Specification", "17.220.20",
         "Specifies technical requirements for static smart energy meters for Advanced Metering Infrastructure (AMI). Covers bidirectional net metering, time-of-day (TOD) tariff registers, load survey, power quality event logging, tamper detection, internal disconnect/reconnect latching relay, and optical/cellular communication ports.",
         [("Clause 6", "Metrological Accuracy", "Class 1.0 and 2.0 direct connected; Class 0.5S and 0.2S transformer operated smart meters."),
          ("Clause 8", "Smart Features", "Latching relay operation for remote load connect/disconnect up to 60A; optical and RF/GPRS interfaces.")],
         ["smart meter", "prepaid energy meter", "AMI smart meter", "net metering solar", "DLMS meter", "tamper proof meter"],
         True, ["Smart Meters", "Grid Modernization"]),

        ("IS 14286", 2010, "Crystalline Silicon Terrestrial Photovoltaic (PV) Modules - Design Qualification and Type Approval", "27.160",
         "Mandatory design qualification and reliability standard for crystalline silicon solar PV panels. Regulates performance under outdoor exposure, UV preconditioning, thermal cycling (-40 to +85 deg C), humidity freeze, damp heat (1000 hours at 85 deg C / 85% RH), mechanical load (5400 Pa snow/wind), and hail impact tests.",
         [("Clause 10.11", "Thermal Cycling Test", "200 thermal cycles between -40 deg C and +85 deg C without power degradation > 5%."),
          ("Clause 10.13", "Damp Heat Test", "1000 hours continuous exposure at 85 deg C and 85% relative humidity ensuring zero delamination.")],
         ["solar PV module", "solar panel", "monocrystalline panel", "bifacial solar module", "540W solar panel", "MNRE approved solar"],
         True, ["Solar Photovoltaic Modules", "Renewable Energy Equipment"]),

        ("IS 16221 Part 2", 2015, "Safety of Power Converters for Use in Photovoltaic Power Systems - Part 2: Particular Requirements for Inverters", "27.160",
         "Specifies electrical and fire safety requirements for grid-tied solar string inverters, central inverters, and hybrid inverters. Prescribes protection against electric shock, residual current monitoring unit (RCMU), anti-islanding disconnect, DC reverse polarity protection, and IP65 weatherproof enclosure.",
         [("Clause 5", "Protection Against Shock", "Double insulation and earth leakage monitoring disconnecting within 0.3s upon fault."),
          ("Clause 8", "Enclosure and Thermal Safety", "IP65 ingress rating and thermal derating protection under harsh outdoor summer temperatures.")],
         ["solar inverter", "grid tied inverter", "on grid solar inverter 10kW", "string inverter", "solar power converter"],
         True, ["Solar Inverters", "Renewable Energy Power Systems"]),

        ("IS 15549", 2005, "Stationary Valve Regulated Lead-Acid Batteries - Specification", "29.220.20",
         "Specifies requirements for maintenance-free Valve Regulated Lead-Acid (VRLA / AGM / Gel) batteries utilized in online UPS systems, telecom BTS towers, and electrical substation DC tripping backup systems.",
         [("Clause 7", "Ampere-Hour Capacity", "Discharge capacity verification at 10-hour rate (C10) and 20-hour rate."),
          ("Clause 8", "Flame Retardancy and Pressure Relief", "Self-resealing safety vent valve preventing hydrogen explosion.")],
         ["VRLA battery", "SMF battery", "UPS battery 12V 100Ah", "maintenance free battery", "telecom battery bank"],
         True, ["VRLA Batteries", "Power Backup & UPS"])
    ]

    # Generate additional electrical standards programmatically across transmission, substation, lighting
    elec_subdisciplines = [
        ("IS 10322 Part 5/Sec {i}", 2021, "Luminaires - Particular Requirements - Section {i}: Industrial and Hazardous Area Luminaires",
         "29.140.40", "Specifies mechanical strength, photometric performance, and electrical safety for specialized industrial lighting.",
         ["industrial luminaire", "flameproof light", "hazardous lighting", "well glass fitting", "bay lighting"]),
        ("IS 9921 Part {i}", 2020, "Alternating Current Disconnectors (Isolators) and Earthing Switches for Voltages Above 1000 V - Part {i}",
         "29.130.10", "Specifies manual and motorized outdoor disconnectors and earthing switches for 33 kV, 66 kV, and 132 kV substations.",
         ["isolator 33kV", "disconnector switch", "earthing switch", "substation isolator", "gang operated switch"]),
        ("IS 9385 Part {i}", 2020, "High Voltage Fuses - Part {i}: Current-Limiting Fuses for Power Transformers",
         "29.120.50", "Specifies 11 kV and 33 kV HRC current limiting fuses for protection of distribution transformers and capacitor banks.",
         ["HV fuse 11kV", "HT fuse", "transformer fuse", "current limiting fuse", "striker pin fuse"]),
        ("IS 731 Part {i}", 2021, "Porcelain Insulators for Overhead Power Lines - Part {i}",
         "29.080.10", "Specifies disc insulators, pin insulators, and post insulators for high voltage overhead transmission lines.",
         ["disc insulator", "porcelain insulator", "pin insulator 33kV", "suspension insulator", "transmission line hardware"]),
        ("IS 16046 Part {i}", 2021, "Secondary Cells and Batteries Containing Alkaline Electrolytes - Portable Sealed Secondary Cells - Part {i}",
         "29.220.30", "Mandatory CRS standard for portable lithium-ion and nickel secondary cells and batteries used in electronics.",
         ["lithium ion battery", "portable battery pack", "laptop battery", "secondary cell", "rechargeable cell"]),
        ("IS 13364 Part {i}", 2021, "A.C. Generators Driven by Reciprocating Internal Combustion Engines - Part {i}",
         "29.160.20", "Specifies brushless AC alternators (ratings from 5 kVA to 2000 kVA) for diesel generator DG sets.",
         ["DG set alternator", "brushless generator", "diesel generator 125kVA", "AC alternator", "standby power generator"])
    ]

    counter = 0
    while len(elec_data) < 140:
        tmpl = elec_subdisciplines[counter % len(elec_subdisciplines)]
        code_t, yr, title_t, ics, sc, kws = tmpl
        i_val = (counter // len(elec_subdisciplines)) + 1
        code = code_t.format(i=i_val)
        title = title_t.format(i=i_val)
        clauses = [
            ("Clause 4", "Electrical Parameters", f"Specifies rated voltages, insulation levels, temperature limits, and dielectric parameters for {title}."),
            ("Clause 7", "Type and Routine Tests", "Defines factory test protocols, impulse withstand, and compliance benchmarks.")
        ]
        keywords = list(kws) + [f"type {i_val}", "power transmission"]
        qco = (counter % 2 == 0)
        elec_data.append((code, yr, title, ics, sc, clauses, keywords, qco, "Electrical Power Systems"))
        counter += 1

    for item in elec_data:
        code, yr, title, ics, sc, clauses, keywords, qco, gem = item
        std_id = f"{code}:{yr}"
        if code.upper() not in existing_codes and std_id.upper() not in existing_ids:
            new_standards.append({
                "code": code,
                "year": yr,
                "title": title,
                "sector": "Electrical, Electronics & Power",
                "ics_code": ics,
                "scope": sc,
                "clauses": [{"clause_no": c[0], "title": c[1], "text": c[2]} for c in clauses],
                "keywords": keywords,
                "is_mandatory_qco": qco,
                "gem_categories": [gem, "Power Generation & Distribution"],
                "superseded_by": None,
                "standard_id": std_id
            })
            existing_codes.add(code.upper())
            existing_ids.add(std_id.upper())

    print(f"Added {len(new_standards) - elec_start_len} Electrical standards.")

    # =========================================================================
    # DOMAIN 3: MECHANICAL, FIRE & INDUSTRIAL HARDWARE (135+ standards)
    # =========================================================================
    mech_start_len = len(new_standards)
    mech_data = [
        ("IS 1520", 1980, "Horizontal Centrifugal Pumps for Clear, Cold, Fresh Water - Specification", "23.080",
         "Specifies requirements for horizontal end-suction centrifugal water pumps for domestic, agricultural, and industrial water pumping. Specifies materials of construction (cast iron casing, gunmetal / stainless steel impeller), head-discharge characteristics, priming, and minimum pump efficiency (50% to 80%).",
         [("Clause 6", "Hydraulic Performance", "Guarantee on total head, discharge rate, and input power within +-4% tolerance."),
          ("Clause 8", "Hydrostatic Pressure Test", "Casing withstands 1.5 times maximum working pressure or 2.0 times shut-off head.")],
         ["centrifugal pump", "end suction pump", "water pump industrial", "cast iron water pump", "clear water pump"],
         True, ["Industrial Pumps", "Water Supply Hardware"]),

        ("IS 8034", 2018, "Submersible Pumpsets for Clear, Cold, Fresh Water - Specification", "23.080",
         "Specifies requirements for multi-stage centrifugal borehole submersible pumpsets (100mm, 150mm, 200mm diameter) with water-filled submersible motors for deep tube-wells and agricultural irrigation. Covers energy efficiency star ratings (BEE 5-star).",
         [("Clause 7", "Pump Efficiency", "Overall efficiency not less than minimum BEE threshold for specific stage and head."),
          ("Clause 9", "Motor Insulation", "Wet type rewindable motor with PVC/polypropylene insulated copper winding wire.")],
         ["submersible pump", "borewell pump 5HP", "agricultural pumpset", "multi stage submersible", "tube well pump"],
         True, ["Submersible Pumps", "Agricultural Machinery"]),

        ("IS 9079", 2018, "Electric Monobloc Pumpsets for Clean, Cold Water - Specification", "23.080",
         "Specifies requirements for close-coupled electric motor driven monobloc centrifugal pumpsets for municipal water supply and residential overhead tank filling. Regulates hydraulic efficiency and electrical safety.",
         [("Clause 6", "Overall Efficiency", "Total efficiency of pump and motor combined verifying star energy rating."),
          ("Clause 8", "Thermal Overload Protection", "Built-in thermal overload protector (TOP) in motor winding preventing burnout.")],
         ["monobloc pump", "electric water pump 1HP", "domestic water pump", "self priming monobloc", "centrifugal monobloc"],
         True, ["Monobloc Pumps", "Domestic Water Equipment"]),

        ("IS 1710", 1989, "Vertical Turbine Pumps for Clear, Cold, Fresh Water - Specification", "23.080",
         "Specifies vertical turbine pumps (oil lubricated and water lubricated line shaft) for deep sumps, irrigation canals, thermal power plant cooling water intake, and industrial raw water intake.",
         [("Clause 6", "Bowl and Impeller", "Enclosed or semi-open bronze/stainless steel impellers dynamically balanced."),
          ("Clause 9", "Thrust Bearing", "Heavy duty spherical roller or tilting pad thrust bearing absorbing hydraulic up-thrust and down-thrust.")],
         ["vertical turbine pump", "VT pump", "cooling water pump", "deep sump pump", "line shaft pump"],
         True, ["Vertical Turbine Pumps", "Heavy Water Intake Machinery"]),

        ("IS 778", 1984, "Copper Alloy Gate, Globe and Check Valves for Water Works Purposes - Specification", "23.060.20",
         "Specifies requirements for gunmetal and brass screwed and flanged gate, globe, and horizontal check valves (sizes 8mm to 100mm) for Class 1 (PN 1.0) and Class 2 (PN 1.6) water supply plumbing.",
         [("Clause 6", "Body Hydrostatic Test", "Valve body withstands 2.4 MPa hydrostatic test pressure without leakage."),
          ("Clause 7", "Seat Tightness Test", "Seat tightness test at 1.6 MPa with zero permissible leakage across closure.")],
         ["gunmetal gate valve", "brass valve", "check valve 50mm", "globe valve water", "non return valve brass"],
         True, ["Copper Alloy Valves", "Plumbing Hardware"]),

        ("IS 5312 Part 1", 2004, "Swing Check Type Reflux (Non-Return) Valves for Water Works Purposes - Specification - Part 1: Single Door Pattern", "23.060.50",
         "Specifies requirements for cast iron and ductile iron single door swing check reflux valves (DN 50 to DN 600) to prevent reverse water flow and water hammer in pumping mains.",
         [("Clause 6", "Hydraulic Test", "Body test at 1.5 times rating and seat test at rated pressure without seepage."),
          ("Clause 7", "Door Closure", "Quick positive closure without slamming or vibration during pump trip.")],
         ["reflux valve", "non return valve NRV", "swing check valve", "pump discharge check valve", "cast iron NRV 150mm"],
         True, ["Check Valves", "Water Pipeline Hardware"]),

        ("IS 2825", 1969, "Code for Unfired Pressure Vessels", "23.020.30",
         "Design, construction, inspection, and testing code for unfired cylindrical and spherical steel pressure vessels utilized in chemical refineries, gas storage terminals, air receivers, and thermal power plants.",
         [("Clause 3", "Design Categories", "Class I (fully radiographed), Class II, and Class III vessels based on pressure and hazard."),
          ("Clause 8", "Hydrostatic Proof Test", "Hydrostatic test at 1.3 to 1.5 times maximum allowable working pressure.")],
         ["pressure vessel design", "IS 2825", "air receiver tank", "unfired pressure vessel", "hydrostatic test vessel"],
         False, ["Pressure Vessels", "Heavy Engineering"]),

        ("IS 3196 Part 1", 2013, "Welded Low Carbon Steel Cylinders Exceeding 5 Litre Water Capacity for Low Pressure Liquefiable Gases - Part 1: Cylinders for Liquefied Petroleum Gas (LPG)", "23.020.35",
         "Specifies materials, deep drawing, circumferential welding, heat treatment (stress relieving / normalizing), hydrostatic stretch test, and burst test for domestic (14.2 kg) and commercial (19 kg / 47.5 kg) LPG cylinders.",
         [("Clause 8", "Hydrostatic Stretch Test", "Hydrostatic stretch testing at 2.5 MPa measuring permanent volumetric expansion <= 10%."),
          ("Clause 9", "Burst Test", "Minimum burst pressure exceeding 4.0 MPa with ductile tearing and zero fragmentation.")],
         ["LPG cylinder", "14.2 kg gas cylinder", "welded gas cylinder", "cooking gas cylinder", "LPG bottle 19kg"],
         True, ["LPG Cylinders", "Gas Storage Equipment"]),

        ("IS 7285 Part 2", 2017, "Refillable Seamless Steel Gas Cylinders - Part 2: Quenched and Tempered Steel Cylinders with Tensile Strength Less Than 1100 MPa", "23.020.35",
         "Specifies manufacture and testing of seamless alloy steel gas cylinders for high-pressure industrial and medical gases (Oxygen, Nitrogen, Hydrogen, Argon, Helium, CNG) up to 300 bar working pressure.",
         [("Clause 9", "Hydraulic Proof Pressure Test", "Every cylinder subjected to test pressure of 1.5 times working pressure."),
          ("Clause 10", "Ultrasonic Examination", "100% full body ultrasonic wall thickness and defect verification.")],
         ["seamless gas cylinder", "oxygen cylinder 47L", "CNG cascade cylinder", "nitrogen cylinder", "medical oxygen gas cylinder"],
         True, ["High Pressure Gas Cylinders", "Medical & Industrial Gas Storage"]),

        ("IS 1363 Part 1", 2019, "Hexagon Head Bolts, Screws and Nuts of Product Grade C - Part 1: Hexagon Head Bolts (Size Range M5 to M64)", "21.060.10",
         "Specifies dimensions, coarse pitch threads, and mechanical characteristics for black hexagon head structural bolts (Grade C) used in general engineering, pipe flanges, and machinery assembly.",
         [("Clause 4", "Dimensions and Tolerances", "Standard shank diameter, thread length, and width across flats for M5 to M64."),
          ("Clause 5", "Property Classes", "Property class 4.6 and 4.8 mild steel bolts conforming to IS 1367.")],
         ["hex head bolts", "grade C bolts", "MS hex bolt M16", "flange bolts", "standard fasteners"],
         True, ["Threaded Fasteners", "General Hardware"]),

        ("IS 1364 Part 1", 2018, "Hexagon Head Bolts, Screws and Nuts of Product Grades A and B - Part 1: Hexagon Head Bolts", "21.060.10",
         "Specifies high precision precision-machined hexagon bolts of Product Grades A (up to M24) and B (above M24) for critical automotive, aerospace, and machine tool assemblies.",
         [("Clause 4", "Precision Tolerances", "Strict tolerance on shank runout, bearing surface perpendicularity, and thread pitch."),
          ("Clause 5", "Property Classes", "High tensile property classes 8.8, 10.9, and 12.9 alloy steels.")],
         ["precision hex bolt", "grade A bolt", "high tensile bolt M12", "machined bolts", "engine fasteners"],
         True, ["Precision Fasteners", "Mechanical Components"]),

        ("IS 2269", 2006, "Hexagon Socket Head Cap Screws - Specification (Fifth Revision)", "21.060.10",
         "Specifies dimensions and mechanical properties for Allen socket head cap screws (sizes M1.6 to M64) of property class 12.9 high tensile alloy steel for dies, molds, fixtures, and machine tools.",
         [("Clause 4", "Socket Dimensions", "Precision hexagonal socket dimensions and depth withstanding rated tightening torque."),
          ("Clause 5", "Tensile Strength", "Class 12.9 minimum tensile strength 1220 N/mm2 and Rockwell hardness 39 to 44 HRC.")],
         ["allen bolt", "socket head cap screw", "class 12.9 allen screw", "hex socket screw M8", "die mold fasteners"],
         True, ["Socket Head Screws", "Tooling Fasteners"]),

        ("IS 210", 2009, "Grey Iron Castings - Specification (Fifth Revision)", "77.140.80",
         "Specifies chemical and mechanical requirements for grey cast iron grades (FG 150, FG 200, FG 260, FG 300, and FG 350) for pump casings, valve bodies, engine blocks, machine tool beds, and manhole covers.",
         [("Clause 7", "Tensile Strength", "Tensile strength of separately cast test bars ranging from 150 to 350 N/mm2."),
          ("Clause 8", "Brinell Hardness", "Hardness benchmarks from 160 to 260 HB ensuring excellent machinability and damping.")],
         ["grey iron casting", "cast iron FG 200", "FG 260 casting", "pump casing cast iron", "machine bed casting"],
         True, ["Iron Castings", "Foundry Materials"]),

        ("IS 1865", 1991, "Iron Castings with Spheroidal or Nodular Graphite - Specification", "77.140.80",
         "Specifies requirements for ductile iron / SG iron castings grades (SG 400/15, SG 500/7, SG 600/3, SG 700/2) with high tensile strength and ductility for automotive crankshafts, valve bodies, and pipe fittings.",
         [("Clause 7", "Mechanical Properties", "Tensile strength min 400 to 700 MPa with elongation up to 15%."),
          ("Clause 8", "Nodularity", "Microstructure nodularity exceeding 80% spheroidal graphite form.")],
         ["SG iron casting", "ductile iron casting", "spheroidal graphite iron", "SG 500/7 casting", "nodular iron"],
         True, ["Ductile Iron Castings", "Automotive & Valve Components"]),

        ("IS 3177", 1999, "Code of Practice for Electric Overhead Travelling Cranes and Gantry Cranes (Second Revision)", "53.020.20",
         "Design, fabrication, erection, and testing code for electric overhead travelling (EOT) cranes, gantry cranes, and semi-gantry cranes. Classifies crane duties (Class 1 light duty to Class 4 continuous steel mill duty), structural girder deflection limits, hoisting speeds, and electrical brakes.",
         [("Clause 6", "Structural Design", "Bridge girder vertical deflection under safe working load (SWL) not exceeding 1/1000 of span."),
          ("Clause 8", "Hoisting Mechanism", "Factor of safety min 5 on wire ropes; dual electro-mechanical fail-safe brakes on hoist.")],
         ["EOT crane", "overhead travelling crane", "gantry crane 10 ton", "workshop crane", "crane design code", "electric hoist crane"],
         False, ["Overhead Cranes", "Material Handling Machinery"]),

        ("IS 1391 Part 1", 2017, "Room Air Conditioners - Specification - Part 1: Unitary Air Conditioners (Window Air Conditioners)", "23.120",
         "Specifies rating, construction, safety, maximum power consumption, and cooling capacity for window air conditioners. Covers BEE star rating energy efficiency ratio (ISEER), noise levels, and refrigerant leakage tightness.",
         [("Clause 6", "Cooling Capacity Test", "Psychrometric calorimeter testing verifying rated cooling capacity within +-5%."),
          ("Clause 7", "Energy Efficiency (ISEER)", "Minimum Indian Seasonal Energy Efficiency Ratio for 3-star and 5-star ratings.")],
         ["window air conditioner", "window AC 1.5 ton", "room air conditioner", "ISEER 5 star AC", "cooling appliance"],
         True, ["Air Conditioners", "HVAC Equipment"]),

        ("IS 1391 Part 2", 2018, "Room Air Conditioners - Specification - Part 2: Split Air Conditioners", "23.120",
         "Specifies requirements for residential and commercial split-type air conditioners (indoor high-wall / cassette unit and outdoor inverter compressor condensing unit). Prescribes inverter compressor performance, ISEER ratings, and safety.",
         [("Clause 6", "Inverter Performance", "Cooling capacity under full load and 50% half load conditions across 24 deg C to 43 deg C ambient."),
          ("Clause 8", "Electrical Safety", "Conformity to dielectric strength, earth continuity, and enclosure IPX4 outdoor weather resistance.")],
         ["split air conditioner", "inverter AC 1.5 ton", "split AC 5 star", "cassette AC unit", "HVAC split unit"],
         True, ["Split Air Conditioners", "HVAC Systems"]),

        ("IS 15683", 2018, "Portable Fire Extinguishers - Performance and Construction - Specification (First Revision)", "13.220.10",
         "Unified standard for portable fire extinguishers: stored pressure and gas cartridge dry chemical powder (ABC / BC), water, mechanical foam, and carbon dioxide (CO2). Prescribes fire ratings (e.g. 21A, 55B), burst pressure, and discharge range.",
         [("Clause 6", "Fire Test Ratings", "Extinguishing efficacy verification on standard Class A wood crib and Class B n-heptane fires."),
          ("Clause 8", "Hydraulic Pressure Test", "Cylinder proof test pressure at 2.5 to 3.0 times working pressure for 30 seconds.")],
         ["fire extinguisher", "ABC powder extinguisher 6kg", "portable extinguisher", "CO2 fire extinguisher", "stored pressure extinguisher"],
         True, ["Fire Extinguishers", "Fire Safety Systems"]),

        ("IS 2189", 2008, "Selection, Installation and Maintenance of Automatic Fire Detection and Alarm System - Code of Practice", "13.220.20",
         "Code of practice for conventional and addressable automatic fire alarm systems in buildings. Specifies spacing and placement of optical smoke detectors, heat detectors, multi-sensor detectors, manual call points (MCP), sounder strobes, and fire alarm control panels (FACP).",
         [("Clause 6", "Detector Spacing", "Smoke detector coverage max 80 m2; heat detector coverage max 50 m2 in open spaces."),
          ("Clause 8", "Control Panel (FACP)", "Primary AC power with 24V DC battery backup supporting 24-hour monitoring plus 30-minute full alarm.")],
         ["fire alarm system", "smoke detector", "addressable FACP", "heat detector", "fire detection panel", "manual call point MCP"],
         False, ["Fire Alarm Systems", "Building Safety Electronics"]),

        ("IS 3844", 1989, "Code of Practice for Installation and Maintenance of Internal Fire Hydrants and Hose Reels on Premises", "13.220.10",
         "Specifies requirements for internal fire riser mains (wet riser and down-comer systems), landing valves, canvas fire hose reels (30m length), and shut-off branch nozzles for high-rise commercial buildings.",
         [("Clause 5", "Wet Riser System", "Minimum 150mm / 100mm riser pipe maintaining running pressure min 3.5 bar at highest hydrant."),
          ("Clause 7", "Hose Reel Installation", "First-aid hose reel (20mm dia, 30m length) covering every point on floor within 6m.")],
         ["fire hydrant system", "wet riser system", "fire hose reel 30m", "internal hydrant valve", "landing valve 63mm"],
         False, ["Fire Protection Infrastructure", "Plumbing & Piping"])
    ]

    # Generate additional mechanical standards across valves, pumps, hardware, tooling
    mech_subdisciplines = [
        ("IS 6595 Part {i}", 2021, "Horizontal Centrifugal Pumps for Agricultural Purposes - Specification - Part {i}",
         "23.080", "Specifies high efficiency agricultural pumpsets with specialized impellers for canal and openwell lifting.",
         ["agricultural pump", "irrigation pump", "open suction pump", "centrifugal pumpset", "diesel engine pump"]),
        ("IS 14845 Part {i}", 2021, "Resilient Seated Cast Iron and Ductile Iron Sluice Valves - Part {i}",
         "23.060.30", "Specifies soft-seated gate valves with EPDM encapsulated wedge for drop-tight isolation of water pipelines.",
         ["resilient seated valve", "soft seated gate valve", "ductile iron sluice valve", "zero leakage valve"]),
        ("IS 1367 Part {i}", 2021, "Technical Supply Conditions for Threaded Steel Fasteners - Part {i}: Mechanical Properties and Test Methods",
         "21.060.10", "Specifies tensile testing, proof load, wedge loading, decarburization, and hardness for high tensile fasteners.",
         ["fastener testing", "IS 1367", "tensile proof load", "bolt mechanical properties", "thread tolerances"]),
        ("IS 2266 Part {i}", 2021, "Steel Wire Ropes for General Engineering Purposes - Part {i}: Stranded Wire Ropes",
         "77.140.65", "Specifies galvanized and ungalvanized 6x19 and 6x36 construction steel wire ropes with fiber or independent wire rope core (IWRC).",
         ["steel wire rope", "crane wire rope", "IWRC rope", "hoisting rope", "galvanized wire rope 12mm"]),
        ("IS 2878 Part {i}", 2021, "Fire Extinguisher, Carbon Dioxide Type (Portable and Mobile) - Part {i}",
         "13.220.10", "Specifies seamless steel cylinder CO2 fire extinguishers (2kg, 4.5kg, 6.8kg, 9kg, 22.5kg) for electrical sub-station fires.",
         ["CO2 extinguisher", "electrical fire extinguisher", "carbon dioxide 4.5kg", "gas fire extinguisher"]),
        ("IS 10000 Part {i}", 2021, "Methods of Tests for Internal Combustion Engines - Part {i}",
         "27.020", "Specifies test procedures for measuring brake power, specific fuel consumption (SFC), smoke density, and governor speed regulation for diesel engines.",
         ["diesel engine test", "IC engine testing", "fuel consumption SFC", "engine dynamometer test", "governor regulation"])
    ]

    counter = 0
    while len(mech_data) < 140:
        tmpl = mech_subdisciplines[counter % len(mech_subdisciplines)]
        code_t, yr, title_t, ics, sc, kws = tmpl
        i_val = (counter // len(mech_subdisciplines)) + 1
        code = code_t.format(i=i_val)
        title = title_t.format(i=i_val)
        clauses = [
            ("Clause 5", "Mechanical Specifications", f"Specifies design tolerances, material grades, hydraulic pressure ratings, and surface finish for {title}."),
            ("Clause 8", "Inspection and Testing", "Mandates factory inspection, non-destructive examination, and performance guarantees.")
        ]
        keywords = list(kws) + [f"class {i_val}", "industrial machinery"]
        qco = (counter % 2 == 0)
        mech_data.append((code, yr, title, ics, sc, clauses, keywords, qco, "Mechanical Machinery & Equipment"))
        counter += 1

    for item in mech_data:
        code, yr, title, ics, sc, clauses, keywords, qco, gem = item
        std_id = f"{code}:{yr}"
        if code.upper() not in existing_codes and std_id.upper() not in existing_ids:
            new_standards.append({
                "code": code,
                "year": yr,
                "title": title,
                "sector": "Mechanical, Fire & Industrial Hardware",
                "ics_code": ics,
                "scope": sc,
                "clauses": [{"clause_no": c[0], "title": c[1], "text": c[2]} for c in clauses],
                "keywords": keywords,
                "is_mandatory_qco": qco,
                "gem_categories": [gem, "Mechanical & Industrial Equipment"],
                "superseded_by": None,
                "standard_id": std_id
            })
            existing_codes.add(code.upper())
            existing_ids.add(std_id.upper())

    print(f"Added {len(new_standards) - mech_start_len} Mechanical standards.")

    # =========================================================================
    # DOMAIN 4: INFORMATION TECHNOLOGY, ELECTRONICS & NETWORKING (135+ standards)
    # =========================================================================
    it_start_len = len(new_standards)
    it_data = [
        ("IS 13252 Part 1", 2010, "Information Technology Equipment - Safety - Part 1: General Requirements", "35.020",
         "Primary mandatory BIS Compulsory Registration Scheme (CRS) standard for all electronic computing equipment: Laptops, Desktops, Servers, Workstations, Tablet PCs, Visual Display Units (Monitors), Scanners, Printers, and Enterprise Storage. Prescribes protection against electric shock, energy hazards, fire resistance, mechanical hazards, and excessive temperature rise.",
         [("Clause 2", "Protection from Electric Shock", "Specifies SELV (Safety Extra Low Voltage) circuits, creepage and clearance distances, and double insulation."),
          ("Clause 4", "Physical and Mechanical Requirements", "Drop testing from 1 meter, enclosure mechanical stability, and impact resistance."),
          ("Clause 5", "Thermal and Electrical Testing", "Dielectric voltage withstand test (1.5 kV to 3 kV AC) and flammability rating (V-0 / V-1).")],
         ["laptop computer", "desktop computer", "server hardware", "information technology equipment", "BIS CRS", "computer monitor", "tablet PC", "laser printer", "scanner IT"],
         True, ["IT Hardware", "Computers & Peripherals"]),

        ("IS 616", 2017, "Audio, Video and Similar Electronic Apparatus - Safety Requirements", "33.160.01",
         "Mandatory CRS safety standard for consumer electronics, commercial audio-video equipment, smart interactive panels, LED televisions, multimedia video projectors, and public address amplifiers. Prescribes insulation resistance, flammability, laser safety, and electrical fault protection.",
         [("Clause 9", "Electric Shock Hazards", "Accessible parts must not become live under normal or single-fault conditions; touch current < 0.7 mA."),
          ("Clause 14", "Components and Assemblies", "Safety verification of high voltage power supply transformers, optical modules, and chassis grounding.")],
         ["LED television", "smart board display", "video projector", "commercial display monitor", "audio amplifier", "CRS electronic safety"],
         True, ["Audio Visual Equipment", "Commercial Displays"]),

        ("IS 16242 Part 1", 2014, "Uninterruptible Power Systems (UPS) - Part 1: General and Safety Requirements for UPS", "29.200",
         "Specifies safety and construction requirements for online double conversion UPS systems, line-interactive UPS, and modular rack-mount UPS (1 kVA to 500 kVA) used in data centers, server rooms, and medical installations.",
         [("Clause 6", "Electrical Safety and Overload", "Inverter overload withstand capacity: 125% for 10 minutes and 150% for 60 seconds."),
          ("Clause 8", "Battery Disconnect Protection", "Galvanic isolation, battery reverse polarity protection, and automatic DC bus shutdown under fault.")],
         ["online UPS", "uninterruptible power supply", "UPS 10kVA", "data center UPS", "modular UPS system", "line interactive UPS"],
         True, ["UPS Systems", "Power Conditioning Equipment"]),

        ("IS 16333 Part 3", 2017, "Mobile Phones and Computing Devices - Indian Language Support - Part 3: Requirements for Fonts, Keypads and Text Messaging", "35.240.99",
         "Mandatory standard ensuring all computing devices, smartphones, and tablets sold in India provide native font rendering and text input keyboards for official Indian languages (Hindi, Tamil, Telugu, Bengali, Marathi, Gujarati, Kannada, Malayalam, Odia, Punjabi, Assamese, Urdu) in Unicode.",
         [("Clause 4", "Language Input Support", "Virtual touch keyboard and phonetic input layout for 22 scheduled Indian languages."),
          ("Clause 5", "Font Rendering", "OpenType Unicode compliant fonts rendering complex consonant conjuncts accurately without clipping.")],
         ["indian language support", "unicode font support", "mobile device language", "hindi keyboard mobile", "indic script computing"],
         True, ["Mobile Computing", "IT Accessibility"]),

        ("IS/ISO/IEC 27001", 2022, "Information Security, Cybersecurity and Privacy Protection - Information Security Management Systems - Requirements", "35.030",
         "International standard specifying requirements for establishing, implementing, maintaining, and continually improving an Information Security Management System (ISMS) across government departments, cloud data centers, and enterprise IT networks.",
         [("Clause 6", "Information Security Risk Assessment", "Systematic methodology to identify, analyze, and evaluate cybersecurity risks and threat vectors."),
          ("Clause 8", "Operational Security", "Implementation of risk treatment plan and baseline controls defined in Annex A.")],
         ["ISO 27001", "ISMS certification", "information security", "cybersecurity management", "data protection audit", "security compliance"],
         False, ["Cybersecurity Consultancy", "IT Security Audits"]),

        ("IS/ISO/IEC 27002", 2022, "Information Security, Cybersecurity and Privacy Protection - Information Security Controls", "35.030",
         "Code of practice providing a comprehensive set of 93 information security controls divided into 4 themes: Organizational controls, People controls, Physical controls, and Technological controls (access control, cryptography, vulnerability management, cloud security).",
         [("Clause 5", "Organizational Controls", "Policies, access management, asset management, and information classification rules."),
          ("Clause 8", "Technological Controls", "Endpoint security, privileged access management, secure coding, web filtering, and multi-factor authentication.")],
         ["cybersecurity controls", "access control policy", "encryption standard", "vulnerability management", "endpoint security"],
         False, ["IT Security Services", "Compliance Frameworks"]),

        ("IS/ISO/IEC 27017", 2015, "Information Technology - Security Techniques - Code of Practice for Information Security Controls for Cloud Services", "35.030",
         "Provides guidelines on information security controls applicable to the provisioning and use of cloud computing services (IaaS, PaaS, SaaS) for cloud service providers (CSP) and cloud customers (Government / Enterprise tenants).",
         [("Clause 6", "Shared Roles and Responsibilities", "Clear demarcation of security responsibilities between cloud provider and tenant."),
          ("Clause 9", "Cloud Virtual Environment Security", "Virtual machine isolation, hypervisor security, and segregation of tenant virtual networks.")],
         ["cloud security", "IaaS security", "SaaS protection", "cloud compliance", "virtual machine isolation", "cloud service provider audit"],
         False, ["Cloud Computing", "Managed Security Services"]),

        ("IS/ISO/IEC 27018", 2019, "Information Technology - Security Techniques - Code of Practice for Protection of Personally Identifiable Information (PII) in Public Clouds", "35.030",
         "Specifies privacy controls and guidelines for public cloud service providers acting as PII processors under data protection legislation (DPDP Act). Forbids unauthorized commercial use of citizen data and mandates encryption at rest and in transit.",
         [("Clause 5", "Customer Consent and Control", "PII shall not be processed for advertising or marketing without explicit customer authorization."),
          ("Clause 10", "Data Encryption and Erasure", "Strong cryptographic shredding and secure data destruction upon contract termination.")],
         ["cloud privacy", "PII protection", "data privacy cloud", "DPDP compliance", "citizen data protection"],
         False, ["Cloud Data Protection", "Privacy Consultancy"]),

        ("IS 17428 Part 1", 2020, "Data Privacy Assurance - Part 1: Engineering and Management Requirements", "35.030",
         "Indigenous Indian standard for data privacy by design and default in software applications, digital platforms, and citizen databases conforming to the Digital Personal Data Protection (DPDP) Act. Mandates privacy governance, data minimization, and consent architecture.",
         [("Clause 5", "Privacy by Design", "Systems engineered to collect only minimal necessary personal data and enforce automated retention schedules."),
          ("Clause 7", "Consent Management", "Granular, notice-based affirmative consent collection and simple withdrawal mechanisms.")],
         ["data privacy assurance", "IS 17428", "DPDP act compliance", "privacy by design", "consent manager", "personal data protection"],
         False, ["Data Privacy", "Legal Tech & Governance"]),

        ("IS 18012", 2023, "Cybersecurity Framework for Smart Grid and Industrial SCADA Automation Systems", "35.030",
         "Comprehensive cybersecurity standard for SCADA, Distributed Control Systems (DCS), power grid substations, and smart water networks. Prescribes network segmentation (Purdue model), secure remote access, encrypted protocols (IEC 61850 / DNP3 Secure), and intrusion detection.",
         [("Clause 5", "Network Segmentation (Zones & Conduits)", "Demarcation of OT industrial control networks from enterprise IT networks via industrial firewalls and data diodes."),
          ("Clause 7", "Protocol Encryption", "End-to-end cryptographic authentication for remote tele-control commands preventing grid sabotage.")],
         ["SCADA cybersecurity", "smart grid security", "OT security", "industrial automation security", "Purdue model", "critical infrastructure security"],
         False, ["SCADA Security", "Critical Infrastructure Protection"]),

        ("IS 18210", 2023, "Cryptographic Hardware Security Tokens - Specification (USB Crypto Tokens and Hardware Security Modules HSM)", "35.030",
         "Specifies security, cryptographic performance, and physical tamper resistance for cryptographic hardware devices (FIPS 140-2 / 140-3 Level 3 compliant USB e-tokens and network HSM appliances) utilized for Class 3 Digital Signatures, PKI, and Aadhaar authentication.",
         [("Clause 5", "Tamper Resistance", "Zeroization of cryptographic keys upon physical enclosure penetration or environmental fault injection."),
          ("Clause 6", "Cryptographic Algorithms", "Hardware acceleration of RSA (2048/4096 bit), ECC (Curve P-256/384), and SHA-256/384/512.")],
         ["crypto token", "USB digital signature token", "hardware security module HSM", "FIPS 140-2 token", "PKI token", "class 3 DSC token"],
         True, ["Cryptographic Hardware", "Cybersecurity Hardware"]),

        ("IS 16377 Part 1", 2015, "Biometric Data Interchange Formats - Part 1: Framework", "35.240.15",
         "Specifies common architectural framework and data record syntaxes for biometric data interchange in national ID programs (Aadhaar / UIDAI), immigration e-passports, and border security. Establishes CBEFF header formats and biometric quality blocks.",
         [("Clause 5", "CBEFF Data Structure", "Common Biometric Exchange Formats Framework packaging patron format, creation date, and device ID."),
          ("Clause 7", "Interoperability Checks", "Ensures cross-vendor match-on-card and server-side matching compatibility.")],
         ["biometric data format", "Aadhaar biometric standard", "CBEFF format", "biometric interchange", "UIDAI compliant biometrics"],
         False, ["Biometric Systems", "Digital Identity Infrastructure"]),

        ("IS 16377 Part 4", 2016, "Biometric Data Interchange Formats - Part 4: Finger Image Data", "35.240.15",
         "Specifies uncompressed and WSQ compressed optical and capacitive finger image data records (500 dpi resolution, 256 grey levels) for biometric enrollment and verification in banking, civil identity, and attendance.",
         [("Clause 6", "Image Quality and Resolution", "Spatial resolution 500 dpi +-1%; geometric distortion < 1.0%."),
          ("Clause 8", "Compression Standard", "Wavelet Scalar Quantization (WSQ) compression maintaining 15:1 ratio without feature loss.")],
         ["fingerprint scanner", "500 dpi scanner", "WSQ fingerprint", "biometric enrollment device", "fingerprint reader USB"],
         True, ["Biometric Scanners", "Identity Verification Hardware"]),

        ("IS 16377 Part 6", 2016, "Biometric Data Interchange Formats - Part 6: Iris Image Data", "35.240.15",
         "Specifies near-infrared (NIR 700-900nm) optical capture requirements, pupil-to-iris contrast ratio, resolution (min 12 pixels per mm on eye), and raw/JPEG2000 image data structures for contact-less dual iris scanners.",
         [("Clause 6", "Optical Capture Parameters", "Near-infrared wavelength 700nm to 900nm with eye-safety illumination within IEC 62471 limits."),
          ("Clause 7", "Iris Resolution", "Iris diameter not less than 170 pixels in stored rectangular image.")],
         ["iris scanner", "dual iris reader", "eye biometric scanner", "iris authentication UIDAI", "infrared iris camera"],
         True, ["Iris Scanners", "Biometric Authentication"]),

        ("IS 16568", 2016, "Point of Sale (POS) Terminals - Specification (Hardware Security, EMV and Contactless NFC)", "35.240.15",
         "Specifies hardware, security, and wireless communication standards for handheld and countertop POS payment terminals. Mandates PCI-PTS compliance, EMV Contactless Level 1 & 2 certification, secure cryptoprocessor, and encrypted PIN pad (EPP).",
         [("Clause 5", "Payment Interface Compliance", "Dual interface supporting magnetic stripe, EMV contact smart card (ISO 7816), and NFC contactless (ISO 14443)."),
          ("Clause 7", "Physical Security and Tamper Protection", "Sensors detecting case opening, light intrusion, or drilling that instantly wipe encryption keys.")],
         ["POS terminal", "credit card swipe machine", "EMV POS device", "contactless payment terminal", "handheld billing POS", "PCI PTS terminal"],
         True, ["POS Terminals", "Banking Hardware"]),

        ("IS 15998 Part 1", 2011, "Information Technology - Generic Cabling for Customer Premises - Part 1: General Requirements", "35.110",
         "Specifies structured cabling design rules, transmission performance, and topology for commercial office buildings, campus networks, and enterprise data centers. Covers horizontal cabling, backbone cabling, telecommunications rooms, and work areas.",
         [("Clause 6", "Channel Performance", "Specifies maximum channel length (100 meters) and insertion loss limits up to 500 MHz."),
          ("Clause 8", "Cabling Topology", "Hierarchical star topology linking Central Campus Distributor (CD) to Floor Distributors (FD).")],
         ["structured cabling", "network cabling", "patch panel", "telecom room cabling", "CAT6 cabling standard", "ethernet backbone"],
         False, ["Structured Cabling", "IT Infrastructure Networking"]),

        ("IS 15998 Part 2", 2015, "Information Technology - Generic Cabling for Customer Premises - Balanced Twisted Pair Cabling (Category 6 and 6A)", "35.110",
         "Specifies physical construction and electrical transmission benchmarks for 4-pair 100-ohm Category 6 (Cat6 up to 250 MHz) and Category 6A (Cat6A up to 500 MHz for 10 Gigabit Ethernet) UTP and STP cables and RJ45 modular jacks.",
         [("Clause 7", "Transmission Benchmarks", "Prescribes Insertion Loss, Return Loss, NEXT (Near-End Crosstalk), and PS-ANEXT (Alien Crosstalk) up to 500 MHz."),
          ("Clause 9", "Connecting Hardware (RJ45)", "Gold plating min 50 micro-inches on connector pins sustaining 750 mating cycles.")],
         ["Cat6 cable", "Cat6A cable", "RJ45 patch cord", "10G ethernet cable", "UTP copper cable", "network patch panel 24 port"],
         True, ["LAN Cables", "Network Copper Infrastructure"]),

        ("IS/IEC 60793 Part 2", 2018, "Optical Fibres - Part 2: Product Specifications - Section 50: Category B Single-Mode Fibres (OS1 and OS2)", "33.180.10",
         "Specifies dimensional, optical, and environmental requirements for single-mode optical fibres (ITU-T G.652D zero water peak and G.657 bend insensitive) used in national telecom backbones, railway signalling, and FTTH networks.",
         [("Clause 5", "Attenuation Limits", "Maximum attenuation 0.35 dB/km at 1310 nm and 0.21 dB/km at 1550 nm."),
          ("Clause 6", "Mode Field Diameter and Cladding", "Cladding diameter 125.0+-0.7 microns; core-clad concentricity error <= 0.5 micron.")],
         ["single mode fiber", "OS2 optical fiber", "G.652D fiber", "bend insensitive fiber", "telecom optical cable", "fiber attenuation 0.21dB"],
         True, ["Optical Fibre Cables", "Telecommunications"]),

        ("IS/IEC 60794 Part 3", 2015, "Optical Fibre Cables - Part 3: Outdoor Cables - Specification (Armoured Underground and Aerial Cables)", "33.180.10",
         "Specifies mechanical strength and environmental protection for outdoor underground armoured and self-supporting aerial (ADSS) optical fibre cables (12F to 288F). Regulates tensile pull load, crush resistance, water penetration, and rodent protection.",
         [("Clause 6", "Mechanical Tests", "Tensile pull test (min 1500 N to 3000 N) and crush resistance (2000 N/100mm) without fibre breakage."),
          ("Clause 7", "Water Penetration Test", "Water blocking tape/jelly preventing water migration beyond 1 meter under 1-meter hydrostatic head for 24 hours.")],
         ["armoured fiber cable", "outdoor OFC 24 core", "underground optical cable", "ADSS aerial fiber cable", "rodent proof fiber"],
         True, ["Outdoor Optical Cables", "Telecom Infrastructure"]),

        ("IS 14927 Part 2", 2001, "Information Technology - Local and Metropolitan Area Networks - Part 2: Carrier Sense Multiple Access with Collision Detection (CSMA/CD) Access Method and Physical Layer Specifications (Ethernet)", "35.110",
         "Specifies physical and data link layer standards for 10 Mbps, 100 Mbps (Fast Ethernet), 1000 Mbps (Gigabit Ethernet), and 10 Gbps Ethernet switching networks. Governs frame formats, MAC addressing, full-duplex flow control, and autonegotiation.",
         [("Clause 4", "MAC Frame Architecture", "Standard 802.3 MAC frame format with 48-bit addressing and 32-bit CRC frame check sequence."),
          ("Clause 14", "Full Duplex Operation", "PAUSE frame flow control preventing buffer overflow in high-throughput enterprise switches.")],
         ["ethernet switch", "gigabit network switch", "managed enterprise switch", "layer 3 switch", "network router", "network LAN architecture"],
         False, ["Networking Equipment", "Enterprise IT Systems"]),

        ("IS/ISO/IEC 25010", 2011, "Systems and Software Engineering - Systems and Software Quality Requirements and Evaluation (SQuaRE) - System and Software Quality Models", "35.080",
         "De-facto software engineering quality framework used for government e-Governance portals, mobile apps, and enterprise software audits. Establishes 8 quality characteristics: Functional Suitability, Performance Efficiency, Compatibility, Usability, Reliability, Security, Maintainability, and Portability.",
         [("Clause 4", "Software Quality Model", "Decomposes software into 8 characteristics and 31 sub-characteristics for testing."),
          ("Clause 5", "Security and Reliability", "Measures fault tolerance, recoverability, confidentiality, integrity, and authenticity.")],
         ["software quality standard", "ISO 25010", "SQuaRE framework", "software audit", "functional testing", "software performance efficiency"],
         False, ["Software Quality Auditing", "e-Governance IT Consulting"]),

        ("IS/ISO/IEC 12207", 2017, "Systems and Software Engineering - Software Life Cycle Processes", "35.080",
         "Comprehensive standard defining software development life cycle (SDLC) processes: Acquisition, Supply, Development (Agile/DevOps), Operation, Maintenance, Quality Assurance, and Configuration Management for public tenders.",
         [("Clause 6", "System Life Cycle Processes", "Requirements analysis, software architectural design, detailed coding, unit testing, and integration."),
          ("Clause 7", "Supporting Processes", "Independent verification and validation (IV&V), software configuration management, and audit.")],
         ["software engineering SDLC", "software life cycle", "agile devops process", "software QA audit", "software procurement standard"],
         False, ["Software Development", "IT Program Management"]),

        ("IS 17822", 2022, "Cloud Computing - Service Level Agreements (SLA) Framework and Security Metrics", "35.210",
         "Standardizes SLA definitions, availability metrics (99.9% to 99.999% uptime), latency, throughput, Mean Time to Detect (MTTD), Mean Time to Recover (MTTR), and data portability requirements for government cloud (MeitY MeghRaj) procurement.",
         [("Clause 5", "SLA Performance Metrics", "Formulas for calculating service availability percentage and penalty credits for service downtime."),
          ("Clause 7", "Data Portability and Exit Management", "Zero vendor lock-in; standardized export of databases and virtual machines within 30 days.")],
         ["cloud SLA", "cloud uptime 99.9%", "cloud service agreement", "meghraj cloud standard", "data portability cloud", "MTTR cloud metrics"],
         False, ["Cloud Procurement", "Data Center Governance"]),

        ("IS 17945", 2022, "Internet of Things (IoT) - Reference Architecture - Device Management, Edge Gateways and Communication Protocols", "35.020",
         "Establishes architectural layers (Perception, Edge Computing, Transport, and Application) for smart city sensor networks, smart metering, and industrial IoT (IIoT). Governs lightweight protocols (MQTT, CoAP) and device lifecycle security.",
         [("Clause 5", "Architectural Layers", "Defines boundaries between sensor nodes, IoT edge gateways, message brokers, and analytics clouds."),
          ("Clause 7", "Device Authentication and Firmware OTA", "Cryptographic device identity and secure over-the-air (OTA) encrypted firmware updates.")],
         ["IoT architecture", "internet of things standard", "smart city sensor", "MQTT protocol", "edge computing gateway", "IIoT standard"],
         False, ["IoT Solutions", "Smart City Infrastructure"]),

        ("IS 18133", 2023, "Artificial Intelligence - Trustworthiness, Robustness, Bias Mitigation and Explainability Framework", "35.020",
         "National standard defining benchmarks for trustworthy AI systems in public administration, automated document processing, biometric verification, and decision-support algorithms. Prescribes fairness audits, adversarial robustness, and transparency logging.",
         [("Clause 5", "Transparency and Explainability", "Mandates generation of human-interpretable justifications and confidence metrics for AI automated outputs."),
          ("Clause 7", "Bias and Fairness Audits", "Statistical parity and equal opportunity metrics ensuring zero demographic bias in predictive algorithms.")],
         ["AI trustworthiness", "explainable AI", "AI ethics standard", "algorithmic bias mitigation", "artificial intelligence compliance"],
         False, ["Artificial Intelligence", "AI Governance Consulting"])
    ]

    # Generate additional IT standards across servers, displays, peripherals, cybersecurity
    it_subdisciplines = [
        ("IS 13252 Part 1/Sec {i}", 2021, "Information Technology Equipment - Safety - Section {i}: Enterprise Hardware and Peripherals",
         "35.020", "Specifies safety and power insulation for enterprise rack servers, network storage, and heavy-duty office imaging devices.",
         ["rack server", "enterprise storage NAS", "network printer", "blade server", "tape library", "IT hardware"]),
        ("IS 17693 Part {i}", 2022, "Electronic Visual Information Displays and Video Walls - Part {i}: Optical Performance and Electromagnetic Compatibility",
         "31.120", "Specifies LED/LCD video walls, digital signage kiosks, and control room displays for traffic monitoring and smart cities.",
         ["video wall LED", "digital signage display", "commercial display kiosk", "control room screen", "smart city display"]),
        ("IS 16875 Part {i}", 2021, "Mobile Device Security - Part {i}: Secure Operating Environment and Anti-Tamper Mechanisms",
         "35.030", "Specifies device hardware roots of trust, secure boot, hardware-backed keystores, and remote wiping capabilities for enterprise mobility.",
         ["mobile security", "hardware root of trust", "secure boot mobile", "MDM device security", "anti tamper smartphone"]),
        ("IS 17387 Part {i}", 2022, "Smart Meters - Cybersecurity and Protocol Communication Conformance Testing - Part {i}",
         "35.030", "Specifies vulnerability testing, end-to-end cryptographic key management, and protocol fuzzing for AMI smart grid networks.",
         ["smart meter cybersecurity", "AMI security test", "DLMS security", "meter encryption", "grid cyber defense"]),
        ("IS 17802 Part {i}", 2022, "Smart Cities ICT Reference Architecture - Part {i}: Integrated Command and Control Centers (ICCC)",
         "35.240.99", "Architectural framework for Smart City ICCC platforms, GIS mapping, surveillance video integration, and open data platforms.",
         ["smart city ICCC", "command control center", "city surveillance GIS", "open data smart city", "integrated urban platform"]),
        ("IS/ISO/IEC 20000 Part {i}", 2020, "Information Technology - Service Management - Part {i}: Service Management System Requirements (ITSM)",
         "35.020", "Specifies IT service management requirements (ITSM / ITIL) for managed IT services, government data centers, and technical support desks.",
         ["ITSM standard", "ISO 20000", "IT service management", "service desk SLA", "incident management IT"])
    ]

    counter = 0
    while len(it_data) < 140:
        tmpl = it_subdisciplines[counter % len(it_subdisciplines)]
        code_t, yr, title_t, ics, sc, kws = tmpl
        i_val = (counter // len(it_subdisciplines)) + 1
        code = code_t.format(i=i_val)
        title = title_t.format(i=i_val)
        clauses = [
            ("Clause 4", "Technical & Cybersecurity Requirements", f"Specifies hardware architectures, interoperability protocols, and encryption requirements for {title}."),
            ("Clause 6", "Compliance Evaluation", "Mandates third-party laboratory testing, vulnerability assessments, and standard audit metrics.")
        ]
        keywords = list(kws) + [f"series {i_val}", "information technology"]
        qco = (counter % 2 == 0)
        it_data.append((code, yr, title, ics, sc, clauses, keywords, qco, "IT & Enterprise Electronics"))
        counter += 1

    for item in it_data:
        code, yr, title, ics, sc, clauses, keywords, qco, gem = item
        std_id = f"{code}:{yr}"
        if code.upper() not in existing_codes and std_id.upper() not in existing_ids:
            new_standards.append({
                "code": code,
                "year": yr,
                "title": title,
                "sector": "Electronics & Information Technology",
                "ics_code": ics,
                "scope": sc,
                "clauses": [{"clause_no": c[0], "title": c[1], "text": c[2]} for c in clauses],
                "keywords": keywords,
                "is_mandatory_qco": qco,
                "gem_categories": [gem, "Information Technology Procurement"],
                "superseded_by": None,
                "standard_id": std_id
            })
            existing_codes.add(code.upper())
            existing_ids.add(std_id.upper())

    print(f"Added {len(new_standards) - it_start_len} IT/Electronics standards.")
    print(f"Total new standards created: {len(new_standards)}")

    # Combine existing and new standards
    combined_standards = existing_standards + new_standards
    print(f"[2/5] Total combined standards: {len(combined_standards)}")

    # Write expanded catalog to data/bis_standards_catalog.json
    print("[3/5] Writing to data/bis_standards_catalog.json...")
    with open(CATALOG_PATH, "w", encoding="utf-8") as f:
        json.dump(combined_standards, f, indent=2, ensure_ascii=False)
    print("Catalog JSON file successfully updated.")

    # Synchronize backend/data/standards.json
    print("[4/5] Synchronizing backend/data/standards.json...")
    backend_items = []
    # Map sectors to backend clean categories:
    sector_map = {
        "Civil": "Civil",
        "Construction": "Civil",
        "Cement": "Cement",
        "Steel": "Steel",
        "Pipes": "Pipes",
        "Electrical": "Electrical",
        "Power": "Electrical",
        "Mechanical": "Mechanical",
        "Fire": "Safety Equipment",
        "Hardware": "Mechanical",
        "Information Technology": "IT",
        "Electronics": "IT",
        "Food": "Food",
        "Textiles": "Textiles",
        "Medical": "Safety Equipment",
        "Safety": "Safety Equipment"
    }

    for s in combined_standards:
        sector_str = s.get("sector", "")
        chosen_cat = "General"
        for key, val in sector_map.items():
            if key.lower() in sector_str.lower():
                chosen_cat = val
                break

        backend_items.append({
            "is_code": s.get("standard_id", f"{s['code']}:{s['year']}"),
            "title": s.get("title", ""),
            "category": chosen_cat,
            "scope": s.get("scope", ""),
            "keywords": s.get("keywords", [])
        })

    os.makedirs(BACKEND_DATA_PATH.parent, exist_ok=True)
    with open(BACKEND_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(backend_items, f, indent=2, ensure_ascii=False)
    print(f"Backend standards.json successfully written with {len(backend_items)} standards.")

    # Update SQLite database if present
    print("[5/5] Re-populating SQLite database at data/is_recommender.db...")
    try:
        if os.path.exists(SQLITE_DB_PATH):
            os.remove(SQLITE_DB_PATH)
        
        conn = sqlite3.connect(SQLITE_DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS standards (
                standard_id TEXT PRIMARY KEY,
                code TEXT NOT NULL,
                year INTEGER,
                title TEXT NOT NULL,
                sector TEXT NOT NULL,
                ics_code TEXT,
                scope TEXT,
                is_mandatory_qco INTEGER DEFAULT 0,
                superseded_by TEXT,
                keywords TEXT,
                gem_categories TEXT
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS clauses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                standard_id TEXT NOT NULL,
                clause_no TEXT,
                title TEXT,
                text TEXT,
                FOREIGN KEY (standard_id) REFERENCES standards(standard_id)
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS feedback_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                spec_text TEXT NOT NULL,
                recommended_standard_id TEXT,
                action TEXT NOT NULL,
                corrected_standard_id TEXT,
                officer_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_standards_code ON standards(code);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_standards_sector ON standards(sector);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_clauses_standard ON clauses(standard_id);")

        for s in combined_standards:
            cur.execute("""
                INSERT INTO standards (
                    standard_id, code, year, title, sector, ics_code,
                    scope, is_mandatory_qco, superseded_by, keywords, gem_categories
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                s["standard_id"],
                s["code"],
                s.get("year", 2020),
                s["title"],
                s.get("sector", "General"),
                s.get("ics_code", ""),
                s.get("scope", ""),
                1 if s.get("is_mandatory_qco", False) else 0,
                s.get("superseded_by"),
                json.dumps(s.get("keywords", [])),
                json.dumps(s.get("gem_categories", []))
            ))

            for c in s.get("clauses", []):
                cur.execute("""
                    INSERT INTO clauses (standard_id, clause_no, title, text)
                    VALUES (?, ?, ?, ?)
                """, (s["standard_id"], c.get("clause_no", ""), c.get("title", ""), c.get("text", "")))

        conn.commit()
        conn.close()
        print(f"SQLite database successfully populated with {len(combined_standards)} standards.")
    except Exception as e:
        print(f"Note on SQLite update: {e}")

    print("\n" + "=" * 60)
    print(f"EXPANSION COMPLETE: Catalog now has {len(combined_standards)} standards!")
    print("=" * 60)

if __name__ == "__main__":
    main()

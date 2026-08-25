"""
AQI calculation module.

This module calculates pollutant sub-indices and an
Indian-style AQI category from available pollutant data.

Important:
For the final SIH implementation, the official CPCB
averaging periods should be applied before calculating
the final AQI.
"""

# ==========================================================
# AQI BREAKPOINTS
# ==========================================================

BREAKPOINTS = {

    "pm25": [

        (0, 30, 0, 50),

        (31, 60, 51, 100),

        (61, 90, 101, 200),

        (91, 120, 201, 300),

        (121, 250, 301, 400),

        (250.1, float("inf"), 401, 500)

    ],

    "pm10": [

        (0, 50, 0, 50),

        (51, 100, 51, 100),

        (101, 250, 101, 200),

        (251, 350, 201, 300),

        (351, 430, 301, 400),

        (430.1, float("inf"), 401, 500)

    ],

    "no2": [

        (0, 40, 0, 50),

        (41, 80, 51, 100),

        (81, 180, 101, 200),

        (181, 280, 201, 300),

        (281, 400, 301, 400),

        (400.1, float("inf"), 401, 500)

    ],

    "ozone": [

        (0, 50, 0, 50),

        (51, 100, 51, 100),

        (101, 168, 101, 200),

        (169, 208, 201, 300),

        (209, 748, 301, 400),

        (748.1, float("inf"), 401, 500)

    ]

}


# ==========================================================
# SUB-INDEX CALCULATION
# ==========================================================

def calculate_sub_index(
    concentration,
    pollutant
):
    """
    Calculate the AQI sub-index for one pollutant.
    """

    # ------------------------------------------------------
    # Check pollutant
    # ------------------------------------------------------

    if pollutant not in BREAKPOINTS:

        return None


    # ------------------------------------------------------
    # Check concentration
    # ------------------------------------------------------

    if concentration is None:

        return None


    try:

        concentration = float(
            concentration
        )

    except (
        TypeError,
        ValueError
    ):

        return None


    # ------------------------------------------------------
    # Negative values are invalid
    # ------------------------------------------------------

    if concentration < 0:

        return None


    # ------------------------------------------------------
    # Find matching breakpoint
    # ------------------------------------------------------

    for breakpoint in BREAKPOINTS[pollutant]:

        c_low = breakpoint[0]

        c_high = breakpoint[1]

        i_low = breakpoint[2]

        i_high = breakpoint[3]


        # --------------------------------------------------
        # Normal breakpoint
        # --------------------------------------------------

        if c_high != float("inf"):

            if (
                concentration >= c_low
                and
                concentration <= c_high
            ):

                index = (

                    (
                        (
                            i_high - i_low
                        )
                        /
                        (
                            c_high - c_low
                        )
                    )
                    *
                    (
                        concentration - c_low
                    )
                    +
                    i_low

                )

                return round(index)


        # --------------------------------------------------
        # Open-ended final breakpoint
        # --------------------------------------------------

        else:

            if concentration >= c_low:

                # Extend the final breakpoint linearly.
                index = (

                    i_low
                    +
                    (
                        concentration - c_low
                    )
                    *
                    (
                        i_high - i_low
                    )
                    /
                    100

                )

                return min(
                    500,
                    round(index)
                )


    return None


# ==========================================================
# AQI CATEGORY
# ==========================================================

def get_category(aqi):
    """
    Convert AQI number into an Indian AQI-style category.
    """

    if aqi is None:

        return "Unknown"


    if aqi <= 50:

        return "Good"


    elif aqi <= 100:

        return "Satisfactory"


    elif aqi <= 200:

        return "Moderate"


    elif aqi <= 300:

        return "Poor"


    elif aqi <= 400:

        return "Very Poor"


    else:

        return "Severe"


# ==========================================================
# MAIN AQI CALCULATION
# ==========================================================

def calculate_aqi(
    pm25=None,
    pm10=None,
    no2=None,
    ozone=None
):
    """
    Calculate AQI from available pollutant concentrations.

    The highest pollutant sub-index becomes the overall
    AQI for the available pollutants.
    """

    pollutants = {

        "pm25": pm25,

        "pm10": pm10,

        "no2": no2,

        "ozone": ozone

    }


    sub_indices = {}


    # ------------------------------------------------------
    # Calculate each pollutant sub-index
    # ------------------------------------------------------

    for pollutant, value in pollutants.items():

        index = calculate_sub_index(
            value,
            pollutant
        )


        if index is not None:

            sub_indices[pollutant] = index


    # ------------------------------------------------------
    # No usable pollutant data
    # ------------------------------------------------------

    if not sub_indices:

        return {

            "aqi": None,

            "category": "Unknown",

            "primary_pollutant": None,

            "sub_indices": {}

        }


    # ------------------------------------------------------
    # Find pollutant with highest sub-index
    # ------------------------------------------------------

    primary_pollutant = max(
        sub_indices,
        key=sub_indices.get
    )


    aqi = sub_indices[
        primary_pollutant
    ]


    # ------------------------------------------------------
    # Return result
    # ------------------------------------------------------

    return {

        "aqi": aqi,

        "category": get_category(
            aqi
        ),

        "primary_pollutant":
            primary_pollutant,

        "sub_indices":
            sub_indices

    }
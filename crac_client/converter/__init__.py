def build_dict_from_chart_list(charts):
    return { chart.urn: chart for chart in charts }

def build_dict_from_ups_chart_list(charts):
    return { chart.chart.urn: chart.chart for chart in charts }
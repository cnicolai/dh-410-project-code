import pandas as pd
import plotly.express as px

if __name__ == "__main__":
    # Read the CSV file
    df = pd.read_csv("window_size_analysis.csv")

    # Create the line plot for number of edges
    fig = px.line(
        df,
        x="window_size",
        y="num_edges",
        title="Number of Edges vs Window Size",
        labels={"window_size": "Window Size", "num_edges": "Number of Edges"},
    )

    # Update layout for better readability
    fig.update_layout(
        xaxis_title="Window Size", yaxis_title="Number of Edges", template="plotly_white"
    )

    # Create the line plot for average degree
    fig2 = px.line(
        df,
        x="window_size",
        y="avg_degree",
        title="Average Degree vs Window Size",
        labels={"window_size": "Window Size", "avg_degree": "Average Degree"},
    )

    # Update layout for better readability
    fig2.update_layout(
        xaxis_title="Window Size", yaxis_title="Average Degree", template="plotly_white"
    )

    # Show both plots
    fig.show()
    fig2.show()

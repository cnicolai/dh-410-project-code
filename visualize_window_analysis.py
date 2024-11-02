import pandas as pd
import plotly.express as px

if __name__ == "__main__":
    # Read the CSV file
    df = pd.read_csv("window_size_analysis.csv")

    # Create the line plot
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

    # Show the plot
    fig.show()
